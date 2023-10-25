import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from file_utils import parse_file, get_solution_array

def get_recommended_ticks(o_min, o_max, integer=False):
    STEPS = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1., 2., 5., 10., 20., 50., 100.]
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

def plot_scatter_legend(configs):
    solutions = []

    for f in configs.input:
        o = get_solution_array(f, n_obj=configs.n_objectives)[-1]
        solutions.append(o)

    fig = plt.figure()
    if configs.n_objectives == 2:
        ax = fig.add_subplot()
    elif configs.n_objectives == 3:
        ax = fig.add_subplot(projection='3d')

    o1_all = sum([o[:,0].tolist() for o in solutions], [])
    o2_all = sum([o[:,1].tolist() for o in solutions], [])
    if configs.n_objectives == 3:
        o3_all = sum([o[:,2].tolist() for o in solutions], [])

    if configs.ref_points is not None:
        ref_points = np.array(configs.ref_points)
        o1_all += ref_points[:,0].tolist()
        o2_all += ref_points[:,1].tolist()
        if configs.n_objectives == 3:
            o3_all += ref_points[:,2].tolist()

    # X axis ticks
    o1_min, o1_max = min(o1_all), max(o1_all)
    o1_ticks = get_recommended_ticks(o1_min, o1_max)
    ax.set_xticks(o1_ticks)
    half_x = (o1_ticks[1] - o1_ticks[0]) / 2
    ax.set_xlim(o1_ticks[0] - half_x, o1_ticks[-1] + half_x)

    # Y axis ticks
    o2_min, o2_max = min(o2_all), max(o2_all)
    o2_ticks = get_recommended_ticks(o2_min, o2_max)
    ax.set_yticks(o2_ticks)
    half_y = (o2_ticks[1] - o2_ticks[0]) / 2
    ax.set_ylim(o2_ticks[0] - half_y, o2_ticks[-1] + half_y)

    if configs.n_objectives == 3:
        # Z axis ticks
        o3_min, o3_max = min(o3_all), max(o3_all)
        o3_ticks = get_recommended_ticks(o3_min, o3_max)
        ax.set_zticks(o3_ticks)
        half_z = (o3_ticks[1] - o3_ticks[0]) / 2
        ax.set_zlim(o3_ticks[0] - half_z, o3_ticks[-1] + half_z)


    # Title and labels
    ax.set_xlabel(configs.x_label)
    ax.set_ylabel(configs.y_label)
    if configs.n_objectives == 3:
        ax.set_zlabel(configs.z_label)
    plt.title(configs.title)

    # Fill missing names in legend so we plot all solutions even if there's any without a label
    legend = configs.legend if configs.legend else []
    names = legend + [''] * (len(solutions) - len(legend))

    if configs.ref_points is not None:
        color = mcolors.TABLEAU_COLORS['tab:cyan']
        if configs.n_objectives == 2:
            ax.scatter(ref_points[:,0], ref_points[:,1], s=50, facecolors="None", edgecolors=color, label='ILP', marker='D')
        elif configs.n_objectives == 3:
            ax.scatter(ref_points[:,0], ref_points[:,1], ref_points[:,2], s=50, facecolors="None", edgecolors=color, label='ILP', marker='D')

    for s, color, name in zip(solutions, mcolors.TABLEAU_COLORS, names):
        if configs.n_objectives == 2:
            ax.scatter(s[:,0], s[:,1], s=30, facecolors=color, edgecolors=color, label=name)
        elif configs.n_objectives == 3:
            ax.scatter(s[:,0], s[:,1], s[:,2], s=30, facecolors=color, edgecolors=color, label=name)

    ax.legend()

    if configs.output:
        plt.savefig(configs.output)
    else:
        plt.show()

                
def plot_convergence(configs):
    generation, o = parse_file(configs.input[0], n_obj=configs.n_objectives)

    max_gen = max(generation)

    if configs.trim_gen:
        # Exclude generations after convergence
        last_gen = generation[-1]
        idx = generation.index(last_gen)
        step = len(generation) - idx

        o1_cmp, o2_cmp = set(o[0][idx:]), set(o[1][idx:])
        o1_set, o2_set = set(o[0][idx-step:idx]), set(o[1][idx-step:idx])
        while o1_set == o1_cmp and o2_set == o2_cmp:
            idx -= step
            o1_set, o2_set = set(o[0][idx-step:idx]), set(o[1][idx-step:idx])

        generation = generation[:idx+step]
        o1 = o[0][:idx+step]
        o2 = o[1][:idx+step]

    color = [float(item) for item in generation]

    fig, ax = plt.subplots()

    points = ax.scatter(o1, o2, s=50, c=color, cmap='viridis')

    # X axis ticks
    o1_min, o1_max = min(o1), max(o1)
    o1_ticks = get_recommended_ticks(o1_min, o1_max)
    ax.set_xticks(o1_ticks)
    half_x = (o1_ticks[1] - o1_ticks[0]) / 2
    ax.set_xlim(o1_ticks[0] - half_x, o1_ticks[-1] + half_x)

    # Y axis ticks
    o2_min, o2_max = min(o2), max(o2)
    o2_ticks = get_recommended_ticks(o2_min, o2_max, integer=True)
    ax.set_yticks(o2_ticks)
    half_y = (o2_ticks[1] - o2_ticks[0]) / 2
    ax.set_ylim(o2_ticks[0] - half_y, o2_ticks[-1] + half_y)

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


