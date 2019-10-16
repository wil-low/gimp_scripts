#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gimpfu import *

def hor_line(x, y, line_len):
  return [x, y, x + line_len, y]

def vert_line(x, y, line_len):
  return [x, y, x, y + line_len]

def crosses_for_guides(image, cross_len, cross_color):
  hor_guides = []
  vert_guides = []

  guide = 0

  guide = pdb.gimp_image_find_next_guide(image, guide)
  while guide != 0:
    pos = pdb.gimp_image_get_guide_position(image, guide)
    if pdb.gimp_image_get_guide_orientation(image, guide) == 0:
      hor_guides.append(pos)
    else:
      vert_guides.append(pos)

    guide = pdb.gimp_image_find_next_guide(image, guide)

  if len(hor_guides) == 0:
    pdb.gimp_message("No horizontal guides!")
    return

  if len(vert_guides) == 0:
    pdb.gimp_message("No vertical guides!")
    return

  pdb.gimp_context_push()
  pdb.gimp_image_undo_group_start(image)

  layer = pdb.gimp_layer_new(image, pdb.gimp_image_width(image), pdb.gimp_image_height(image), RGBA_IMAGE, "[foreground] crosses_for_guides", 100, NORMAL_MODE)

  pdb.gimp_image_insert_layer(image, layer, None, -1)
  pdb.gimp_edit_clear(layer)

  pdb.gimp_context_set_foreground(cross_color)
  pdb.gimp_context_set_brush("2. Hardness 100")
  pdb.gimp_context_set_brush_size(1)

  pdb.gimp_image_set_active_layer(image, layer)
  draw = pdb.gimp_image_get_active_drawable(image)

  for x in vert_guides:
    for y in hor_guides:
        pdb.gimp_pencil(draw, 4, hor_line(x - cross_len, y - 1, cross_len * 2))
        pdb.gimp_pencil(draw, 4, vert_line(x - 1, y - cross_len, cross_len * 2))
        pdb.gimp_pencil(draw, 4, hor_line(x - cross_len, y, cross_len * 2))
        pdb.gimp_pencil(draw, 4, vert_line(x, y - cross_len, cross_len * 2))

  pdb.gimp_displays_flush()

  pdb.gimp_image_undo_group_end(image)
  pdb.gimp_context_pop()

register(
          "python_fu_crosses_for_guides",
          "Add crosses into guides intersections",
          "Crosses are created on a new layer",
          "wil_low",
          "wil_low",
          "2019.06.02",
          "Add crosses for guides", 
          "*",
          [
              (PF_IMAGE, "image", "Source image", None),
              (PF_INT, "cross_len", "Cross length", "20"),
              (PF_COLOR, "cross_color",  "Cross color", (0,0,0))
              
          ],
          [],
          crosses_for_guides, menu="<Image>/Script-Fu")

main()

