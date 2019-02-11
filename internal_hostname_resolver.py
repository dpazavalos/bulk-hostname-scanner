"""
Internal hostname resolver

Given a list of host names, attempts to get IPs against a set list of TLDs \n
Splits Valids list into list max length split_size=30 (useful for scan limits) \n
If server is given without tld, tests and find appropriate TLD from list of known TLDs \n
NOTE: Long server lists without TLDs WILL take time \n

This module was originally written for use internally in large corporate domains, where a user may
encounter a list of server names without their internal TLDs, and need to figure the IP addresses
for a scan. Once hostname IPs are found, results are either \n \n

a) text_out= (Default True) \n
displayed in a temporary txt file (along with contact emails for easy copy/paste) divided up into
lines split_size=30 long and joined with report_joiner=',' with invalid hostnames displayed at tail.
Additionally, text_out=True enables the prompt again feature, allowing user to re-run with new input
 \n
b) return_list= (Default False) \n
returnes the final gathered list in a tuple (List[split_size=30 sized lists], invalid_hostnames)
Can be used in conjunction with text_out to prompt user to reset or add to list

Additionally, HostnameToIP(hostnames_in=None) can be given a list to automatically scan out for.\n
Note: doing so sets text_out=False, return_list=True, and show_status=False, meaning the script will
run once silently and return the tuples. Use for module integration \n
hostnames_in can be set either in __init__ or main(), however passing through main keeps those
attributes changed.
"""

from socket import getfqdn as sock_getfqdn, gethostbyname as sock_ghbn, gaierror as sock_gaierror
from webbrowser import open as wb_open
from textwrap import dedent
from re import search as reg_search
from os import remove as os_remove
from typing import List, Tuple, Optional
from sys import argv as sys_argv
import _reference_data


