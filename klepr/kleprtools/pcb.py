import sys
import math
import random
import pcbnew
from klepr.kleprtools import config
from klepr.kleprtools import key

class Klepr():
  """  Main backend class for Klepr 
  """

  def __init__(self, *args, **kwargs):
    """ Constructor """
    self.pcb = pcbnew.GetBoard()  
    self.isNightly = False   # Fallback to KiCAD stable

  ######################################################################
  ######################################################################
  # Start of compatibility layer
  # 
  #   - All PCBnew calls should be processed here, for API compatibility
  #     reasons
  ######################################################################
  ######################################################################

  def checkKicadFileFormatVersion(self):
      """ Checks version of the running instance of PCBNew """

      # Check if the running instance of PCBNew is nightly or stable
      kicadVer = pcbnew.SEXPR_BOARD_FILE_VERSION
      self.isNightly = (kicadVer >= config.KICAD_NIGHTLY_VERSION) and not (kicadVer < config.KICAD_STABLE_VERSION)

  def GetParts(self):
    """ 
    Compatibility layer for returning a list of parts from board

    PCBNew's Python API for calling components is as such:

    GetFootprints() - For KiCAD nightly API
    GetModules() - For KiCAD stable API

    Parameters:

    None    
    """
    if self.isNightly == True:
      return self.pcb.GetFootprints()
    else:
      return self.pcb.GetModules()

  def FindPartByReference(self, reference):
    """ 
    Compatibility layer for finding a part by reference

    PCBNew's Python API for calling components is as such:

    FindFootprintByReference() - For KiCAD nightly API
    FindModuleByReference() - For KiCAD stable API

    Parameters:
        
    reference - (str) 
      The part reference ("K_11", "LED_34", etc.)
    """
    if self.isNightly == True:
      return self.pcb.FindFootprintByReference(reference)
    else:
      return self.pcb.FindModuleByReference(reference)

  def SetPartPosition(self, part, x, y):
    """ 
    Compatibility layer for setting a part's position

    PCBNew's Python API for calling components is as such:

    SetPosition() - For KiCAD nightly API
    SetPosition() - For KiCAD stable API

    Parameters:
        
    part - (pcbnew.FOOTPRINT) 
      Part to be placed

    x - (float) 
      X coordinate of part in millimetres

    y - (float) 
      Y coordinate of part in millimetres
    """
    if self.isNightly == True:
      part.SetPosition(pcbnew.wxPointMM(float(x), float(y)))
    else:
      part.SetPosition(pcbnew.wxPointMM(float(x), float(y)))

  def SetPartOrientation(self, part, angle):
    """ 
    Compatibility layer for rottating a part in degrees

    PCBNew's Python API for calling components is as such:

    SetPosition() - For KiCAD nightly API
    SetPosition() - For KiCAD stable API

    Parameters:
        
    part - (pcbnew.FOOTPRINT) 
      Part to be placed

    x - (float) 
      X coordinate of part in millimetres
    
    y - (float) 
      Y coordinate of part in millimetres
    """
    if self.isNightly == True:
      part.SetOrientation(angle)
    else:
      part.SetOrientation(angle)

  def GetPartReference(self, part):
    """ 
    Compatibility layer for getting a part's reference

    PCBNew's Python API for calling components is as such:

    GetReference() - For KiCAD nightly API
    GetReference() - For KiCAD stable API

    Parameters:

    part  - (pcbnew.FOOTPRINT) 
            
            Part to be placed
    """
    if self.isNightly == True:
      return part.GetReference()
    else:
      return part.GetReference()

  def SaveBoard(self, name):
    """
    Compatibility layer for saving the board to a new file

    PCBNew's Python API for calling components is as such:

    Save() - For KiCAD nightly API
    Save() - For KiCAD stable API

    Parameters

    name - (str)
      The full path and filename of the modified file
    """
    if self.isNightly == True:
      self.pcb.Save(name)
    else:
      self.pcb.Save(name)

  ######################################################################
  ######################################################################
  # End of compatibility layer
  ######################################################################
  ######################################################################

  def convertUnit2MM(self, unit):
    """ Converts unit spacing into millimeter spacing. Used for placing KiCAD components """
    return float(unit * config.UNIT_SPACING_MM)

  def angle2KiCADAngle(self, angle):
    """ Convert degrees to KiCAD angles. Scaling factor was derived from experimentation """
    return float(angle * config.ANGLE_SCALING_FACTOR_DEG)

  def  GetPartsByPrefix(self, prefix):
    """ 
    Returns a list of KiCAD parts with a given prefix 

    Parameters:

    prefix - (str)   
      Prefix to be checked
    """

    prefixedParts = []
    parts = self.GetParts()

    # Look for parts that contain the specified prefix
    for part in parts:
      cmpRefPfx = self.GetPartReference(part)
      cmpRefPfx = cmpRefPfx.split('_')[0]
      refPfx = prefix.split('_')[0]
      
      if (cmpRefPfx == refPfx):
        prefixedParts.append(part) 
  
    return prefixedParts

  def MovePartsToLocation(self,x,y):
    """ 
    Shove KiCAD parts into a specified location 

    Parameters:

    x - (float) 
      The X coordinate in millimeters

    y - (float)     
      The Y coordinate in millimeters
    """
    for part in self.GetParts():
      self.SetPartPosition(part, x, y)

  def PlaceParts(self, layout, prefixTable, outputDir):
    """
    Position components based on layout and prefix, and export modified PCB to
    output directory

    Parameters:

    layout - (key.Keyboard)
      List of Key objects containing XY coordinates AND numerical references

    prefixTable - (key.PrefixTable)
      List of part prefixes 

    outputDir - (str)
      The output directory for resulting PCB
    """

    # Start with all parts out of the way
    self.MovePartsToLocation(config.CORNER_X,config.CORNER_Y)


    ########## Loops version 1

    for entry in prefixTable.table.values():
      parts = self.GetPartsByPrefix(entry.prefix)

      # Map coordinate to part using tuple
      # This is done to avoid indexing errors
      for num, coordinate in enumerate(layout.keys):

        # Snap part to layout coordinate
        cur_x = self.convertUnit2MM(coordinate.abs_x)
        cur_y = self.convertUnit2MM(coordinate.abs_y)
        self.SetPartPosition(parts[num], cur_x, cur_y)

        # Calculate the specified offsets
        off_x = cur_x + float(entry.off_x)
        off_y = cur_y + float(entry.off_y)
        off_x, off_y = key.rotateAroundPoint([off_x, off_y], entry.angle,[cur_x, cur_y])
        off_angle = self.angle2KiCADAngle(float(coordinate.angle) + float(entry.angle))
        
        # Add offsets to current position
        self.SetPartPosition(parts[num], off_x, off_y)
        self.SetPartOrientation(parts[num], off_angle)

