#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gimpfu import *

def layered_guillotine(image, prefix, use_prefix_as_group_name, append_layer_name_to_prefix, tgt_image, min_width, min_height):
  max_width = 0
  max_height = 0

  # sorted guides
  hor_guides = []
  vert_guides = []

  guide = 0
  guide = pdb.gimp_image_find_next_guide(image, guide)
  while guide != 0:
    pos = pdb.gimp_image_get_guide_position(image, guide)
    #pdb.gimp_message("guide found: " + str(guide) + ", pos " + str(pos))
    if pdb.gimp_image_get_guide_orientation(image, guide) == 0:
      hor_guides.append(pos)
    else:
      vert_guides.append(pos)
    guide = pdb.gimp_image_find_next_guide(image, guide)

  if len(hor_guides) == 0 and len(vert_guides) == 0:
    pdb.gimp_message("No guides!")
    return

  hor_guides.append(pdb.gimp_image_height(image))
  vert_guides.append(pdb.gimp_image_width(image))

  hor_guides.sort()
  vert_guides.sort()

  # lists of coords (x/y, w/h)
  x_coords = []
  y_coords = []

  prev_hor_guide = 0
  prev_vert_guide = 0

  guide = pdb.gimp_image_find_next_guide(image, guide)

  for pos in vert_guides:
    delta = pos - prev_vert_guide
    #pdb.gimp_message("guide_v delta: " + str(delta))
    if delta >= min_width:
      x_coords.append((prev_vert_guide, delta))
      if delta > max_width:
        max_width = delta
      #pdb.gimp_message("y_coords " + "%d, %d, %d" % (pos, prev_vert_guide, delta))
    prev_vert_guide = pos

  for pos in hor_guides:
    delta = pos - prev_hor_guide
    #pdb.gimp_message("guide_h delta: " + str(delta))
    if delta >= min_height:
      y_coords.append((prev_hor_guide, delta))
      if delta > max_height:
        max_height = delta
      #pdb.gimp_message("x_coords " + "%d, %d, %d" % (pos, prev_hor_guide, delta))
    prev_hor_guide = pos

  #pdb.gimp_message("x_coords " + repr(x_coords))
  #pdb.gimp_message("y_coords " + repr(y_coords))

  if len(x_coords) == 0 and len(y_coords) == 0:
    pdb.gimp_message("No coords!")
    return

  pdb.gimp_context_push()
  pdb.gimp_image_undo_group_start(image)

  images = gimp.image_list()
  image_ids = pdb.gimp_image_list()[1]

  out_img = -1

  tgt_group = None
  new_display = False

  try:
    i = image_ids.index(tgt_image)
    out_img = images[i]
    if use_prefix_as_group_name == 1:
      for layer in out_img.layers:
        if pdb.gimp_item_get_name(layer) == prefix:
          if pdb.gimp_item_is_group(layer):
            tgt_group = layer
            break 
  except ValueError:
    out_img = pdb.gimp_image_new(max_width, max_height, RGB)
    new_display = True

  if tgt_group is None:
    tgt_group = pdb.gimp_layer_group_new(out_img)
    pdb.gimp_item_set_name(tgt_group, prefix)
    pdb.gimp_image_insert_layer(out_img, tgt_group, None, 0)

  if append_layer_name_to_prefix == 1:
    prefix += "_" + pdb.gimp_item_get_name(pdb.gimp_image_get_active_layer(image))

  total_ops = float(len(x_coords) * len(y_coords))

  draw0 = pdb.gimp_image_get_active_drawable(image)

  counter = 0
  for i in range(len(y_coords)):
    for j in range(len(x_coords)):
      x = x_coords[j]
      y = y_coords[i]

      pdb.gimp_image_select_rectangle(image, CHANNEL_OP_REPLACE, x[0], y[0], x[1], y[1])
      pdb.gimp_edit_copy(draw0)

      layer = pdb.gimp_layer_new(out_img, max_width, max_height, RGBA_IMAGE, "%s_%02d_%02d" % (prefix, i, j), 100, NORMAL_MODE)

      pdb.gimp_image_insert_layer(out_img, layer, tgt_group, -1)
      pdb.gimp_edit_clear(layer)

      pdb.gimp_image_set_active_layer(out_img, layer)
      pdb.gimp_edit_paste(layer, TRUE)
      layer = pdb.gimp_image_get_floating_sel(out_img)
      pdb.gimp_floating_sel_anchor(layer)
      counter += 1
      pdb.gimp_progress_update(counter / total_ops)

  if new_display:
    pdb.gimp_display_new(out_img)

  pdb.gimp_selection_none(image)
  pdb.gimp_selection_none(out_img)

  pdb.gimp_displays_flush()

  pdb.gimp_image_undo_group_end(image)
  pdb.gimp_context_pop()

register(
          "python_fu_layered_guillotine",
          "Dissect image on guides and put them as layers into a new image",
          "",
          "wil_low",
          "wil_low",
          "2019.10.16",
          "Layered guillotine", 
          "*",
          [
              (PF_IMAGE, "image", "Source image", None),
              (PF_STRING, "prefix", "Layer name prefix", "pr"),
              (PF_TOGGLE, "use_prefix_as_group_name", "Use prefix as group name", 1),
              (PF_TOGGLE, "append_layer_name_to_prefix", "Add layer name to prefix", 1),
              (PF_INT, "tgt_image", "Target image ID", "-1"),
              (PF_INT, "min_width", "Minimal width", "100"),
              (PF_INT, "min_height",  "Minimal height", "100")
              
          ],
          [],
          layered_guillotine, menu="<Image>/Script-Fu")

main()

