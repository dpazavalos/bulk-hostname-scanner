"""Simple table formatter"""


def tmat(*to_display: any, gap_space=10) -> str:
    """
    returns values in standardized table format, used to stdout results
    """

    # Make sure all items to display are unpacked
    disp_arr = []
    for item in to_display:
        if isinstance(item, (list, tuple)):
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
        gapper += gap_space

    return tbl
