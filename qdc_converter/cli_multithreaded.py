import csv
import multiprocessing as mp
import os
import struct
from types import SimpleNamespace

import numpy as np
from pebble import concurrent
from tqdm import tqdm

from .cli import LAYER_PARAMETERS
from .utils import (chunks, get_files_recursively, patch_tqdm, print_error,
                    window)

MULTIPROCESSING_BATCH = 64


def shared_array_as_np(shared_array, x_size, y_size):
    '''
    Returns shared mp array as np.
    '''
    np_array = np.frombuffer(shared_array.get_obj(),
                             dtype=np.dtype(shared_array.get_obj()._type_))
    np_array = np_array.reshape((x_size, y_size))
    return np_array


@concurrent.process
def calculate_grd_rows(j_array, shared_array, validity_codes, x_size, y_size, z_correction):
    '''
    Multiprocessing GRD worker.
    '''
    result = []
    for j in j_array:
        row_values = []
        arr_depth = shared_array_as_np(shared_array, x_size, y_size)
        f_fix = lambda x: np.sign(x) * np.int16(np.abs(x))

        for i in range(x_size):
            if validity_codes:
                t_val = f_fix(arr_depth[i, j] / 4096)
                z = t_val * 10 + (arr_depth[i, j] - t_val * 4096) / 256
            else:
                z = arr_depth[i, j] / 100
            row_values.append(z + z_correction)
        result.append(row_values)

    return result


@concurrent.process
def calculate_csv_rows(j_array, shared_array, validity_codes, x_size, y_size, x_orig, y_orig, layer):
    '''
    Multiprocessing CSV worker.
    '''
    result = []
    for j in j_array:
        arr_depth = shared_array_as_np(shared_array, x_size, y_size)
        f_fix = lambda x: np.sign(x) * np.int16(np.abs(x))
        layer_parameters = SimpleNamespace(**LAYER_PARAMETERS[layer])

        for i in range(x_size):
            if arr_depth[i, j] > 0:  # Skip all 0 values
                if validity_codes:
                    t_val = f_fix(arr_depth[i, j] / 4096)
                    z = t_val * 10 + (arr_depth[i, j] - t_val * 4096) / 256
                else:
                    z = arr_depth[i, j] / 100

                # Adding a_step / 2 to move point to the middle of the cell extent
                x = x_orig + layer_parameters.a_step / 2 + i * layer_parameters.a_step
                y = y_orig + layer_parameters.a_step / 2 + j * layer_parameters.a_step

                result.append((x, y, z))

    return result


def calculates_generator(workers, target, args_chunks, **kwargs):
    """
    Multiprocess execution generator.
    """
    def futures_generator():
        for args in args_chunks:
            yield target(args, **kwargs)

    for future, *_ in window(futures_generator(), workers):
        yield future.result()


