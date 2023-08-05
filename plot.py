import matplotlib.pyplot as plt
import numpy as np

def plot_evolution(configs):
    lst = configs.input.read().split()
    configs.input.close()

    generation = [int(i)+1 for i in lst[::3]]
    o1 = [float(i) for i in lst[1::3]]
    o2 = [float(i) for i in lst[2::3]]

    max_gen = max(generation)
    color = [float(item) for item in generation]

    fig, ax = plt.subplots()

    points = ax.scatter(o1, o2, s=50, c=color, cmap='viridis')
    ax.set_xticks(np.arange(np.floor(min(o1)), np.ceil(max(o1))+1, 2.))
    ax.set_yticks(np.arange(np.floor(min(o2)), np.ceil(max(o2))+1, 1))
    fig.colorbar(points)

    plt.show()
    

if __name__ == '__main__':
    pass
