import csv
import os
import struct
from types import SimpleNamespace

import numpy as np
from tqdm import tqdm

from .utils import get_files_recursively, patch_tqdm, print_error


LAYER_PARAMETERS = {
    0: {
        'a_step': 90 / 2 ** 22,
        'n_sectors': 7,
        'f_size1': 372736,
        'f_offset1': 4097,
        'f_size2': 352256,
        'f_offset2': 4097,
        'f_size3': -1,
        'f_offset3': 0,
        'f_size4': -1,
        'f_offset4': 0,
        'l_size': 256,
        'l_size2': 256,
    },
    1: {
        'a_step': 90 / 2 ** 21,
        'n_sectors': 3,
        'f_size1': 372736,
        'f_offset1': 266241,
        'f_size2': 352256,
        'f_offset2': 266241,
        'f_size3': 110592,
        'f_offset3': 4097,
        'f_size4': 90112,
        'f_offset4': 4097,
        'l_size': 128,
        'l_size2': 128,
    },
    2: {
        'a_step': 90 / 2 ** 20,
        'n_sectors': 1,
        'f_size1': 372736,
        'f_offset1': 331777,
        'f_size2': 352256,
        'f_offset2': 331777,
        'f_size3': 110592,
        'f_offset3': 69633,
        'f_size4': 90112,
        'f_offset4': 69633,
        'l_size': 64,
        'l_size2': 64,
    },
    3: {
        'a_step': 90 / 2 ** 19,
        'n_sectors': 0,
        'f_size1': 372736,
        'f_offset1': 348161,
        'f_size2': 352256,
        'f_offset2': 348161,
        'f_size3': 110592,
        'f_offset3': 86017,
        'f_size4': 90112,
        'f_offset4': 86017,
        'l_size': 32,
        'l_size2': 32,
    },
    4: {
        'a_step': 90 / 2 ** 18,
        'n_sectors': 1,
        'f_size1': 372736,
        'f_offset1': 352257,
        'f_size2': -1,
        'f_offset2': 0,
        'f_size3': 110592,
        'f_offset3': 90113,
        'f_size4': -1,
        'f_offset4': 0,
        'l_size': 64,
        'l_size2': 16,
    },
    5: {
        'a_step': 90 / 2 ** 17,
        'n_sectors': 0,
        'f_size1': 372736,
        'f_offset1': 368641,
        'f_size2': -1,
        'f_offset2': 0,
        'f_size3': 110592,
        'f_offset3': 106497,
        'f_size4': -1,
        'f_offset4': 0,
        'l_size': 32,
        'l_size2': 8,
    },
}


def run_cli(qdc_folder_path, output_path, layer, validity_codes, quite, x_correction, y_correction, z_correction,
            csv_delimiter, csv_skip_headers, csv_yxz, message_queue=None):
    # Patch tqdm to duplicate messages up to the passed message queue.
    if message_queue:
        patch_tqdm(tqdm, message_queue)

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

        x_size = (x_max - x_min + 1) * layer_parameters.l_size - 1
        y_size = (y_max - y_min + 1) * layer_parameters.l_size - 1
        arr_depth = np.zeros((x_size + 1, y_size + 1), dtype=np.int16)

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

        f_fix = lambda x: np.sign(x) * np.int16(np.abs(x))

        # Save depth array to *.csv or *.grd
        if output_path_ext.lower() == '.grd':
            # ESRI ASCII grid
            with open(output_path, 'w') as f_grd:
                f_grd.write(f'NCOLS {x_size + 1}\n')
                f_grd.write(f'NROWS {y_size + 1}\n')
                f_grd.write(f'XLLCORNER {x_orig}\n')
                f_grd.write(f'YLLCORNER {y_orig}\n')
                f_grd.write(f'CELLSIZE {layer_parameters.a_step}\n')
                f_grd.write('NODATA_VALUE 0\n')

                for j in tqdm(range(y_size, -1, -1), desc=_('Saving Esri ASCII raster')):
                    row_values = []
                    for i in range(x_size + 1):
                        if validity_codes:
                            t_val = f_fix(arr_depth[i, j] / 4096)
                            z = t_val * 10 + (arr_depth[i, j] - t_val * 4096) / 256
                        else:
                            z = arr_depth[i, j] / 100
                        row_values.append(z + z_correction)
                    f_grd.write(' '.join(str(x) for x in row_values) + '\n')

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
                for j in tqdm(range(y_size, -1, -1), desc=_('Saving CSV table'), disable=quite):
                    for i in range(x_size + 1):
                        if arr_depth[i, j] > 0:  # Skip all 0 values
                            if validity_codes:
                                t_val = f_fix(arr_depth[i, j] / 4096)
                                z = t_val * 10 + (arr_depth[i, j] - t_val * 4096) / 256
                            else:
                                z = arr_depth[i, j] / 100

                            # Adding a_step / 2 to move point to the middle of the cell extent
                            x = x_orig + layer_parameters.a_step / 2 + i * layer_parameters.a_step
                            y = y_orig + layer_parameters.a_step / 2 + j * layer_parameters.a_step

                            if csv_yxz:
                                writer.writerow([y + y_correction, x + x_correction, z + z_correction])
                            else:
                                writer.writerow([x + x_correction, y + y_correction, z + z_correction])

    except Exception as e:
        print_error(f'{_("Error")}: {e}', message_queue)
        raise
