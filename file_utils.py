import numpy as np

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

def get_solution_array(f):
    solutions = []
    generation, o1, o2 = parse_file(f)

    if len(generation) > 0:
        last_gen = generation[-1]

        # To avoid ValueError when calling method index
        generation.append(last_gen+1)

        for g in range(1, last_gen+1):
            i, j = generation.index(g), generation.index(g+1)
            o1_slize, o2_slize = o1[i:j], o2[i:j]
            solutions.append(np.array([o1_slize,o2_slize]).T)
    else:
        solutions.append(np.array(o1, o2).T)

    return solutions

