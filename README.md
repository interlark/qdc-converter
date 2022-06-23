[Русский](https://github.com/interlark/qdc-converter/blob/main/README.md) | [English](https://github.com/interlark/qdc-converter/blob/main/README.en.md)

# QDC Конвертер
[![Tests](https://github.com/interlark/qdc-converter/actions/workflows/tests.yml/badge.svg)](https://github.com/interlark/qdc-converter/actions/workflows/tests.yml)
[![PyPi version](https://badgen.net/pypi/v/qdc-converter)](https://pypi.org/project/qdc-converter)
[![Supported Python versions](https://badgen.net/pypi/python/qdc-converter)](https://pypi.org/project/qdc-converter)
[![License](https://badgen.net/pypi/license/qdc-converter)](https://github.com/interlark/qdc-converter/blob/main/LICENSE)

Конвертер ***.qdc** *(Garmin QuickDraw Contours)* в таблицу ***.csv** *(CSV таблица)* или ***.grd** *(Растр ESRI ASCII Grid)*

![Screencast](https://user-images.githubusercontent.com/20641837/175391112-c11a74c1-5b84-444a-a2b7-ca611d933f36.gif)

## Установка
### Установка одним файлом
Скачать [релиз](https://github.com/interlark/qdc-converter/releases/latest).

### Установка из PyPI
```bash
# CLI
pip install qdc-converter
# CLI + GUI
pip install qdc-converter[gui]
```

### Установка из репозитория
```bash
git clone https://github.com/interlark/qdc-converter
cd qdc-converter

python -m venv venv

# Windows
.\venv\Scripts\activate.bat
# Linux, MacOS
. venv/bin/activate

# CLI
pip install .
# CLI + GUI
pip install .[gui]
```

## Использование
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


## Параметры
```bash
qdc-converter --help
```
```
Usage: qdc-converter [OPTIONS]

  QDC Конвертер.

  Конвертер Garmin's QDC файлов в CSV или GRD.

Options:
  Основные параметры:             Ключевые параметры конвертера
    -i, --qdc-folder-path DIRECTORY
                                  Путь до папки со вложенными контурами
                                  QuickDraw Contours (QDC).  [required]

    -o, --output-path FILE        Путь до сконвертированного файла (*.csv или
                                  *.grd).  [required]

    -l, --layer [0,1,2,3,4,5]     Слой данных (0 - Raw user data, 1 -
                                  Recommended).  [0<=x<=5; required]
  Параметры корректировки:        Корректировки
    -dx, --x-correction FLOAT     Корректировка X.
    -dy, --y-correction FLOAT     Корректировка Y.
    -dz, --z-correction FLOAT     Корректировка Z.
  CSV Параметры:                  Параметры касающиеся записи CSV таблицы
    -csvd, --csv-delimiter TEXT   CSV разделитель значений колонок (по-умолчанию ",").
    -csvs, --csv-skip-headers     Не записывать заголовок таблицы.
    -csvy, --csv-yxz              Изменить порядок записи с X,Y,Z на Y,X,Z в
                                  CSV таблице.
  Другие параметры:               Другие параметры конвертера
    -st, --singlethreaded         Запустить конвертер в одном потоке.
    -vc, --validity-codes         Записывать код качества вместо глубины.
    -q, --quite                   "Молчаливый режим"
  --version                       Show the version and exit.
  --help                          Show this message and exit.
```
