import gettext
import importlib.util
import os
import sys
import warnings
from itertools import islice

try:
    import PySimpleGUI as sg
    GUI_ENABLED = True
    del sg
except ImportError as e:
    if e.name != 'PySimpleGUI':
        # GUI was installed, but failed to load
        # due to tkinter missing or other dependencies.
        warnings.warn('Failed to load GUI: %s' % e.msg)
    GUI_ENABLED = False


def print_error(error_msg, message_queue=None):
    """Print error message to `stderr` and dublicate it to
    `message_queue` if it's been passed.

    Args:
        error_msg (str): Error message.
        message_queue (multiprocessing.Queue): Message queue.
    """
    print(error_msg, file=sys.stderr)
    if message_queue:
        # Send error message up to the message queue
        message_queue.put(('#Error', error_msg))


def data_path():
    """Returns data path."""
    if '_MEIPASS2' in os.environ:
        here = os.environ['_MEIPASS2']
    else:
        here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, 'data')


def image_path(image_name):
    """Get package's data path.

    Args:
        image_name (str): Image basename.

    Returns:
        Image full path.
    """
    return os.path.join(data_path(), 'images', image_name)


def patch_tqdm(tqdm, message_queue):
    """Patch tqdm to make it dublicate progress to `message_queue`.

    Args:
        tqdm (tqdm.tqdm) Tqdm class to be patched.
        message_queue (multiprocessing.Queue): Message queue.
    """
    original_update = tqdm.update
    original_close = tqdm.close
    original_init = tqdm.__init__

    def new_update(tqdm_self, *args, **kwargs):
        original_update(tqdm_self, *args, **kwargs)
        message_queue.put(('#UpdateProgressBar', (tqdm_self.n, tqdm_self.total)))

    def new_close(tqdm_self, *args, **kwargs):
        message_queue.put(('#UpdateProgressBar', (tqdm_self.n, tqdm_self.total)))
        original_close(tqdm_self, *args, **kwargs)

    def new_init(tqdm_self, *args, **kwargs):
        original_init(tqdm_self, *args, **kwargs)
        message_queue.put(('#UpdateProgressBarTitle', tqdm_self.desc))
        message_queue.put(('#UpdateProgressBar', (tqdm_self.n, tqdm_self.total)))

    tqdm.update = new_update
    tqdm.close = new_close
    tqdm.__init__ = new_init


def get_files_recursively(root_path, exts):
    """Recursively search for files with the extension
    specified in `exts`.

    Args:
        root_path (str): Root path.
        exts (str): Files extension.

    Returns:
        List of found files.
    """
    if type(exts) not in (list, tuple):
        exts = (exts,)
    result = []
    files = [os.path.join(dp, f) for dp, _, fn in os.walk(root_path) for f in fn]
    for f in files:
        if any(f.endswith(ext) for ext in exts):
            full_path_f = os.path.join(root_path, f)
            result.append(full_path_f)
    return result


def install_i18n():
    """Install i18n."""
    locale_dir = os.path.join(data_path(), 'locale')
    if not os.path.isdir(locale_dir):
        # find locale in module path
        qdc_converter_module = importlib.util.find_spec('qdc-converter')
        if qdc_converter_module:
            for path in qdc_converter_module.submodule_search_locations:
                locale_path = os.path.join(path, 'data', 'locale')
                if os.path.exists(locale_path):
                    locale_dir = locale_path

    gettext.install('messages', locale_dir)


def chunks(iterable, n):
    """Split iterable in batches."""
    it_len = len(iterable)
    for ndx in range(0, it_len, n):
        yield iterable[ndx:min(ndx + n, it_len)]


def window(iterable, n=2, with_trailing=True):
    """Returns a sliding window.

    Example:
        list(window([1, 2, 3, 4, 5], 3))
        =>
        [(1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5), (5,)]
    """
    it = iter(iterable)
    result = tuple(islice(it, n))
    if len(result) <= n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result
    if with_trailing:
        result = result[1:]
        while result:
            yield result
            result = result[1:]
