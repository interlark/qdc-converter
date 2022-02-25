# QDC Конвертер

Конвертер **Garmin QuickDraw QDC файлов** в таблицу ***.csv (CSV таблица)** или ***.grd (Растр ESRI ASCII Grid)**

# Установка
```bash
pip install qdc-converter
```

# Использование
Основные параметры: **-i**, **-o** и **-l**.

* Пример конвертирования папки ```Contours``` с вложенными ***.qdc** файлами в таблицу ```export_table.csv``` с 3 полями ```X``` *(долгота в десятичных градусах)*, ```Y``` *(широта в десятичных градусах)* и  ```Depth(m)``` *(глубина в метрах)*, используя слой данных L_**1**:
  ```
  qdc-converter -i "Contours" -o "export_table.csv" -l 1
  ```

* Пример конвертирования папки ```Contours``` с вложенными ***.qdc** файлами в растр ```export_raster.grd```, используя слой данных L_**0**:
  ```
  qdc-converter -i "Contours" -o "export_raster.grd" -l 0
  ```
  Полученный растр можно загрузить во многие ГИС (например, QGIS) и сконвертировать в более быстрочитаемый формат.


# Параметры
```bash
qdc-converter --help
```
```bash
Usage: qdc-converter [OPTIONS]

  QDC конвертер.

Options:
  Основные параметры:             Ключевые параметры конвертера
    -i, --qdc-folder-path DIRECTORY
                                  Путь до папки со вложенными контурами
                                  QuickDraw Contours (QDC).  [required]

    -o, --output-path FILE        Путь до сконвертированного файла (*.csv или
                                  *.grd).  [required]

    -l, --layer [0,1,2,3,4,5]     Слой данных (0 - Raw user data, 1 -
                                  Recommended).  [required]

    -vc, --validity-codes         Записывать код качества вместо глубины.
    -q, --quite                   "Молчаливый режим"
  Параметры корректировки:        Корректировки
    -dx, --x-correction FLOAT     Корректировка X.
    -dy, --y-correction FLOAT     Корректировка Y.
    -dz, --z-correction FLOAT     Корректировка Z.
  CSV Параметры:                  Параметры касающиеся записи CSV таблицы
    -csvd, --csv-delimiter TEXT   CSV разделитель значений колонок.
    -csvs, --csv-skip-headers     Не записывать заголовок таблицы.
    -csvy, --csv-yxz              Изменить порядок записи с X,Y,Z на Y,X,Z в
                                  CSV таблице.

  --help                          Show this message and exit.

```
