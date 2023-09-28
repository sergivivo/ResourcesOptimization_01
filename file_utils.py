def parse_file(f):
    """
    Three possible formats for the columns:
        <ts_date> <ts_time> <generation> <o1> <o2>
        <generation> <o1> <o2>
        <o1> <o2>
    """
    first = f.readline().split()
    columns = len(first)
    lst = first + f.read().split()
    f.close()

    if columns == 2:
        generation = []
        o1 = [float(i) for i in lst[::columns]]
        o2 = [float(i) for i in lst[1::columns]]
    elif columns >= 3:
        # Ignore timestamps
        generation = [int(i) for i in lst[columns-3::columns]]
        o1 = [float(i) for i in lst[columns-2::columns]]
        o2 = [float(i) for i in lst[columns-1::columns]]
    else:
        generation, o1, o2 = [], [], []

    return generation, o1, o2