class HostnameToIP:
    """Translates hostnames to IP's (valids for found, invalids for not)\n
chunk_size breaks up list of valids into necessary sized lines as needed (useful for scan limts)
If server is given without tld, tests and find appropriate TLD from list of known TLDs\n
NOTE: Long server lists without TLDs WILL take time\n

(If a list of hostnames to check already exists, provide as attribute hostnames_in)"""

    def __init__(self, hostnames_in: List[str] = None, split_size=30, report_joiner=',',
                 text_out=True, return_list=False, show_status=True):

        # Bind References to custom data types
        self.ips = _reference_data.IPReports.new()
        """Storage for valids, invalids, and valids_split values"""
        self.ref = _reference_data.References
        """Immutable reference data; contact info, known TLDs, known exclusions"""

        # text_out reporting attributes
        self.split_size: int = split_size
        """# to split list of valids into, for potential scan limits"""
        self.report_joiner: str = report_joiner
        """String character used to separate valids return IPs into"""

        # Module running attributes
        self.repeating: bool = True
        """Used to keep main loop repeating, typically in conjunction with text_out"""
        self.text_out: bool = text_out
        """Bool to display results in a txt file or not
        Also used by prompt to run again (since running again is only used with text_out"""
        self.return_list: bool = return_list
        """Bool to return final results in a nested list\n
        [0] valids (one list, no chunks), [1] invalids"""
        self.show_status = show_status
        """Enables stdout print"""

        self.hostnames_in: List[str] = []
        """List of given hostnames to resolve"""
        self.check_if_hostnames_given(hostnames_in)

        self.local_tld: str = ''
        """localhost's tld, if has one\n
        When not given, DNS will assume similar .domain.TLD . Helpful for figuring IPs,
        but stdout will then only show hostname\n
        Use to check if TLD was assumed, and append to stdout"""
        try:
            self.local_tld += reg_search(r"\..*", sock_getfqdn())[0]
        except TypeError:
            # if local hostname has no
            pass

    def stat_print(self, *to_print):
        """Default check against self.show_status to see if allowed to print"""
        if self.show_status:
            for arg in to_print:
                print(arg, end=' ')
            print()

    def clear_ips(self):
        self.ips.reset()

    def silent_running(self, text_out=False, return_list=False, show_status=False):
        self.text_out = text_out
        self.return_list = return_list
        self.show_status = show_status

    def check_if_hostnames_given(self, hn_in) -> None:
        """Checks if a list of hostnames was given to the module\n
        Hostnames can be passed either on init or when calling main"""
        # Check if init with hostnames
        if self.hostnames_in:
            pass

        # Check if main with hostnames
        elif hn_in:
            self.silent_running()
            for hostname in hn_in:
                self.hostnames_in.append(hostname)

        # check if called from command line and if sys.argv has hostnames as arg, or a simple file
        # containing hostnames
        elif len(sys_argv) > 1:
            self.silent_running()
            for arg in sys_argv:
                self.hostnames_in.append(arg)

        settest: set = [1, 2, 3]
        set()


    @staticmethod
    def splash() -> str:
        """Welcome screen"""

        return dedent("""
        
        
            * * AdHoc Server Name Resolver * *

        Identifies IPs for a list of given servers, based on internal TLDs

        Enter manually or copy/paste a column of server names separated by new lines
        Text file will open with lines of IPs for servers, no more than 30 IPs per line
        Note: while full domains are optional, a large list without them WILL take time""")

    def splash_screen(self) -> None:
        """Print welcome screen"""
        self.stat_print(self.splash())

    @staticmethod
    def report_header(title: str) -> str:
        return '\n\n' + title.center(44, '=') + '\n\n'

    def report_invalids(self, invalids_remaining: List[str]) -> str:
        """given a list of invalid results, prepares for reporting function\n
        (Can be given a blank list, to indicate no invalid results)"""

        rep: str = ''

        rep += self.report_header("Contacts")
        rep += self.ref.contacts

        # Build rep if any unidentified servers
        if invalids_remaining:
            rep += self.report_header('Servers with no found IP')
            rep += '\n'.join(i for i in invalids_remaining)
        else:
            rep += self.report_header('IPs found for all Servers')

        return rep

    @staticmethod
    def dns_assumed(hostname: str, tld: str) -> bool:
        """Determines if DNS assumed the domain.TLD. on an unqualified hostname"""
        return ('.' not in hostname) and (not tld)

    def ghbn(self, hostname: str) -> Tuple[str, str]:
        """Iterative socket.gethostbyname on given hostname + each self.tlds\n
        Returns hostname's IP and tld used\n
        If unable to resolve, returns none"""

        for top in self.ref.tlds:
            try:
                ip_gathered, tld_used = sock_ghbn(hostname + top), top
                if self.dns_assumed(hostname, tld_used):
                    # If hostname was provided without TLD but TLD matches running machine's TLD,
                    # then gethostbyname runs successfully without notice.
                    # Catch this and use local_tld
                    tld_used = self.local_tld

                return ip_gathered, tld_used

            except (sock_gaierror, UnicodeError):
                pass

    def gather(self) -> None:
        """Gathers server names from user, split by newline\n
        Runs until blank line submitted
        Defauts to pass if self.hostnames_in is set"""
        if not self.hostnames_in:
            prompt: str = None
            self.stat_print("\nEnter servers (Leave blank to start scan)\n")
            while prompt != '':
                prompt = input('> ').lower().strip()
                if prompt and (prompt not in self.hostnames_in) and \
                        (prompt not in self.ref.known_exclusions):
                    self.hostnames_in.append(prompt)

    @staticmethod
    def tprint(zero: any = '', one: any = '', two: any = '') -> str:
        """returns three values in standardized table format, used to stdout results"""
        return ' '.join((str(zero).rjust(7), str(one).ljust(17), str(two).ljust(27)))

    def split_list(self, target: list) -> List[List[str]]:
        """Splits given list into nested lists based on self.chunk_size as range step"""
        out: List[list] = []
        for i in range(0, len(target), self.split_size):
            out.append(target[i:i + self.split_size])
        return out

    def sort(self) -> None:
        """Sorts hostnames from self.hostnames_in to valid and invalid lists based on ghbn results\n
        """

        # stdout Header
        self.stat_print('\n\t*', len(self.hostnames_in), 'unique servers identified *\n')
        self.stat_print(self.tprint('#', 'IP', 'Server Name'))

        line_count = 0

        # Get host by name, sorts, and tabling
        # stdout used for Progress only.
        # Valids and Invalids ultimately write to AdHoc_IpBlocks.txt or are returned
        for srv in self.hostnames_in:
            line_count += 1
            ip_gathered = self.ghbn(srv)
            if ip_gathered:
                self.stat_print(self.tprint(line_count, ip_gathered[0], srv + ip_gathered[1]))
                self.ips.valids.append(ip_gathered[0])
            else:
                # All TLDs tried, none valid. Return given hostname name only
                self.stat_print(self.tprint(line_count, 'N / A', srv))
                self.ips.invalids.append(srv)

        self.ips.valids_split = self.split_list(self.ips.valids)

    def report_to_txt(self) -> None:
        """Cultivates text report from self.valids and self.invalids"""

        # Write valid IPs to rep_file
        with open(self.ref.rep_file, 'w') as report:
            report.write('\n\n'.join(
                [self.report_joiner.join(valid) for valid in self.ips.valids_split]))

        # Any remaining servers (invalid names)
        with open(self.ref.rep_file, 'a') as report:
            report.write(self.report_invalids(self.ips.invalids))

        # use default text editor to open file
        # Note that wb_open calls web browser to open the file with default opener
        # While this works, can take a moment to open. The check_again
        wb_open(self.ref.rep_file)

    def check_run_again(self, prompt: str = '') -> None:
        """Sets self.repeating T/F flag, optional open Scan Portal"""
        # Need to increase options? consider python module pycolims to manage single stage menu-ing

        self.stat_print('\n(0) Quit '
                        '\n(1) Run a new list '
                        '\n(2) Add to list')

        prompts = '0 1 2'.split()
        while prompt not in prompts:
            prompt = input('> ')

        # Exit main loop
        if prompt == '0':
            self.repeating = False
            os_remove(self.ref.rep_file)

        # Clear list
        elif prompt == '1':
            self.clear_ips()
            self.repeating = True

        # todo ensure properly extends. Sublist to add to main?
        elif prompt == '2':
            self.repeating = True

    def main(self, hostnames_in: List[str] = None) -> Optional[Tuple[List[List[str]], List[str]]]:
        """Display splash screen, gather IPs (hostnames_in= or stdin), opt report, return list"""

        # todo expand check (main arg, init, sys.argv)
        self.check_if_hostnames_given(hostnames_in)

        if self.text_out:
            self.splash_screen()
            while self.repeating:
                self.gather()
                self.sort()
                self.report_to_txt()
                self.check_run_again()

        else:
            self.gather()
            self.sort()

        if self.return_list:
            return self.ips.valids_split, self.ips.invalids


if __name__ == '__main__':
    HN2IP = HostnameToIP()
    HN2IP.main()
