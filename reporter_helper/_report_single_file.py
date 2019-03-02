from ._report_zengine import _ReporterEngine
from typing import List
from tempfile import mkstemp, TemporaryFile
from threading import Thread
from os import remove as os_remove
from time import sleep


class _SingleFile(_ReporterEngine):
    """
    Used to export findings to single plaintext report. Uses constants information to fill report
    (Most commonly used to send information to internal scan portals. Adj as needed)
    """

    valids_split: List[List[str]] = []
    """IPs of valid Hostnames, split into sublists by self.split_size"""

    def _list_splitter(self, target: list) -> List[List[str]]:
        """Splits given list into nested lists based on self.chunk_size as range step"""
        out: List[list] = []
        for i in range(0, len(target), self._sett.split_size):
            out.append(target[i:i + self._sett.split_size])
        return out

    @staticmethod
    def _report_divider(title: str) -> str:
        """Header lines used to visually break up report items. Std creator"""
        return '\r\n\r\n' + title.center(44, '=') + '\r\n\r\n'

    # # # Primary engine functions

    def _temp_file_handler(self, temp_file: str):
        """temp file handler. Thread and spool to open temp file.
        Deletes file once user has closed it"""

        # use webbrowser.open to call default text editor (no OS reliance)
        self._wb_open(temp_file)
        file_is_open = True

        # Webbrowser open is used to avoid determining a user's default text editer
        # Because the file must pipe, it can take time before it is actually open
        sleep(5)

        # Wait till temp file is open
        '''while not file_is_open:
            try:
                with open(temp_file, 'w'):
                    print("waiting for open")
                    pass
            except PermissionError:
                file_is_open = True'''

        # Temp file is open. Delete it once user is through
        while file_is_open:
            try:
                os_remove(temp_file)
                file_is_open = False
            except PermissionError:
                print("waiting for Close")
                pass

    def _report_inval(self, invalids_remaining: [str], ) -> str:
        """Generate an Invalids Report, given a list of invalid results.
        Can be given a blank list, to indicate no invalid results"""

        rep: str = ''

        rep += self._report_divider("Contacts")
        rep += self._const.contacts

        # Build rep if any unidentified servers
        if invalids_remaining:
            rep += self._report_divider('Servers with no found IP')
            rep += '\r\n'.join(i for i in invalids_remaining)
        else:
            rep += self._report_divider('All Servers identified')

        return rep

    def report(self) -> None:
        """Cultivates text report from self.valids and self.invalids"""

        # Split valid IPs into split size based on _sett.split_size
        self.valids_split = self._list_splitter(self._ips.valids)

        temp_report = TemporaryFile(suffix='.txt', delete=False)
        # temp_report = mkstemp(suffix='.txt', text=True)[1]

        # Write valid IPs to rep_file
        # form valids split chunks into sett.report_joiner joined lines ( 10.10.10.2,10.10.10.3 )
        valids_formed = [self._sett.report_joiner.join(valid) for valid in self.valids_split]
        valids_joined = '\r\n\r\n'.join(valids_formed)
        '''with open(temp_report.name, 'w') as report:
            report.write('\n\n'.join(valids_formed))'''
        temp_report.write(bytes(valids_joined, encoding='ascii'))
        # temp_report.write(b'\r\n\r\n')

        # Any non resolved servers
        '''with open(temp_report.name, 'a') as report:
            report.write(self._report_inval(self._ips.invalids))'''
        report_invalids = self._report_inval(self._ips.invalids)
        temp_report.write(bytes(report_invalids, encoding='ascii'))

        temp_report.close()
        opener = Thread(target=self._temp_file_handler, args=(temp_report.name, ))
        opener.start()
        # os_remove(temp_report.name)
