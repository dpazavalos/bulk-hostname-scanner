from ._report_zengine import _ReporterEngine
from typing import List


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
        for i in range(0, len(target), self._sett.sngl_split_size):
            out.append(target[i:i + self._sett.sngl_split_size])
        return out

    @staticmethod
    def _report_divider(title: str) -> str:
        """Header lines used to visually break up report items. Std creator"""
        return '\r\n\r\n' + title.center(44, '=') + '\r\n\r\n'

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

        # Gen temp file
        temp_report = self._temporary_file(suffix='.txt', delete=False)

        # Split valid IPs into split size based on _sett.split_size
        self.valids_split = self._list_splitter(self._ips.valids)

        # Write valid IPs to rep_file
        # form valids split chunks into sett.report_joiner joined lines ( 10.10.10.2,10.10.10.3 )
        _valids_formed = [self._sett.sngl_report_joiner.join(valid) for valid in self.valids_split]
        valids_joined = '\r\n\r\n'.join(_valids_formed)
        temp_report.write(bytes(valids_joined, encoding='ascii'))

        # Any non resolved servers
        report_invalids = self._report_inval(self._ips.invalids)
        temp_report.write(bytes(report_invalids, encoding='ascii'))

        # Close connection to temp file. Send string path to threaded handler
        temp_report.close()
        self._file_handler(temp_report.name)