#    ########## Loops version 2
#
#    for coordinate in layout.keys:
#      for entry in prefixTable.table.values():
#        
#        # Construct part reference
#        compRef = entry.prefix + str(coordinate.ref)
#
#        # If part reference is not properly delimited, skip
#        # i.e. More than one underscore
#        if not (compRef.count('_') == 1):
#          continue
#
#        print("Searching for component:", compRef)
#        part = self.FindPartByReference(compRef)
#
#        # If part does not exist, skip
#        if part == None:
#          continue
#
#        print("Found component:", compRef, ". Placing...")
#
#        # Snap part to the current key position
#        cur_x = self.convertUnit2MM(coordinate.abs_x)
#        cur_y = self.convertUnit2MM(coordinate.abs_y)
#        self.SetPartPosition(part, cur_x, cur_y)
#
#        # Calculate the specified offsets
#        off_x = cur_x + float(entry.off_x)
#        off_y = cur_y + float(entry.off_y)
#        off_x, off_y = key.rotateAroundPoint([off_x, off_y], coordinate.angle,[cur_x, cur_y])
#        off_angle = self.angle2KiCADAngle(coordinate.angle + entry.angle)
#
#        # Add offsets to current position
#        self.SetPartPosition(part, off_x, off_y)
#        self.SetPartOrientation(part, off_angle)
#
    print("End of component placement. Exporting board to", outputDir)
    self.SaveBoard(outputDir + "/mod_.kicad_pcb")
