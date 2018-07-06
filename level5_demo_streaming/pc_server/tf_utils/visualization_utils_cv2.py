# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""A set of functions that are used for visualization.

These functions often receive an image, perform some visualization on the image.
The functions do not return a value, instead they modify the image itself.

"""
import collections
import numpy as np
import cv2



_TITLE_LEFT_MARGIN = 10
_TITLE_TOP_MARGIN = 10
STANDARD_COLORS_PIL = [
    'AliceBlue', 'Chartreuse', 'Aqua', 'Aquamarine', 'Azure', 'Beige', 'Bisque',
    'BlanchedAlmond', 'BlueViolet', 'BurlyWood', 'CadetBlue', 'AntiqueWhite',
    'Chocolate', 'Coral', 'CornflowerBlue', 'Cornsilk', 'Crimson', 'Cyan',
    'DarkCyan', 'DarkGoldenRod', 'DarkGrey', 'DarkKhaki', 'DarkOrange',
    'DarkOrchid', 'DarkSalmon', 'DarkSeaGreen', 'DarkTurquoise', 'DarkViolet',
    'DeepPink', 'DeepSkyBlue', 'DodgerBlue', 'FireBrick', 'FloralWhite',
    'ForestGreen', 'Fuchsia', 'Gainsboro', 'GhostWhite', 'Gold', 'GoldenRod',
    'Salmon', 'Tan', 'HoneyDew', 'HotPink', 'IndianRed', 'Ivory', 'Khaki',
    'Lavender', 'LavenderBlush', 'LawnGreen', 'LemonChiffon', 'LightBlue',
    'LightCoral', 'LightCyan', 'LightGoldenRodYellow', 'LightGray', 'LightGrey',
    'LightGreen', 'LightPink', 'LightSalmon', 'LightSeaGreen', 'LightSkyBlue',
    'LightSlateGray', 'LightSlateGrey', 'LightSteelBlue', 'LightYellow', 'Lime',
    'LimeGreen', 'Linen', 'Magenta', 'MediumAquaMarine', 'MediumOrchid',
    'MediumPurple', 'MediumSeaGreen', 'MediumSlateBlue', 'MediumSpringGreen',
    'MediumTurquoise', 'MediumVioletRed', 'MintCream', 'MistyRose', 'Moccasin',
    'NavajoWhite', 'OldLace', 'Olive', 'OliveDrab', 'Orange', 'OrangeRed',
    'Orchid', 'PaleGoldenRod', 'PaleGreen', 'PaleTurquoise', 'PaleVioletRed',
    'PapayaWhip', 'PeachPuff', 'Peru', 'Pink', 'Plum', 'PowderBlue', 'Purple',
    'Red', 'RosyBrown', 'RoyalBlue', 'SaddleBrown', 'Green', 'SandyBrown',
    'SeaGreen', 'SeaShell', 'Sienna', 'Silver', 'SkyBlue', 'SlateBlue',
    'SlateGray', 'SlateGrey', 'Snow', 'SpringGreen', 'SteelBlue', 'GreenYellow',
    'Teal', 'Thistle', 'Tomato', 'Turquoise', 'Violet', 'Wheat', 'White',
    'WhiteSmoke', 'Yellow', 'YellowGreen'
]

''' PIL RGB colors to OpenCV BGR
for color in STANDARD_COLORS:
    rgb = ImageColor.getrgb(color)
    bgr = (rgb[2],rgb[1],rgb[0])
    print("  {}, # {}".format(bgr,color))
'''
STANDARD_COLORS = [
  (0, 0, 0), # Blank color for Background
  (0, 140, 255), # DarkOrange
  (211, 0, 148), # DarkViolet
  (255, 255, 0), # Aqua
  (203, 192, 255), # Pink
  (139, 139, 0), # DarkCyan
  (255, 248, 240), # AliceBlue
  (0, 255, 127), # Chartreuse
  (212, 255, 127), # Aquamarine
  (255, 255, 240), # Azure
  (220, 245, 245), # Beige
  (196, 228, 255), # Bisque
  (205, 235, 255), # BlanchedAlmond
  (226, 43, 138), # BlueViolet
  (135, 184, 222), # BurlyWood
  (160, 158, 95), # CadetBlue
  (215, 235, 250), # AntiqueWhite
  (30, 105, 210), # Chocolate
  (80, 127, 255), # Coral
  (237, 149, 100), # CornflowerBlue
  (220, 248, 255), # Cornsilk
  (60, 20, 220), # Crimson
  (255, 255, 0), # Cyan
  (11, 134, 184), # DarkGoldenRod
  (169, 169, 169), # DarkGrey
  (107, 183, 189), # DarkKhaki
  (204, 50, 153), # DarkOrchid
  (122, 150, 233), # DarkSalmon
  (143, 188, 143), # DarkSeaGreen
  (209, 206, 0), # DarkTurquoise
  (147, 20, 255), # DeepPink
  (255, 191, 0), # DeepSkyBlue
  (255, 144, 30), # DodgerBlue
  (34, 34, 178), # FireBrick
  (240, 250, 255), # FloralWhite
  (34, 139, 34), # ForestGreen
  (255, 0, 255), # Fuchsia
  (220, 220, 220), # Gainsboro
  (255, 248, 248), # GhostWhite
  (0, 215, 255), # Gold
  (32, 165, 218), # GoldenRod
  (114, 128, 250), # Salmon
  (140, 180, 210), # Tan
  (240, 255, 240), # HoneyDew
  (180, 105, 255), # HotPink
  (92, 92, 205), # IndianRed
  (240, 255, 255), # Ivory
  (140, 230, 240), # Khaki
  (250, 230, 230), # Lavender
  (245, 240, 255), # LavenderBlush
  (0, 252, 124), # LawnGreen
  (205, 250, 255), # LemonChiffon
  (230, 216, 173), # LightBlue
  (128, 128, 240), # LightCoral
  (255, 255, 224), # LightCyan
  (210, 250, 250), # LightGoldenRodYellow
  (211, 211, 211), # LightGray
  (211, 211, 211), # LightGrey
  (144, 238, 144), # LightGreen
  (193, 182, 255), # LightPink
  (122, 160, 255), # LightSalmon
  (170, 178, 32), # LightSeaGreen
  (250, 206, 135), # LightSkyBlue
  (153, 136, 119), # LightSlateGray
  (153, 136, 119), # LightSlateGrey
  (222, 196, 176), # LightSteelBlue
  (224, 255, 255), # LightYellow
  (0, 255, 0), # Lime
  (50, 205, 50), # LimeGreen
  (230, 240, 250), # Linen
  (255, 0, 255), # Magenta
  (170, 205, 102), # MediumAquaMarine
  (211, 85, 186), # MediumOrchid
  (219, 112, 147), # MediumPurple
  (113, 179, 60), # MediumSeaGreen
  (238, 104, 123), # MediumSlateBlue
  (154, 250, 0), # MediumSpringGreen
  (204, 209, 72), # MediumTurquoise
  (133, 21, 199), # MediumVioletRed
  (250, 255, 245), # MintCream
  (225, 228, 255), # MistyRose
  (181, 228, 255), # Moccasin
  (173, 222, 255), # NavajoWhite
  (230, 245, 253), # OldLace
  (0, 128, 128), # Olive
  (35, 142, 107), # OliveDrab
  (0, 165, 255), # Orange
  (0, 69, 255), # OrangeRed
  (214, 112, 218), # Orchid
  (170, 232, 238), # PaleGoldenRod
  (152, 251, 152), # PaleGreen
  (238, 238, 175), # PaleTurquoise
  (147, 112, 219), # PaleVioletRed
  (213, 239, 255), # PapayaWhip
  (185, 218, 255), # PeachPuff
  (63, 133, 205), # Peru
  (221, 160, 221), # Plum
  (230, 224, 176), # PowderBlue
  (128, 0, 128), # Purple
  (0, 0, 255), # Red
  (143, 143, 188), # RosyBrown
  (225, 105, 65), # RoyalBlue
  (19, 69, 139), # SaddleBrown
  (0, 128, 0), # Green
  (96, 164, 244), # SandyBrown
  (87, 139, 46), # SeaGreen
  (238, 245, 255), # SeaShell
  (45, 82, 160), # Sienna
  (192, 192, 192), # Silver
  (235, 206, 135), # SkyBlue
  (205, 90, 106), # SlateBlue
  (144, 128, 112), # SlateGray
  (144, 128, 112), # SlateGrey
  (250, 250, 255), # Snow
  (127, 255, 0), # SpringGreen
  (180, 130, 70), # SteelBlue
  (47, 255, 173), # GreenYellow
  (128, 128, 0), # Teal
  (216, 191, 216), # Thistle
  (71, 99, 255), # Tomato
  (208, 224, 64), # Turquoise
  (238, 130, 238), # Violet
  (179, 222, 245), # Wheat
  (255, 255, 255), # White
  (245, 245, 245), # WhiteSmoke
  (0, 255, 255), # Yellow
  (50, 205, 154), # YellowGreen
]


def draw_bounding_box_on_image_cv(image,
                                  ymin,
                                  xmin,
                                  ymax,
                                  xmax,
                                  color='red',
                                  thickness=4,
                                  display_str_list=(),
                                  use_normalized_coordinates=True):
  im_height, im_width = image.shape[:2]
  if use_normalized_coordinates:
    (left, right, top, bottom) = (xmin * im_width, xmax * im_width,
                                  ymin * im_height, ymax * im_height)
  else:
    (left, right, top, bottom) = (xmin, xmax, ymin, ymax)

  ####################
  # draw objectbox
  ####################
  points = np.array([[left, top], [left, bottom], [right, bottom], [right, top], [left, top]])
  cv2.polylines(image, np.int32([points]),
                isClosed=False, thickness=thickness, color=color, lineType=cv2.LINE_AA)

  ####################
  # calculate str width and height
  ####################
  fontFace = cv2.FONT_HERSHEY_SIMPLEX
  fontScale = 0.4
  fontThickness = 1
  display_str_heights = [cv2.getTextSize(text=ds, fontFace=fontFace, fontScale=fontScale, thickness=fontThickness)[0][1] for ds in display_str_list]
  total_display_str_height = (1 + 2 * 0.05) * sum(display_str_heights)

  if top > total_display_str_height:
    text_bottom = top
  else:
    text_bottom = bottom + total_display_str_height

  ####################
  # draw textbox and text
  ####################
  for display_str in display_str_list[::-1]:
    # 
    [(text_width, text_height), baseLine] = cv2.getTextSize(text=display_str, fontFace=fontFace, fontScale=fontScale, thickness=fontThickness)
    margin = np.ceil(0.05 * text_height)

    cv2.rectangle(image, (int(left), int(text_bottom - 3 * baseLine - text_height - 2 * margin)), (int(left + text_width), int(text_bottom - baseLine)), color=color, thickness=-1)
    cv2.putText(image, display_str, org=(int(left + margin), int(text_bottom - text_height - margin)), fontFace=fontFace, fontScale=fontScale, thickness=fontThickness, color=(0, 0, 0))
  
    text_bottom -= text_height - 2 * margin


def draw_bounding_box_on_image_array_cv(image,
                                     ymin,
                                     xmin,
                                     ymax,
                                     xmax,
                                     color=(0, 255, 0),
                                     thickness=4,
                                     display_str_list=(),
                                     use_normalized_coordinates=True):
  """Adds a bounding box to an image (numpy array).

  Bounding box coordinates can be specified in either absolute (pixel) or
  normalized coordinates by setting the use_normalized_coordinates argument.

  Args:
    image: a numpy array with shape [height, width, 3].
    ymin: ymin of bounding box.
    xmin: xmin of bounding box.
    ymax: ymax of bounding box.
    xmax: xmax of bounding box.
    color: color to draw bounding box. Default is red.
    thickness: line thickness. Default value is 4.
    display_str_list: list of strings to display in box
                      (each to be shown on its own line).
    use_normalized_coordinates: If True (default), treat coordinates
      ymin, xmin, ymax, xmax as relative to the image.  Otherwise treat
      coordinates as absolute.
  """
  draw_bounding_box_on_image_cv(image, ymin, xmin, ymax, xmax, color,
                             thickness, display_str_list,
                             use_normalized_coordinates)


def visualize_boxes_and_labels_on_image_array(
    image,
    boxes,
    classes,
    scores,
    category_index,
    use_normalized_coordinates=False,
    max_boxes_to_draw=20,
    min_score_thresh=.5,
    agnostic_mode=False,
    line_thickness=4,
    groundtruth_box_visualization_color=(0, 0, 0),
    skip_scores=False,
    skip_labels=False):
  """Overlay labeled boxes on an image with formatted scores and label names.

  This function groups boxes that correspond to the same location
  and creates a display string for each detection and overlays these
  on the image. Note that this function modifies the image in place, and returns
  that same image.

  Args:
    image: uint8 numpy array with shape (img_height, img_width, 3)
    boxes: a numpy array of shape [N, 4]
    classes: a numpy array of shape [N]. Note that class indices are 1-based,
      and match the keys in the label map.
    scores: a numpy array of shape [N] or None.  If scores=None, then
      this function assumes that the boxes to be plotted are groundtruth
      boxes and plot all boxes as black with no classes or scores.
    category_index: a dict containing category dictionaries (each holding
      category index `id` and category name `name`) keyed by category indices.
    use_normalized_coordinates: whether boxes is to be interpreted as
      normalized coordinates or not.
    max_boxes_to_draw: maximum number of boxes to visualize.  If None, draw
      all boxes.
    min_score_thresh: minimum score threshold for a box to be visualized
    agnostic_mode: boolean (default: False) controlling whether to evaluate in
      class-agnostic mode or not.  This mode will display scores but ignore
      classes.
    line_thickness: integer (default: 4) controlling line width of the boxes.
    groundtruth_box_visualization_color: box color for visualizing groundtruth
      boxes
    skip_scores: whether to skip score when drawing a single detection
    skip_labels: whether to skip label when drawing a single detection

  Returns:
    uint8 numpy array with shape (img_height, img_width, 3) with overlaid boxes.
  """
  # Create a display string (and color) for every box location, group any boxes
  # that correspond to the same location.
  box_to_display_str_map = collections.defaultdict(list)
  box_to_color_map = collections.defaultdict(str)
  if not max_boxes_to_draw:
    max_boxes_to_draw = boxes.shape[0]
  for i in range(min(max_boxes_to_draw, boxes.shape[0])):
    if scores is None or scores[i] > min_score_thresh:
      box = tuple(boxes[i].tolist())
      if scores is None:
        box_to_color_map[box] = groundtruth_box_visualization_color
      else:
        display_str = ''
        if not skip_labels:
          if not agnostic_mode:
            if classes[i] in category_index.keys():
              class_name = category_index[classes[i]]['name']
            else:
              class_name = 'N/A'
            display_str = str(class_name)
        if not skip_scores:
          if not display_str:
            display_str = '{}%'.format(int(100*scores[i]))
          else:
            display_str = '{}: {}%'.format(display_str, int(100*scores[i]))
        box_to_display_str_map[box].append(display_str)
        if agnostic_mode:
          box_to_color_map[box] = (0, 140, 255) # 'DarkOrange'
        else:
          box_to_color_map[box] = STANDARD_COLORS[
              classes[i] % len(STANDARD_COLORS)]

  # Draw all boxes onto image.
  for box, color in box_to_color_map.items():
    ymin, xmin, ymax, xmax = box
    draw_bounding_box_on_image_array_cv(
        image,
        ymin,
        xmin,
        ymax,
        xmax,
        color=color,
        thickness=line_thickness,
        display_str_list=box_to_display_str_map[box],
        use_normalized_coordinates=use_normalized_coordinates)

  return image