def run_cli(qdc_folder_path, output_path, layer, validity_codes, quite, x_correction, y_correction, z_correction,
            csv_delimiter, csv_skip_headers, csv_yxz, multithreaded, message_queue=None):
    # Patch tqdm to duplicate messages up to the passed message queue.
    if message_queue:
        patch_tqdm(tqdm, message_queue)

    assert multithreaded

    try:
        # Some arguments validation
        output_path_ext = os.path.splitext(output_path)[-1]
        if output_path_ext.lower() not in ('.csv', '.grd'):
            raise ValueError(_('Output file extension must be *.csv (CSV table) or *.grd (ESRI ASCII grid)'))

        layer_parameters = SimpleNamespace(**LAYER_PARAMETERS[layer])
        qdc_files = get_files_recursively(qdc_folder_path, '.qdc')

        # Calculate boundaries
        x_min, y_min = 32000, 32000
        x_max, y_max = -32000, -32000
        for qdc_file in qdc_files:
            qdc_file_size = os.path.getsize(qdc_file)
            if qdc_file_size in (layer_parameters.f_size1, layer_parameters.f_size2,
                                 layer_parameters.f_size3, layer_parameters.f_size4):
                with open(qdc_file, 'rb') as f_qdc:
                    f_qdc.seek(164)
                    val = struct.unpack('<h', f_qdc.read(2))[0]
                    x_min = min(val, x_min)
                    x_max = max(val, x_max)

                    f_qdc.seek(160)
                    val = struct.unpack('<h', f_qdc.read(2))[0]
                    y_min = min(val, y_min)
                    y_max = max(val, y_max)

        if x_min == 32000 or y_min == 32000 \
           or x_max == -32000 or y_max == -32000:
            raise RuntimeError(_('No valid QDC files found!'))

        x_size = (x_max - x_min + 1) * layer_parameters.l_size
        y_size = (y_max - y_min + 1) * layer_parameters.l_size
        arr_depth = np.zeros((x_size, y_size), dtype=np.int16)

        # Calculate depth array
        for qdc_file in tqdm(qdc_files, desc=_('Calculating depth map'), disable=quite):
            qdc_file_size = os.path.getsize(qdc_file)
            if qdc_file_size in (layer_parameters.f_size1, layer_parameters.f_size2,
                                 layer_parameters.f_size3, layer_parameters.f_size4):
                with open(qdc_file, 'rb') as f_qdc:
                    f_qdc.seek(164)
                    val = struct.unpack('<h', f_qdc.read(2))[0]
                    x_orig = (val - x_min) * layer_parameters.l_size2

                    f_qdc.seek(160)
                    val = struct.unpack('<h', f_qdc.read(2))[0]
                    y_orig = (val - y_min) * layer_parameters.l_size2

                    if qdc_file_size == layer_parameters.f_size1:
                        i = layer_parameters.f_offset1
                    elif qdc_file_size == layer_parameters.f_size2:
                        i = layer_parameters.f_offset2
                    elif qdc_file_size == layer_parameters.f_size3:
                        i = layer_parameters.f_offset3
                    elif qdc_file_size == layer_parameters.f_size4:
                        i = layer_parameters.f_offset4

                    for yy in range(layer_parameters.n_sectors + 1):
                        for xx in range(layer_parameters.n_sectors + 1):
                            for y in range(32):
                                for x in range(32):
                                    x_abs = xx * 32 + x + x_orig
                                    y_abs = yy * 32 + y + y_orig
                                    f_qdc.seek(i + 1)
                                    val_code = struct.unpack('<h', f_qdc.read(2))[0]  # Read validity code

                                    if validity_codes:  # Write validity codes to array instead of depth
                                        arr_depth[x_abs, y_abs] = val_code
                                    else:
                                        if val_code != 0:
                                            f_qdc.seek(i - 1)
                                            val_depth = struct.unpack('<h', f_qdc.read(2))[0]  # Read depth in cm
                                            arr_depth[x_abs, y_abs] = val_depth
                                    i += 4

        x_orig = x_min * 90 / 2 ** 14
        y_orig = y_min * 90 / 2 ** 14

        # Create shared memory array that could be accessed from other
        # processes instead of pickling and passing it on each fork.
        mp_array_typecode = np.ctypeslib.as_ctypes(arr_depth.dtype.type())._type_
        shared_array = mp.Array(typecode_or_type=mp_array_typecode,
                                size_or_initializer=arr_depth.size)

        np_shared_depth_array = shared_array_as_np(shared_array, x_size, y_size)
        np.copyto(np_shared_depth_array, arr_depth)

        # Save depth array to *.csv or *.grd
        if output_path_ext.lower() == '.grd':
            # ESRI ASCII grid
            with open(output_path, 'w') as f_grd:
                f_grd.write(f'NCOLS {x_size}\n')
                f_grd.write(f'NROWS {y_size}\n')
                f_grd.write(f'XLLCORNER {x_orig}\n')
                f_grd.write(f'YLLCORNER {y_orig}\n')
                f_grd.write(f'CELLSIZE {layer_parameters.a_step}\n')
                f_grd.write('NODATA_VALUE 0\n')

                args_chunks = list(chunks(range(y_size - 1, -1, -1), MULTIPROCESSING_BATCH))
                kwargs = dict(
                    shared_array=shared_array, validity_codes=validity_codes,
                    x_size=x_size, y_size=y_size, z_correction=z_correction
                )

                for rows_set in tqdm(desc=_('Saving Esri ASCII raster'), disable=quite, total=len(args_chunks),
                                     iterable=calculates_generator(workers=mp.cpu_count(), args_chunks=args_chunks,
                                                                   target=calculate_grd_rows, **kwargs)):
                    for rows in rows_set:
                        f_grd.write(' '.join(str(x) for x in rows) + '\n')

            # Write projection file
            output_path_prj = output_path[:-4] + '.prj'
            with open(output_path_prj, 'w') as f_prj:
                f_prj.write('GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",'
                            'SPHEROID["WGS_1984",6378137.0,298.257223563]],'
                            'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]')

        elif output_path_ext.lower() == '.csv':
            # CSV table
            with open(output_path, 'w', newline='') as f_csv:
                writer = csv.writer(f_csv, delimiter=csv_delimiter)

                # Write header
                if not csv_skip_headers:
                    if csv_yxz:
                        if validity_codes:
                            writer.writerow(['Y', 'X', 'ValCode'])
                        else:
                            writer.writerow(['Y', 'X', 'Depth(m)'])
                    else:
                        if validity_codes:
                            writer.writerow(['X', 'Y', 'ValCode'])
                        else:
                            writer.writerow(['X', 'Y', 'Depth(m)'])

                # Write data
                args_chunks = list(chunks(range(y_size - 1, -1, -1), MULTIPROCESSING_BATCH))
                kwargs = dict(
                    shared_array=shared_array, validity_codes=validity_codes,
                    x_size=x_size, y_size=y_size, x_orig=x_orig, y_orig=y_orig, layer=layer
                )

                for rows in tqdm(desc=_('Saving CSV table'), disable=quite, total=len(args_chunks),
                                 iterable=calculates_generator(workers=mp.cpu_count(), args_chunks=args_chunks,
                                                               target=calculate_csv_rows, **kwargs)):
                    for x, y, z in rows:
                        if csv_yxz:
                            writer.writerow([y + y_correction, x + x_correction, z + z_correction])
                        else:
                            writer.writerow([x + x_correction, y + y_correction, z + z_correction])

    except Exception as e:
        print_error(f'{_("Error")}: {e}', message_queue)
        raise
