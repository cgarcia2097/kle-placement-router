""" This is a Python implementation of the Keyboard Layout Editor classes """

import json
import math
import sys
import random
from datetime import datetime

def rotateAroundPoint(point, degrees, origin=[0,0]):
  """ Rotate a point [X,Y] around a defined origin [X,Y] """

  dx = point[0] - origin[0]
  dy = point[1] - origin[1]
  cos = math.cos(math.radians(float(degrees)))
  sin = math.sin(math.radians(float(degrees)))
  qx = origin[0] + cos*dx - sin*dy
  qy = origin[1] + cos*dy + sin*dx

  return qx,qy

class Prefix():
  """ Contains additional information about  """

  def __init__(
      self, 
      obj_id=math.ceil(random.random()*sys.maxsize),
      prefix="REF_",
      off_x=0.0,
      off_y=0.0,
      angle=0.0
    ):
    """ 
    Parameters:
    
    prefix - (str)
      The prefix of the reference to be tracked
    off_x - (float)
      The additional X unit offset from the center point of prefixed reference
    off_y - (float)
      The additional Y unit offset from the center point of prefixed reference
    angle - (float) 
      The additional angular rotation for each prefixed reference

    """
    self.id = obj_id
    self.prefix = prefix
    self.off_x = off_x
    self.off_y = off_y
    self.angle = angle

  def Prefix2Json(self):
    """ Export Prefix as JSON """
    return json.dumps(vars(self))
  
  def Json2Prefix(self, json):
    """ Import JSON as a Prefix """

    attribute = json.loads(json)
    self.id = attribute['id']
    self.prefix = attribute['prefix']
    self.off_x = attribute['off_x']
    self.off_y = attribute['off_y']
    self.angle = attribute['angle']


class PrefixTable():
  """ Contains a collection of Prefix objects """

  def __init__(self):
    """
    Constructor 
    
    Parameters:

    table - (dict{int : Prefix})
      A Prefix list uniquely indexed by the Prefix object's id
    """
    self.table = {}

  def exportPrefixTable(self, outputDir):
    """ Export keyboard information as a JSON """
    table = []
    for prefix in self.table:
      table.append(prefix.Prefix2Json)
    
    with open(outputDir + "/refTable.json", "w") as fp:
      json.dump(table, fp)

class Point():
  """ Placeholder for XY coordinates """
  
  def __init__(self, ref=0, x=0, y=0, angle=0):
    self.ref = ref
    self.x = x
    self.y = y
    self.angle = angle

class Key():
  """ Information as pertains to each keyswitch. """

  def __init__(self, * args, **kwargs):
    self.ref = 0

    ########### Absolute coordinates in key units

    self.abs_x = 0.0
    self.abs_y = 0.0
    self.abs_x2 = 0.0
    self.abs_y2 = 0.0

    ########### Keyswitch rotation on the keyboard, in degrees

    self.angle = 0.0
    self.stab_angle = 0.0

    ########### Absolute bounding box for each key

    self.width = 0.0
    self.height = 0.0
    self.width2 = 0.0
    self.height2 = 0.0

    ########### Other keyswitch metadata

    self.switchType = ""
    self.stabilizerType = ""

  def Json2Key(self, jsonStr):
    """ Load from JSON string """
    attribute = json.loads(jsonStr)

    self.ref = attribute['ref']
    self.abs_x = attribute['abs_x']
    self.abs_y = attribute['abs_y']
    self.abs_x2 = attribute['abs_x2']
    self.abs_y2 = attribute['abs_y2']
    self.angle = attribute['angle']
    self.stab_angle = attribute['stab_angle']
    self.width = attribute['width']
    self.height = attribute['height']
    self.width2 = attribute['width2']
    self.height2 = attribute['height2']
    self.switchType = attribute['switchType']
    self.stabilizerType = attribute['stabilizerType']

  def Key2Json(self):
    """ Return JSON-encoded string representation of itself """
    return json.dumps(vars(self))
    
class Keyboard():
  """ Information that pertains to the whole keyboard """

  def __init__(self, name="", author=""):
    """ Constructor for the circuit """

    # For storing Key Objects
    self.keys = []

    # Other metadata
    self.name = name
    self.author = author
    self.date = datetime.now()

  def parseKeyboardInfo(self):
    """ Add additional info """

    print("Parsing the additional layout information")

    for i in self.keys:
      i.switchType = self.args.switch_type
      i.stabilizerType = self.args.stabilizer_type

  def parseLayout(self, layout):
    """ Parse the layout information from KLE layout """
    
    print("Parsing the layout information from KLE layout")

    cur_abs = Point(x=0,y=0)
    cur_rel = Point(x=0,y=0)
    cur_angle = 0
    key_num = 0

    # Extract all rows
    for row in layout:
      if isinstance(row, list):

        # Set default key size
        key_width = 1
        key_height = 1

        # Extract all information from row
        for item in row:

          # Key descriptors show up as dicts, parse accordingly
          if isinstance(item, dict):

            for key, value in item.items():
              if key == "x":
                cur_abs.x += value
              if key == "y":
                cur_abs.y += value
              if key == "w":
                key_width = value
              if key == "h":
                key_height = value
              if key == "r":
                cur_angle = value

              # Edge case, if rx or ry is missing, 
              # Use current coordinates for rotation point
              if key == "rx":
                cur_rel.x = value
                cur_abs.x = value
                cur_abs.y = cur_rel.y

              if key == "ry":
                cur_rel.y = value
                cur_abs.y = value
                cur_abs.x = cur_rel.x

          # Keyboard keys show up as str
          # Create key based on current key descriptor
          elif isinstance(item,str):
            newKey = Key()
            newKey.ref = key_num
            newKey.width = key_width
            newKey.height = key_height
            newKey.angle = cur_angle
            newKey.stab_angle = cur_angle

            # If keyswitch is vertical, turn it
            if key_height > key_width:
              newKey.stab_angle += 90

            # Calculate the X-Y coordinates, and rotate around reference point
            x = cur_abs.x + key_width / 2.0  
            y = cur_abs.y + key_height / 2.0
            newKey.abs_x, newKey.abs_y = rotateAroundPoint([x,y], cur_angle, [cur_rel.x, cur_rel.y])

            # Add to cache and reset for the next key
            self.keys.append(newKey)
            cur_abs.x += key_width
            key_height = 1
            key_width = 1
            key_num += 1
            
        cur_abs.y += 1
        cur_abs.x = cur_rel.x

  def exportCoordinateMap(self, outputDir):
    """ Export Keyboard as a JSON """
    coor_map = []
    for key in self.keys:
      coor_map.append(key.Key2Json())
    
    with open(outputDir + "/coordinateMap.json", "w") as fp:
      json.dump(coor_map, fp)