import sys
import math
import random
import pcbnew
from klepr.kleprtools import key
from klepr.kleprtools import config

# KiCAD versions; update when necessary
config.isKiCADNightly = False
KICAD_NIGHTLY_VERSION = 2021
KICAD_STABLE_VERSION = 2017

PROG_VERSION_NUMBER = 0.1
UNIT_SPACING_MM = 19.05

# class Reference():
#     """ Information as pertains to each reference object """
# 
#     def __init__(
#             self, 
#             obj_id=math.ceil(random.random()*sys.maxsize),
#             reference="REF_",
#             off_x=0,
#             off_y=0,
#             angle=0
#         ):
#         """ 
#         Parameters:
#         
#         reference   - The prefix of the reference to be tracked
#         off_x       - The additional X unit offset from the module center point
#         off_y       - The additional Y unit offset from the module center point
#         angle       - The additional angular rotation for each prefixed reference
# 
#         """
#         self.id = obj_id
#         self.reference = reference
#         self.off_x = off_x
#         self.off_y = off_y
#         self.angle = angle
# 
# 
# class ReferenceTable():
#     """ Contains a collection of Reference objects """
# 
#     def __init__(self):
#         self.table = {}

def unitSpacing2MM(unit):
    """ Converts unit spacing into millimeter spacing. Used for placing KiCAD components """
    return unit*UNIT_SPACING_MM

def angle2WxAngle(angle):
    """ Convert degrees to KiCAD angles """
    return (angle)*-10.0

class PCBPlacer(pcbnew.BOARD):
    """ Main class for placing PCB components together """

def checkKicadFileFormatVersion(pcb):
    """ Checks for KiCAD file format version """

    # Strip the first five characters out of the file version
    version = str(pcb.GetFileFormatVersionAtLoad())
    version_year = int(version[0:4])
    return version_year

def compareReferences(str1, str2):
    """ Checks contents of both strings when id() returns a different number. 
        Uses the underscore '_' as a delimiter for splitting text values
    """
    delimiter = '_'

    ref1 = str1.split(delimiter)
    ref2 = str2.split(delimiter)
    ref10 = ref1[0]
    ref11 = ref1[1]
    ref20 = ref2[0]
    ref21 = ref2[1]

    # Check if string lengths and references are the same
    if (len(str1) != len(str2)) or (ref10 != ref20) or (ref11 != ref21):
        return False
    return True

def GetNumOfPrefixedParts(prefix):
    """ Returns the number of parts with a given prefix """

    numParts = 0

    # Get the current PCB instance
    pcb = pcbnew.GetBoard()

    ########## Add compatibility layer for differing versions of KiCAD
    if config.isKiCADNightly == True:
        parts = pcb.GetFootprints()
    else:
        parts = pcb.GetModules()

    # Loop through all components for references
    for component in parts:

        cmpRefPfx = component.GetReference()
        cmpRefPfx = cmpRefPfx.split('_')[0]
        refPfx = prefix.split('_')[0]
        ok = (cmpRefPfx == refPfx) 

        if ok:
            numParts += 1

    return numParts

def shovePartsIntoCorner(x,y):
    """ Shove KiCAD parts into a specified location """

    pcb = pcbnew.GetBoard()
    
    ########## Add compatibility layer for differing versions of KiCAD
    if config.isKiCADNightly == True:
        parts = pcb.GetFootprints()
    else:
        parts = pcb.GetModules()

    for component in parts:
        component.SetPosition(pcbnew.wxPointMM(float(x), float(y)))

def placeComponents(layout, references, outputDir):
    """ Position components based of reference configuration and layout. 
    
        TODO: Not make this program run on 0(n^3) complexity. AKA simplify the loops

        :param: The XY coordinate map
        :
    """
    shovePartsIntoCorner(200,200)
    print("Placing components...")

    # Fetch the current instance of the board
    pcb = pcbnew.GetBoard()

    ########## Add compatibility layer for differing versions of KiCAD
    if config.isKiCADNightly == True:
        parts = pcb.GetFootprints()
    else:
        parts = pcb.GetModules()

    print("Opened current instance of PCB...")

    # Iterate through each coordinate
    for coordinate in layout:
        num = key.Key()
        num.Json2Key(coordinate)

        # Iterate through all tracked references
        for reference in references.values():

            cmp_designator = reference.reference + str(num.ref)

            # compareReferences() and loop used since string formatting yields 
            # futile results with pcbnew.FindFootprintByReference(STRING)

            # Loop though all PCB components
            for component in parts:

                cur_designator = component.GetReference()

                # Check if reference is delimited by an underscore exactly once
                if not (cur_designator.count('_') == 1):
                    # print("Component reference not underscore-delimited correctly. Skipping...")
                    continue
                
                # Check if current reference matches constructed reference
                if not compareReferences(cmp_designator, cur_designator):
                    # print("Component reference not matching the current reference. Skipping...")
                    continue

                print("Found match, placing component", cur_designator)

                # Snap to the current X-Y position parsed from the KLE file
                cur_x = unitSpacing2MM(num.abs_x)
                cur_y = unitSpacing2MM(num.abs_y)
                component.SetPosition(pcbnew.wxPointMM(float(cur_x), float(cur_y)))

                # Add the specified offsets (plus rotations)
                off_x = cur_x + float(reference.off_x)
                off_y = cur_y + float(reference.off_y)
                off_x, off_y = key.rotateAroundPoint([off_x, off_y], num.angle,[cur_x, cur_y])
                off_angle = angle2WxAngle(num.angle + reference.angle)

                # Add orientation + offset angle
                component.SetPosition(pcbnew.wxPointMM(float(off_x), float(off_y)))
                component.SetOrientation(off_angle)

    print("End of component placement. Exiting.")
    pcb.Save(str(outputDir) + "/mod_.kicad_pcb")

if __name__ == "__main__":
    pcb = pcbnew.GetBoard()
else:

    # Get current instance of the PCB objects
    pcb = pcbnew.GetBoard()
    
    # Check file version of the PCB
    kicadVer = checkKicadFileFormatVersion(pcb)
    print("KiCAD File Version", kicadVer)
    
    # Determine if we're working with a stable or a nightly version of KiCAD
    # We assume that the file corresponds to the version
    config.isKiCADNightly = (kicadVer >= config.KICAD_NIGHTLY_VERSION) and not (kicadVer < config.KICAD_STABLE_VERSION)
    print("KiCAD Nightly Status", config.isKiCADNightly)