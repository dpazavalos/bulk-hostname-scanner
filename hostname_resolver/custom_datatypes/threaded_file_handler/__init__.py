"""
Multi Thread file opener and cleanup
Best used with temp files
"""

from webbrowser import open as _wb_open
from os import remove as _os_remove
from time import sleep as _sleep
from threading import Thread as _Thread


class TFH:
    """
    Multi Thread file opener and cleanup
    Best used with temp files
    """

    @staticmethod
    def _threaded_file_handler(temp_file: str):
        # use webbrowser.open to call default text editor (no OS reliance)
        _wb_open(temp_file)

        # Because file pipes through browser, it can take time a moment before actually open
        _sleep(5)

        # Temp file is open. Delete it once user is through
        file_is_open = True
        while file_is_open:
            try:
                _os_remove(temp_file)
                file_is_open = False
            except PermissionError:
                # Being used. Wait
                pass
            except FileNotFoundError:
                file_is_open = False

    def handle(self, file_path: str):
        """File handler. Threads dedicated file handler to open and cleanup file \n
        Call and forget

        Args:
            file_path: string path to file
        """
        opener = _Thread(target=self._threaded_file_handler, args=(file_path,))
        opener.start()
