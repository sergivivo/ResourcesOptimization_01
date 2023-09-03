import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

def get_recommended_ticks(o_min, o_max, integer=False):
    STEPS = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1., 2., 5., 10., 20., 50., 100.]
    DIVISIONS = 10
    for i in range(len(STEPS)):
        if STEPS[i] <= (o_max - o_min) / DIVISIONS < STEPS[i+1]:
            if integer and STEPS[i+1] < 1:
                step = 1
            else:
                step = STEPS[i+1]
            start = np.floor(o_min / step) * step
            end   = (np.ceil(o_max / step) + 1) * step
            return np.arange(start, end, step)

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

def plot_scatter_legend(configs):
    solutions = []

    for f in configs.input:
        generation, o1, o2 = parse_file(f)

        # Generation should preferably be an empty list
        if generation:
            # Otherwise, only get the values from the last generation
            last_idx = generation.index(generation[-1])
            o1 = o1[last_idx:]
            o2 = o2[last_idx:]

        solutions.append({'x': o1, 'y': o2})

    fig, ax = plt.subplots()

    o1_all = [e for d in solutions for e in d['x']]
    o2_all = [e for d in solutions for e in d['y']]

    # X axis ticks
    o1_min, o1_max = min(o1_all), max(o1_all)
    o1_ticks = get_recommended_ticks(o1_min, o1_max)
    ax.set_xticks(o1_ticks)
    #ax.set_xlim(o1_ticks[0], o1_ticks[-1])

    # Y axis ticks
    o2_min, o2_max = min(o2_all), max(o2_all)
    o2_ticks = get_recommended_ticks(o2_min, o2_max, integer=True)
    ax.set_yticks(o2_ticks)
    #ax.set_ylim(o2_ticks[0], o2_ticks[-1])

    # Title and labels
    plt.xlabel(configs.x_label)
    plt.ylabel(configs.y_label)
    plt.title(configs.title)

    # Fill missing names in legend so we plot all solutions even if there's any without a label
    legend = configs.legend if configs.legend else []
    names = legend + [''] * (len(solutions) - len(legend))

    for s, color, name in zip(solutions, mcolors.TABLEAU_COLORS, names):
        ax.scatter(s['x'], s['y'], s=30, facecolors=color, edgecolors=color, label=name)

    ax.legend()

    if configs.output:
        plt.savefig(configs.output)
    else:
        plt.show()

                
def plot_convergence(configs):
    generation, o1, o2 = parse_file(configs.input[0])

    max_gen = max(generation)
    color = [float(item) for item in generation]

    fig, ax = plt.subplots()

    points = ax.scatter(o1, o2, s=50, c=color, cmap='viridis')

    # X axis ticks
    o1_min, o1_max = min(o1), max(o1)
    o1_ticks = get_recommended_ticks(o1_min, o1_max)
    ax.set_xticks(o1_ticks)
    #ax.set_xlim(o1_ticks[0], o1_ticks[-1])

    # Y axis ticks
    o2_min, o2_max = min(o2), max(o2)
    o2_ticks = get_recommended_ticks(o2_min, o2_max, integer=True)
    ax.set_yticks(o2_ticks)
    #ax.set_ylim(o2_ticks[0], o2_ticks[-1])

    # Title and labels
    plt.xlabel(configs.x_label)
    plt.ylabel(configs.y_label)
    plt.title(configs.title)

    fig.colorbar(points)

    if configs.output:
        plt.savefig(configs.output)
    else:
        plt.show()
    

if __name__ == '__main__':
    pass


