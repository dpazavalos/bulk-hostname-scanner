"""Reusable unique item gatherer. Returns unique values with optional list_in and blacklists"""


class GatherUnique:
    """
    Reusable unique item gatherer. Returns unique values with optional list_in and blacklists
    """

    def __init__(self):

        self._header = ''
        """Optional header to display to user when gathering entries stdin"""
        self._list_in = []
        """optional input parameter, in lieu of stdin prompting"""
        self._gathered = []
        """Unique items reconciled against potential blacklist(s)"""
        self._black_lists = []
        """Optional list(s) of items to verify against"""

    def _reset(self):
        """
        Reset attributes
        """
        self._header = ''
        self._list_in.clear()
        self._black_lists.clear()
        self._gathered.clear()

    def _not_in_args(self, item) -> bool:
        """
        Check given item against black lists
        """
        for black_list in self._black_lists:
            if item in black_list:
                return False
        return True

    def _gather_from_stdin(self) -> None:
        """
        Gathers input from user, split by newline. Runs until blank line submitted.
        Sorts against blacklists into _gathered
        """
        print("\n" + self._header + "\n")

        prompt: str = None
        while prompt != '':
            prompt = input('> ').lower().strip()
            if prompt != '' and prompt not in self._gathered and self._not_in_args(prompt):
                self._gathered.append(prompt)

    def _gather_from_list_in(self):
        """
        Gathers items from given list_in, sorts against blacklists into _gathered
        """
        for item in self._list_in:
            if item not in self._gathered and self._not_in_args(item):
                self._gathered.append(item)

    def _return_gathered(self) -> list:
        """
        Returns gathered list, resets working attributes
        """
        # Save gathered, clear attributes, return
        to_return = self._gathered.copy()
        self._reset()
        return to_return

    def run(self,
            header: str = '', list_in: list = None,
            **blacklists) -> list:
        """
        Gathers a list of unique entries from user, with optional blacklists and header prompt
        Note: Item type depends on gathering method. If using stdin, anticipate string returns.
        Otherwise, use list_in

        Args:
            header: Header prompt to display to user on startup.

            list_in: An optional input parameter. Feeding a list bypasses stdin, and straight to
                unique list generation. If black lists are provided, reconciles against them.

            blacklists: Optional *kwargs for one or more blacklists to check entires against.
                Returned list will not contain any blacklisted entries. (Note: kwargs used only for
                flexible positioning. Arg names literally do not matter)

        Returns:
            Unique list of values, either from stdin or list_in arg
        """

        # Assign running attributes
        self._header = header
        self._list_in = list_in
        for blist in blacklists.values():
            self._black_lists.append(blist)

        if list_in:
            self._gather_from_list_in()
        else:
            self._gather_from_stdin()

        return self._return_gathered()
