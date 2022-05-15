import multiprocessing as mp

import click
from click_option_group import optgroup

from .cli import run_cli
from .utils import GUI_ENABLED, install_i18n
from .version import version

if GUI_ENABLED:
    from .gui import run_gui


# Install localization
install_i18n()

# Add multiprocessing support on Windows for Pyinstaller's builds.
mp.freeze_support()


@click.version_option(version=version)
@click.command(help=_('QDC Converter.\n\nConverter of Garmin\'s QDC files into CSV or GRD.'))
@optgroup.group(_('Main parameters'), help=_('Key parameters of the converter'))
@optgroup.option('--qdc-folder-path', '-i', required=not(GUI_ENABLED),
                 type=click.Path(exists=True, resolve_path=True, file_okay=False, dir_okay=True),
                 help=_('Path to folder with QuickDraw Contours (QDC) inside.'))
@optgroup.option('--output-path', '-o', required=not(GUI_ENABLED),
                 type=click.Path(exists=False, resolve_path=True, file_okay=True, dir_okay=False),
                 help=_('Path to the result file (*.csv or *.grd).'))
@optgroup.option('--layer', '-l', required=not(GUI_ENABLED),
                 type=click.IntRange(0, 5), metavar='[0,1,2,3,4,5]',
                 help=_('Data layer (0 - Raw user data, 1 - Recommended).'))
@optgroup.option('--validity-codes', '-vc', is_flag=True, help=_('Write validity code instead of depth.'))
@optgroup.option('--quite', '-q', is_flag=True, help=_('"Quite mode"'))
@optgroup.group(_('Correction parameters'), help=_('Corrections'))
@optgroup.option('--x-correction', '-dx', type=click.FLOAT, default=0.0, help=_('Correction of X.'))
@optgroup.option('--y-correction', '-dy', type=click.FLOAT, default=0.0, help=_('Correction of Y.'))
@optgroup.option('--z-correction', '-dz', type=click.FLOAT, default=0.0, help=_('Correction of Z.'))
@optgroup.group(_('CSV parameters'), help=_('Parameters related to CSV'))
@optgroup.option('--csv-delimiter', '-csvd', type=click.STRING, default=',', help=_('CSV delimiter (default ",").'))
@optgroup.option('--csv-skip-headers', '-csvs', is_flag=True, help=_('Do not write header.'))
@optgroup.option('--csv-yxz', '-csvy', is_flag=True, help=_('Change column order from X,Y,Z to Y,X,Z.'))
def main(qdc_folder_path, output_path, layer, validity_codes, quite, x_correction, y_correction, z_correction,
         csv_delimiter, csv_skip_headers, csv_yxz):
    if qdc_folder_path is None or output_path is None or layer is None:
        assert GUI_ENABLED
        return run_gui(qdc_folder_path, output_path, layer, validity_codes, quite, x_correction, y_correction,
                       z_correction, csv_delimiter, csv_skip_headers, csv_yxz)

    else:
        return run_cli(qdc_folder_path, output_path, layer, validity_codes, quite, x_correction, y_correction,
                       z_correction, csv_delimiter, csv_skip_headers, csv_yxz)
