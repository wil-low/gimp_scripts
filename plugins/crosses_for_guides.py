#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Импортируем необходимые модули
from gimpfu import *

def hor_line(x, y, line_len):
  return [x, y, x + line_len, y]

def vert_line(x, y, line_len):
  return [x, y, x, y + line_len]

def crosses_for_guides(image, drawable, cross_len, cross_color):
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
  # Запрещаем запись информации для отмены действий,
  # что бы все выполненные скриптом операции можно было отменить одим махом
  # нажав Ctrl + Z или выбрав из меню "Правка" пункт "Отменить действие"
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
        #pdb.gimp_message("Cross: " + str(x) + ", " + str(y))
        pdb.gimp_pencil(draw, 4, hor_line(x - cross_len, y - 1, cross_len * 2))
        pdb.gimp_pencil(draw, 4, vert_line(x - 1, y - cross_len, cross_len * 2))
        pdb.gimp_pencil(draw, 4, hor_line(x - cross_len, y, cross_len * 2))
        pdb.gimp_pencil(draw, 4, vert_line(x, y - cross_len, cross_len * 2))

  # Обновляем изоборажение на дисплее
  pdb.gimp_displays_flush()

  # Разрешаем запись информации для отмены действий
  pdb.gimp_image_undo_group_end(image)
  pdb.gimp_context_pop()

# Регистрируем функцию в PDB
register(
          "python_fu_crosses_for_guides", # Имя регистрируемой функции
          "Add crosses in guides intersections", # Информация о дополнении
          "Crossed are created on a new layer", # Короткое описание выполняемых скриптом действий
          "Andrei Ivushkin", # Информация об авторе
          "Andrei Ivushkin", # Информация о копирайте (копилефте?)
          "2019.06.02", # Дата изготовления
          "Add crosses in guides", # Название пункта меню, с помощью которого дополнение будет запускаться
          "*", # Типы изображений с которыми может работать дополнение
          [
              (PF_IMAGE, "image", "Исходное изображение", None), # Указатель на изображение
              (PF_DRAWABLE, "drawable", "Исходный слой", None), # Указатель на слой
              (PF_INT, "cross_len", "Cross length", "20"), # Ширана рамки
              (PF_COLOR, "cross_color",  "Cross color", (0,0,0)) # Цвет рамки
              
          ],
          [], # Список переменных которые вернет дополнение
          crosses_for_guides, menu="<Image>/Script-Fu") # Имя исходной функции и меню в которое будет помещён пункт запускающий дополнение

# Запускаем скрипт
main()

