"""
Internal hostname resolver

Given a list of host names, attempts to get IPs against a set list of TLDs \n
Splits Valids list into list max length split_size=30 (useful for scan limits) \n
If server is given without tld, tests and find appropriate TLD from list of known TLDs \n
NOTE: Long server lists without TLDs WILL take time \n

This module was originally written for use internally in large corporate domains, where a user may
encounter a list of server names without their internal TLDs, and need to figure the IP addresses
for a scan. Once hostname IPs are found, results are either \n \n

Additionally, HostnameToIP(hostnames_in=None) can be given a list to automatically scan out for.\n
Note: doing so sets text_out=False, return_list=True, and show_status=False, meaning the script will
run once silently and return the tuples. Use for module integration \n
hostnames_in can be set either in __init__ or run(), however passing through run keeps those
attributes changed.
"""
# todo move to readme.md
# todo reduce options. Change verbosity to single silent running, default False

from socket import gethostbyname as sock_ghbn, gaierror as sock_gaierror, \
    herror as sock_herror
from webbrowser import open as wb_open
from textwrap import dedent
from os import remove as os_remove
from typing import List, Tuple, Optional, Type
from sys import argv as sys_argv
import reference_data as ref


# todo relocate imports and documentaion to adjacent documentation file


class HostnameToIP:
    """Translates hostnames to IP's (valids for found, invalids for not)\n
chunk_size breaks up list of valids into necessary sized lines as needed (useful for scan limts)
If server is given without tld, tests and find appropriate TLD from list of known TLDs\n
NOTE: Long server lists without TLDs WILL take time\n

(If a list of hostnames to check already exists, provide as attribute hostnames_in)"""

    def __init__(self, ):

        self._sett = ref.build.new_settings_object()
        """Running settings object"""
        self._const = ref.build.new_const_object()
        """Immutable reference data; contact info, known TLDs, known exclusions"""
        self._ips: ref.IpReport = ref.build.new_ip_report_obj()
        """Storage for valids, invalids, and valids_split values"""

        self._repeating: bool = True
        """Used to keep run loop running, typically in conjunction with text_out"""

    def _verprint(self, *to_print):
        """
        Default check against _sett.verbosity to see if allowed to print

        Args:
            *to_print: emulation of print *args. pass as normal
        """
        if self._sett.verbose:
            for arg in to_print:
                print(arg, end=' ')
            print()

    def _clear_ips(self) -> None:
        """Call IPS_report clear function"""
        self._ips.reset()

    @staticmethod
    def _hn_in_breakdown(targ) -> List[str]:
        """Check hn_in entries for if possible file, passed list, or single string.
        Break down into array and return

        Args:
            targ: hn_in item

        Return:
            Array, from singular item to full breakdown"""
        arr = []
        if isinstance(targ, list):
            arr += [x for x in targ]
        else:
            try:
                with open(targ) as fi:
                    for line in fi:
                        try:
                            line = str(line)
                            arr.append(line.strip())
                        except ValueError:
                            pass
            except FileNotFoundError:
                arr.append(targ)
        return arr

    def _process_hostnames_given(self, hn_in: List[str]) -> bool:
        """Checks if a list of hostnames was given to the module\n
        Hostnames can be passed when calling run

        Args:
            hn_in: an optional hostnames in argument from run()

        Return:
            TF bool, indicating if a list of hostnames was given"""

        # Check if hostnames passed through in run()
        if hn_in:
            # for hostname in hn_in:
            self._ips.hostnames_in += self._hn_in_breakdown(hn_in)
            return True

        # Check if hostnames passed through in sys_argv
        elif len(sys_argv) > 1:
            for ndx in range(1, len(sys_argv)):
                self._ips.hostnames_in += self._hn_in_breakdown(sys_argv[ndx])
            return True

        return False

    def _splash_screen(self) -> None:
        """Print welcome screen (w/ verbosity check)"""

        self._verprint(dedent("""
            * * AdHoc Server Name Resolver * *

        Identifies IPs for a list of given servers, based on internal TLDs

        Enter manually or copy/paste a column of server names separated by new lines
        Text file will open with lines of IPs for servers, no more than 30 IPs per line
        Note: while full domains are optional, a large list without them WILL take time
        
        """))

    def _gather(self) -> None:
        """Gathers server names from user, split by newline\n
        Runs until blank line submitted
        Defauts to pass if self.hostnames_in is set"""

        # Note: hostnames_in clears on after first run (_ips.reset()
        if not self._ips.hostnames_in:
            prompt: str = None
            self._verprint("\nEnter servers (Leave blank to start scan)\n")
            prev_gathered = [prev.given for prev in self._ips.socket_answers]
            while prompt != '':
                prompt = input('> ').lower().strip()
                if prompt and prompt not in self._ips.hostnames_in and \
                        prompt not in prev_gathered and \
                        prompt not in self._const.known_exclusions:
                    self._ips.hostnames_in.append(prompt)

    @staticmethod
    def _dns_assumed(hostname: str, tld: str) -> bool:
        """Determines if DNS assumed the domain.TLD. on an unqualified hostname"""
        return ('.' not in hostname) and (not tld)

    def _socketer(self, hostname: str) -> Tuple[str, str]:
        """Extention to socket.gethostbyaddr, includes iterative check against known tld's
        Returns given hostname's FQDN and IP\n
        If unable to resolve, returns none"""

        for top in self._const.tlds:
            name = hostname + top
            try:
                ip = sock_ghbn(name)
                if self._dns_assumed(hostname, top):
                    name += self._const.local_tld
                return name, ip
            except (sock_gaierror, sock_herror, UnicodeError):
                # most errors are attributed to mismatched hostname to tld. Iterate to next one
                pass
        # Looks like IP was never found. Raise ValueError
        raise ValueError("Socketer unable to resolve given!")

    @staticmethod
    def _tmat(*to_display: any) -> str:
        """returns values in standardized table format, used to stdout results"""

        # Make sure all items to display are unpacked
        disp_arr = []
        for item in to_display:
            if isinstance(item, list):
                disp_arr += [str(i) for i in item]
            else:
                disp_arr.append(str(item))

        gap_start = 7
        gapper = gap_start
        tbl = ''
        for item in disp_arr:
            if gapper == gap_start:
                tbl += item.rjust(gapper)
            else:
                tbl += item.ljust(gapper)
            tbl += ' '
            gapper += 10

        return tbl

    def _split_list(self, target: list) -> List[List[str]]:
        """Splits given list into nested lists based on self.chunk_size as range step"""
        out: List[list] = []
        for i in range(0, len(target), self._sett.split_size):
            out.append(target[i:i + self._sett.split_size])
        return out

    def _sort(self) -> None:
        """
        Sorts hostnames from hostnames_in to valid and invalid lists based on _socketer results\n
        """

        # stdout Header
        count = len(self._ips.hostnames_in) + len(self._ips.socket_answers)
        self._verprint('\n\t*', count, 'unique servers identified *\n')
        self._verprint(self._tmat('#', 'Given', 'FQDN', "IP"))

        num = 1
        """Line counter, for all stdout items"""

        # Pull stored givens, if any. Allows 'adding' hostnames without explicitly saving table
        for prev in self._ips.socket_answers:
            self._ips.valids.append(prev.ip)
            self._verprint(self._tmat(num, [p for p in prev]))
            num += 1

        # enumerate through hostnames_in. Gather name and IP.
        not_found = 'N / A'  # To display, if unable to resolve
        for given in self._ips.hostnames_in:
            fqdn, ip = not_found, not_found
            try:
                fqdn, ip = self._socketer(given)
                self._ips.valids.append(ip)
            except ValueError:
                self._ips.invalids.append(given)
            finally:
                self._verprint(self._tmat(num, given, fqdn, ip))
                self._ips.socket_answers.append(self._ips.sock_ans(given, fqdn, ip))
                num += 1

        self._ips.valids_split = self._split_list(self._ips.valids)

    # # # Reporter functions

    @staticmethod
    def _report_divider(title: str) -> str:
        """Header lines used to visually break up report items. Std creator"""
        return '\n\n' + title.center(44, '=') + '\n\n'

    def _report_inval(self, invalids_remaining: List[str]) -> str:
        """Generate an Invalids Report, given a list of invalid results.
        Can be given a blank list, to indicate no invalid results"""

        rep: str = ''

        rep += self._report_divider("Contacts")
        rep += self._const.contacts

        # Build rep if any unidentified servers
        if invalids_remaining:
            rep += self._report_divider('Servers with no found IP')
            rep += '\n'.join(i for i in invalids_remaining)
        else:
            return rep

    # # # Primary engine functions

    def _report(self) -> None:
        """Cultivates text report from self.valids and self.invalids"""

        # Write valid IPs to rep_file
        # form valids split chunks into sett.report_joiner joined lines ( 10.10.10.2,10.10.10.3 )
        valids_formed = [self._sett.report_joiner.join(valid) for valid in self._ips.valids_split]
        with open(self._const.rep_file, 'w') as report:
            report.write('\n\n'.join(valids_formed))

        # Any non resolved servers
        with open(self._const.rep_file, 'a') as report:
            report.write(self._report_inval(self._ips.invalids))

        # use webbrowser.open to call default text editor (no OS reliance)
        wb_open(self._const.rep_file)

    def _menu_prompt(self) -> None:
        """Sets self.repeating T/F flag"""

        prompts = '0 1 2 3'.split()
        menu = '\n(0) Quit '\
               '\n(1) Run a new list '\
               '\n(2) Add to list'\
               '\n(3) Generate Report'

        menuing = True
        while menuing:
            menuing = False

            self._verprint(menu)
            prompt = None
            while prompt not in prompts:
                prompt = input('> ')

                # Exit run loop
                if prompt == '0':
                    self._repeating = False
                    os_remove(self._const.rep_file)  # todo replace with temp file

                # Clear list
                elif prompt == '1':
                    self._ips.reset_all()   # Clear ALL ips data

                elif prompt == '2':
                    self._ips.reset()       # Keep previous socket answers

                elif prompt == '3':
                    menuing = True
                    self._report()

    def run(self,
            hostnames_in: List[str] = None,
            *,
            verbose=True,
            split_size=30,
            report_joiner=',',
            # file_out=False,
            # return_list=False,
            ) -> Optional[Tuple[List[List[str]], List[str]]]:
        """Display _splash screen, _gather IPs (hostnames_in= or stdin), opt report, return list"""

        # Set running settings
        self._sett.set_settings(split_size=split_size,
                                report_joiner=report_joiner,
                                # file_out=file_out,
                                # return_list=return_list,
                                verbose=verbose
                                )

        """Variant of verbosity. Used when given hostnames in sys.argv or run()"""
        if self._process_hostnames_given(hostnames_in):
            pass
            # silent running. A list given through run or sys.argv reduces verbosity
        else:
            self._splash_screen()

        while self._repeating:
            self._gather()
            self._sort()
            self._menu_prompt()

        return self._ips.valids_split, self._ips.invalids


if __name__ == '__main__':
    HN2IP = HostnameToIP()
    HN2IP.run()
