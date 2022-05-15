import base64
import multiprocessing as mp
import os
import threading

import PySimpleGUI as sg

from .cli import run_cli
from .utils import get_files_recursively, image_path


def run_gui(qdc_folder_path, output_path, layer, validity_codes, quite, x_correction,
            y_correction, z_correction, csv_delimiter, csv_skip_headers, csv_yxz):
    """Run GUI with same passed arguments as CLI."""
    sg.theme('SandyBeach')

    # Work with local variables through `args`
    args = locals().copy()

    # Set icon
    with open(image_path('icon.png'), 'rb') as f:
        sg.set_global_icon(base64.b64encode(f.read()))

    # Window's text, labels
    app_description = _('QDC Converter.\n\nConverter of Garmin\'s QDC files into CSV or GRD.')
    window_title, window_description = app_description.split('\n\n')

    t = lambda title, tail='': title[:-1] + tail
    input_dir_title = t(_('Path to folder with QuickDraw Contours (QDC) inside.'), tail=':')
    output_file_title = t(_('Path to the result file (*.csv or *.grd).'), tail=':')
    layer_title = t(_('Data layer (0 - Raw user data, 1 - Recommended).'), tail=':')
    validity_codes_title = t(_('Write validity code instead of depth.'))
    csv_skip_headers_title = t(_('Do not write header.'))
    csv_yxz_title = t(_('Change column order from X,Y,Z to Y,X,Z.'),)
    window_description = t(window_description)
    window_title = t(window_title)

    # Window's layout
    layout = [
        [
            sg.Text(window_description, font='Any 15')
        ],
        [
            sg.Frame('', expand_x=True, layout=[
                [
                    sg.Text(input_dir_title),
                ],
                [
                    sg.Input(qdc_folder_path, key='@qdc_folder_path', expand_x=True),
                    sg.FolderBrowse(_('Browse')),
                ],
            ])
        ],
        [
            sg.Frame('', expand_x=True, layout=[
                [
                    sg.Text(output_file_title),
                ],
                [
                    sg.Input(output_path, key='@output_path', expand_x=True),
                    sg.FileSaveAs(_('Browse'), file_types=(('CSV Table', '*.csv'), ('ESRI ASCII grid', '*.grd')))
                ],
            ]),
        ],
        [
            sg.Frame(_('Options'), expand_x=True, layout=[
                [
                    sg.Text(layer_title),
                    sg.Combo(key='@layer', default_value=1 if layer is None else layer,
                             size=(3, 1), values=(0, 1, 2, 3, 4, 5), readonly=True),
                ],
                [
                    sg.Checkbox(validity_codes_title, key='@validity_codes', default=validity_codes),
                ],
            ]),
        ],
        [
            sg.Frame('CSV', expand_x=True, layout=[
                [
                    sg.Checkbox(csv_skip_headers_title, key='@csv_skip_headers', default=csv_skip_headers),
                ],
                [
                    sg.Checkbox(csv_yxz_title, key='@csv_yxz', default=csv_yxz),
                ],
            ]),
        ],
        [
            sg.ProgressBar(0, orientation='h', size=(1, 22), expand_x=True, key='-ProgressBar-', pad=(5, 10))
        ],
        [
            sg.Column([[
                sg.Button(_('Convert'), key='-Convert-'),
                sg.Button(_('Cancel'), key='-Cancel-', button_color=('white', 'orange3'), visible=False),
            ]], pad=0),
            sg.Button(_('Quit'), key='-Quit-', button_color=('white', 'firebrick3')),
        ],
    ]

    # Main window
    window = sg.Window(window_title, layout, auto_size_text=True, auto_size_buttons=False,
                       default_element_size=(20, 1), text_justification='right', font='Any 12')

    # Process
    converter_process = None
    converter_process_running = lambda: converter_process and converter_process.is_alive()

    # Window elements
    cancel_button = window['-Cancel-']
    convert_button = window['-Convert-']
    progress_bar = window['-ProgressBar-']

    # IPC message queue
    message_queue = mp.Queue()

    # Create bridge between MP message queue and SG message queue
    def message_queue_bridge():
        # Perform message resend from subprocess
        # message queue to parent GUI message queue.
        while True:
            key, value = message_queue.get()
            window.write_event_value(key, value)

    message_bridge_thread = threading.Thread(target=message_queue_bridge, daemon=True)
    message_bridge_thread.start()

    # Add message queue to args
    args['message_queue'] = message_queue

    def swap_buttons(state):
        if state:
            cancel_button.update(visible=True)
            convert_button.update(visible=False)
        else:
            cancel_button.update(visible=False)
            convert_button.update(visible=True)

    # Main event loop
    while True:
        event, values = window.read()

        if event in ('-Quit-', None):
            if converter_process_running():
                converter_process.terminate()
                converter_process.join()
            break

        elif event == '#Error':
            sg.PopupError(values['#Error'], title=_('Error'), font='Any 12')

        elif event == '#UpdateProgressBar':
            current_value, max_value = values['#UpdateProgressBar']
            progress_bar.update(current_count=current_value, max=max_value)

        elif event == '-Cancel-':
            if converter_process_running():
                converter_process.terminate()

        elif event == '-Convert-':
            # Update arguments
            for name, value in values.items():
                if name.startswith('@'):
                    args[name[1:]] = value

            # Validate input path exists
            if not os.path.isdir(args['qdc_folder_path']):
                sg.PopupError(_('Input path is not a folder!'), title=_('Error'), font='Any 12')
                continue

            # Validate input path contains *.qdc files
            qdc_files = get_files_recursively(args['qdc_folder_path'], '.qdc')
            if not qdc_files:
                sg.PopupError(_('No *.qdc files found inside input path!'), title=_('Error'), font='Any 12')
                continue

            # Validate output path
            output_ext = os.path.splitext(args['output_path'])[1].lower()
            if not any(output_ext == ext for ext in ('.csv', '.grd')):
                sg.PopupError(_('Output file extension must be *.csv (CSV table) or *.grd (ESRI ASCII grid)'),
                              title=_('Error'), font='Any 12')
                continue

            # Swap Conver/Cancel buttons
            swap_buttons(True)

            # Run converter process
            converter_process = mp.Process(target=run_cli, kwargs=args, daemon=True)
            converter_process.start()

            # Restore buttons state on process finished
            def restore_buttons():
                converter_process.join()
                swap_buttons(False)

            threading.Thread(target=restore_buttons, daemon=True).start()

    window.Close()
