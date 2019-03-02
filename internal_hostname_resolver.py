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
from textwrap import dedent
from typing import List, Tuple, Optional
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
        self._reporter = None
        """Pointer to _reporter_caller helper options. Built when needed"""

        self._repeating: bool = True
        """Used to keep run loop running, typically in conjunction with text_out"""

    def _verprint(self, *to_print) -> None:
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
            targ: Either a single item, list of items, or stringpath to file containing
                  items (Line separated)

        Return:
            List of item(s) in targ"""
        arr = []
        # Try list unpacking
        if isinstance(targ, list):
            arr += [x for x in targ]

        # Try following it as a file name (best for argv entries)
        else:
            try:
                with open(targ) as fi:
                    for line in fi:
                        try:
                            line = str(line)
                            arr.append(line.strip())
                        except ValueError:
                            pass

            # Give up, assume it's a hostname to check
            except FileNotFoundError:
                arr.append(targ)
        return arr

    def _process_hostnames_given(self, hn_in: List[str]) -> bool:
        """
        Checks if a list of hostnames was given to the module\n
        Hostnames can be passed when calling run

        Args:
            hn_in: an optional hostnames in argument from run()

        Return:
            TF bool, indicating if a list of hostnames was given
        """

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
        """))

    def _gather(self) -> None:
        """
        Verbosity print basic instructions.
        Gather server names from user, split by newline
        Runs until blank line submitted
        Defaults to pass if self.hostnames_in is set (hostnames_in clears on subsequent runs)
        """

        if not self._ips.hostnames_in:

            self._verprint(dedent("""        
            Enter manually or copy/paste a column of server names separated by new lines
            Enter a blank line to start scan
            Note: while full domains are optional, a large list without them WILL take time
            """))

            prompt: str = None
            prev_gathered = [prev.given for prev in self._ips.socket_answers]
            while prompt != '':
                prompt = input('> ').lower().strip()
                if prompt and prompt not in self._ips.hostnames_in and \
                        prompt not in prev_gathered and \
                        prompt not in self._const.known_exclusions:
                    self._ips.hostnames_in.append(prompt)

    def _tld_assumed(self, hostname: str, tld: str) -> bool:
        """
        Determines if DNS assumed the domain.TLD. on an unqualified hostname
        """
        assumed = ('.' not in hostname) and (not tld)

        # local tld is only needed when assumed. On first instance, find it
        if assumed and self._const.local_tld is None:
            self._const.find_local_tld()
        return assumed

    @staticmethod
    def _tmat(*to_display: any) -> str:
        """
        returns values in standardized table format, used to stdout results
        """

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
        for ndx, item in enumerate(disp_arr):

            if ndx == 0:
                tbl += item.rjust(gapper)
            else:
                tbl += item.ljust(gapper)

            tbl += ' '
            gapper += 10

        return tbl

    def _ghbn_ext(self, hostname: str) -> Tuple[str, str]:
        """
        Extention to socket.gethostbyname, includes iterative check against known tld's
        Returns given hostname's FQDN and IP\n
        If unable to resolve, raises ValueError

        Args:
            hostname: Individual hostname to check. Prefer FQDN, but hostname only is acceptable
                (Ensure TlDs contains all needed)

        Returns:
            (Name used to get IP, Actual IP)
        """

        for top in self._const.tlds:
            name = hostname + top
            try:
                ip = sock_ghbn(name)
                if self._tld_assumed(hostname, top):
                    name += self._const.local_tld
                return name, ip
            except (sock_gaierror, UnicodeError):
                # most errors are attributed to mismatched hostname to tld. Iterate to next TLD
                pass
        # Looks like IP was never found. Raise ValueError
        raise ValueError("Socketer unable to resolve given!")

    def _resolve(self) -> None:
        """
        Resolves hostnames from hostnames_in fqdn and IP, using socket extention. Stores answers in
        socket_answers, sorts Ips into valids and invalids
        """

        # stdout Header
        count = len(self._ips.hostnames_in) + len(self._ips.socket_answers)
        self._verprint('\n\t*', count, 'unique servers identified *\n')
        self._verprint(self._tmat('#', 'Given', 'FQDN', "IP"))

        num = 1
        """Line counter. Counts previous answers AND new resolves"""

        # Pull stored givens, if any. Allows 'adding' hostnames without explicitly saving table
        for prev in self._ips.socket_answers:
            self._ips.valids.append(prev.ip)
            self._verprint(self._tmat(num, [p for p in prev]))
            num += 1

        # Iterate through hostnames_in. Gather name and IP.
        not_found = 'N / A'  # To display, if unable to resolve
        for given in self._ips.hostnames_in:

            # Set defaults
            fqdn, ip = not_found, not_found

            try:
                fqdn, ip = self._ghbn_ext(given)
                self._ips.valids.append(ip)

            except ValueError:
                # Raised by _ghbn_ext if unable to resolve. Consider invalid hostname
                self._ips.invalids.append(given)

            finally:
                # Verbose print out progress
                self._verprint(self._tmat(num, given, fqdn, ip))
                self._ips.socket_answers.append(self._ips.sock_ans(given, fqdn, ip))
                num += 1

    # # # Reporter functions

    def _reporter_caller(self, rep_type: str):
        """
        Manages reporting functions

        Args:
            rep_type: ['csv', 'single']  used to call appropriate reporting function
        """

        if rep_type not in ['csv', 'single']:
            raise KeyError("Invalid argument passed to repoter caller!")

        # Import report module. Build _reporter pointer on first demand
        import reporter_helper as rep
        if not self._reporter:
            self._reporter = rep.build.new_reporter_obj(constants=self._const,
                                                        settings=self._sett,
                                                        ip_report=self._ips)
        if rep_type is 'single':
            self._reporter.report_single()
        elif rep_type is 'csv':
            self._reporter.reporter_csv()

    def _menu_prompt(self) -> None:
        """Sets self.repeating T/F flag"""

        prompts = '0 1 2 3 4'.split()
        menu = '\n(0) Quit '\
               '\n(1) Run a new list '\
               '\n(2) Add to list'\
               '\n(3) Generate CSV Report' \
               '\n(4) Generate Single Page Report'

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

                # Clear list
                elif prompt == '1':
                    # Clear ALL ips data to run fresh
                    self._ips.reset_all()

                elif prompt == '2':
                    # Keep previous socket answers to add to
                    self._ips.reset()

                elif prompt == '3':
                    # Gen CSV Report
                    menuing = True
                    self._reporter_caller('csv')

                elif prompt == '4':
                    # Gen Single file report
                    menuing=True
                    self._reporter_caller('single')

    def run(self,
            hostnames_in: List[str] = None,
            *,
            verbose=True,
            split_size=30,
            report_joiner=',',
            ) -> Optional[Tuple[List[str], List[str]]]:
        """Display _splash screen, _gather IPs (hostnames_in= or stdin), opt report, return list"""

        # Set running settings
        self._sett.set_settings(split_size=split_size,
                                report_joiner=report_joiner,
                                verbose=verbose
                                )

        """Variant of verbosity. Used when given hostnames in sys.argv or run()"""

        # Try to process any argv or run(hostnames_in) arguments.
        self._process_hostnames_given(hostnames_in)

        # If hostnames weren't passed, greet user.
        if not self._ips.hostnames_in:
            self._splash_screen()

        while self._repeating:
            self._gather()      # Note: if hostnames were given, gather does nothing for first run
            self._resolve()  #
            self._menu_prompt()

        # try:
        #     os_remove(self._const.rep_file)  # todo replace with temp file
        # except FileNotFoundError:
        #     pass
        return self._ips.valids, self._ips.invalids


if __name__ == '__main__':
    HN2IP = HostnameToIP()
    HN2IP.run()
