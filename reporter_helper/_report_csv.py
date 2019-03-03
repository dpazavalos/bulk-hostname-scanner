from ._report_zengine import _ReporterEngine


class _SingleCsv(_ReporterEngine):
    """
    Used to export findings to csv report
    """

    temp_report: any  # TemporaryFile pointer. Assigned in report, used in _write_to_csv

    def _write_to_csv(self, row_to_write: tuple):
        row = ','.join(item for item in row_to_write)
        self.temp_report.write(bytes(row, encoding='utf-8'))
        self.temp_report.write(b'\r\n')

    def _sorted_write(self):
        """
        Writes socket answers to CSv, sorted by validity
        """
        from operator import itemgetter

        # Sort through socket answers. Write found, set not_found aside for now
        valids = []
        invalids = []
        for answer in self._ips.socket_answers:
            ans_vals = answer.values()
            if self._ips.not_found in ans_vals:
                invalids.append(ans_vals)
            else:
                valids.append(ans_vals)

        # Sort entries, by given values
        valids = sorted(valids, key=itemgetter(0))
        invalids = sorted(invalids, key=itemgetter(0))

        for valid in sorted(valids, key=itemgetter(0)):
            self._write_to_csv(valid)

        # Write blank row as simple separator
        self._write_to_csv((' ', ' ', ' '))

        for invalid in sorted(invalids, key=itemgetter(0)):
            self._write_to_csv(invalid)

        # Write invalids to csv
        for row in invalids:
            self._write_to_csv(row)

    def _unsorted_write(self):
        """
        Writes socket answers to CSV, sorted as gathered
        """
        # Just write everything to it
        for answer in self._ips.socket_answers:
            self._write_to_csv(answer.values())

    def report(self, sort_csv: bool):
        """Cultivates csv report from socket answers"""

        self.temp_report = self._temporary_file(suffix='.csv', delete=False)

        # Write header
        self._write_to_csv(self._ips.sock_ans.keys())

        # Decide which socket_answer parser to use
        if sort_csv:
            self._sorted_write()
        else:
            self._unsorted_write()

        # Close bind to temp_report, send to fild handler
        self.temp_report.close()
        self._file_handler(self.temp_report.name)
