"""
A bulk hostname resolver, designed to get info on a large number of internal hostnames against
internal TLDs.
"""

from socket import gethostbyname as sock_ghbn, gaierror as sock_gaierror
from textwrap import dedent
from typing import List, Tuple
from sys import argv as sys_argv
from hostname_resolver import reference_data as ref


class HostnameResolver:
    """Given a list of hostnames (either stdin, or passed list through run()) , finds IP addresses,
    TLD type if none given, displays on screen, and allows for csv reporting and customizable single
    file reporting.
    NOTE: Long server lists without TLDs WILL take time
    """

    def __init__(self, ):

        self._sett: ref.Settings = ref.build.new_settings_object()
        """Running settings object"""
        self._const: ref.Constants = ref.build.new_const_object()
        """Immutable reference data; contact info, known TLDs, known exclusions"""
        self._ips: ref.IpReport = ref.build.new_ip_report_obj()
        """Storage for valids, invalids, and valids_split values"""
        self._reporter = None
        """Pointer to _reporter_caller helper object. Built when needed"""
        self._gun = None
        """Pointer to custom datatype GatherUnique. Built when needed"""

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
    def _hn_in_breakdown(target) -> List[str]:
        """
        Check hn_in entries for if possible file, passed list, or single string.
        Break down into array and return

        Args:
            target: Either a single item, list of items, or stringpath to file containing
                  items (Line separated)

        Return:
            List of item(s) in targ
        """

        arr = []
        # Try list unpacking
        if isinstance(target, (list, tuple)):
            arr += [x for x in target]

        # Try following it as a file name (best for argv entries)
        else:
            try:
                with open(target) as file:
                    for line in file:
                        try:
                            line = str(line)
                            arr.append(line.strip())
                        except ValueError:
                            pass

            # Give up, assume it's a hostname to check
            except FileNotFoundError:
                arr.append(target)
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
            self._ips.hostnames_in += self._hn_in_breakdown(hn_in)
            return True

        # Check if hostnames passed through in sys_argv
        if len(sys_argv) > 1:
            for ndx in range(1, len(sys_argv)):
                self._ips.hostnames_in += self._hn_in_breakdown(sys_argv[ndx])
            return True

        return False

    def _splash_screen(self) -> None:
        """
        Print welcome screen (w/ verbosity check)
        """

        self._verprint(dedent("""
            * * AdHoc Server Name Resolver * *

        Identifies IPs for a list of given servers, based on internal TLDs"""))

    def _gather(self) -> None:
        """
        Verbosity print basic instructions.
        Gather server names from user, split by newline
        Runs until blank line submitted
        Defaults to pass if self.hostnames_in is set (hostnames_in clears on subsequent runs)
        """

        # First build for Gather Unique (gun)
        if not self._gun:
            from hostname_resolver.custom_datatypes.gatherunique import GatherUnique
            self._gun = GatherUnique()

        # Gun has no verbosity setting. Emulate by building here
        header = ''
        """Header to send to gun"""
        if self._sett.verbose:
            header = dedent("""
                Enter manually or copy/paste a column of server names separated by new lines
                Enter a blank line to start scan
                Note: while full domains are optional, a large list without them WILL take time
                """)

        # Any previously gathered entires. Used when adding to socket_answers
        prev_gathered = [prev.given for prev in self._ips.socket_answers]

        # If not hostnames_in, gun prompts for entries via stdin
        self._ips.hostnames_in \
            = self._gun.run(header=header,
                            list_in=self._ips.hostnames_in,
                            blacklist1=prev_gathered,
                            blacklist2=self._const.known_exclusions)

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

        from hostname_resolver.custom_datatypes.tablemat import tmat as _cust_tmat
        return _cust_tmat(*to_display, gap_space=15)

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
                ip_add = sock_ghbn(name)
                if self._tld_assumed(hostname, top):
                    name += self._const.local_tld
                return name, ip_add
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
        self._verprint(self._tmat('#', self._ips.sock_ans.keys()))

        num = 1
        """Line counter. Counts previous answers AND new resolves"""

        # Pull stored givens, if any. Allows 'adding' hostnames without explicitly saving table
        for prev in self._ips.socket_answers:
            self._ips.valids.append(prev.ip)
            self._verprint(self._tmat(num, [p for p in prev]))
            num += 1

        # Iterate through hostnames_in. Gather name and IP.
        for given in self._ips.hostnames_in:
            answer: ref.SocketAnswer
            try:
                a_fqdn, a_ip = self._ghbn_ext(given)
                answer = self._ips.sock_ans(given=given, fqdn=a_fqdn, ip=a_ip)
                self._ips.valids.append(answer.ip)
            except ValueError:
                # ValueError raised if unable to resolve. Consider invalid hostname
                answer = self._ips.sock_ans(given=given)
                self._ips.invalids.append(answer.given)
            finally:
                self._verprint(self._tmat(num, answer.values()))
                self._ips.socket_answers.append(answer)
                num += 1

    def _reporter_caller(self, rep_type: str):
        """
        Manages reporting functions

        Args:
            rep_type: ['csv_raw', 'csv_sort', 'single']  used to call appropriate reporting function
        """

        # Import report module. Build _reporter pointer on first demand
        from hostname_resolver import reporter_helper as rep
        if not self._reporter:
            self._reporter: rep.ReporterManagerObj \
                = rep.build.new_reporter_obj(constants=self._const,
                                             settings=self._sett,
                                             ip_report=self._ips)

        if rep_type not in self._reporter.dict_call:
            raise KeyError("Invalid argument passed to reporter caller!"
                           "Debug: check _report_amanager.dict_call ")

        self._reporter.dict_call[rep_type]()

    def _menu_prompt(self) -> None:
        """
        After run, prompts user for next step.
        """

        prompts = '0 1 2 3 4'.split()
        menu = '\n(0) Quit '\
               '\n(1) Run a new list '\
               '\n(2) Add to list'\
               '\n(3) Generate CSV Report' \
               '\n(4) Generate CSV Report, sorted' \
               '\n(5) Generate Single Page Report'

        menuing = True
        while menuing:
            menuing = False

            self._verprint(menu)
            prompt = None
            while prompt not in prompts:
                prompt = input('> ')

                # any more options and we'd need a whole separate menuing system...
                if prompt == '0':
                    # Exit run loop
                    self._repeating = False
                elif prompt == '1':
                    # Clear all lists
                    self._ips.reset_all()
                elif prompt == '2':
                    # Keep previous socket answers to add to
                    self._ips.reset()
                elif prompt == '3':
                    # Gen CSV Report, same order as gathered
                    menuing = True
                    self._reporter_caller('csv_raw')
                elif prompt == '4':
                    # Gen CSV Report, Sorted alphabetically and divided by valids and invalids
                    menuing = True
                    self._reporter_caller('csv_sort')
                elif prompt == '5':
                    # Gen Single text file report
                    menuing = True
                    self._reporter_caller('single')

    def run(self,
            hostnames_in: List[str] = None,
            *,
            verbose=True,
            sngl_split_size=30,         # Optional Single file settings arguments
            sngl_report_joiner=',',
            ) -> Tuple[List[str], List[str]]:
        """
        A bulk hostname resolver, designed to get info on a large number of internal hostnames
        against internal TLDs

        Args:
            hostnames_in: optional option to pass a list of hostnames via code
            verbose: On screen verbosity. Combine with hostnames_in for smoother usage
            sngl_split_size: Single reports break ips into [size] sized chunks
            sngl_report_joiner: string used to join IPs together (typically for some sort of
                separate reporting functionality

        Returns:
            Tuple of two lists; list of all IPs gathered, and a list of any hostnames that could not
                be resolved
        """

        # Set running settings
        self._sett.set_settings(verbose=verbose,
                                sngl_split_size=sngl_split_size,
                                sngl_report_joiner=sngl_report_joiner)

        # Try to process any argv or run(hostnames_in) arguments.
        self._process_hostnames_given(hostnames_in)

        # If hostnames weren't passed, greet user.
        if not self._ips.hostnames_in:
            self._splash_screen()

        while self._repeating:
            self._gather()      # Note: if hostnames were given, gather does nothing for first run
            self._resolve()
            self._menu_prompt()

        return self._ips.valids, self._ips.invalids


if __name__ == '__main__':
    _HN2IP = HostnameResolver()
    _HN2IP.run()
