import os

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D




def slices(cube, orientation):
    S = cube.shape[0]
    if orientation not in {0, 1, 2}:
        raise ValueError("Invalid orientation")
    for index in range(S):
        if orientation == 0:
            yield cube[index, :, :]
        if orientation == 1:
            yield cube[:, index, :]
        if orientation == 2:
            yield cube[:, :, index]


def plot_cube(cube):
    S = cube.shape[0]
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.set_xlim3d(left=0, right=S)
    ax.set_ylim3d(bottom=0, top=S)
    ax.set_zlim3d(bottom=0, top=S)
    for a in range(0, S):
        for b in range(0, S):
            for c in range(0, S):
                ax.text3D(x=a, y=b, z=c, s=int(cube[a, b, c]))
    plt.show()


def plot_slice(cube, orientation, index, alpha=0.1, save_fig=None):
    S = cube.shape[0]
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.set_xlim3d(left=0 - 0.25, right=S-0.5)
    ax.set_ylim3d(bottom=0 - 0.25, top=S-0.5)
    ax.set_zlim3d(bottom=0 - 0.25, top=S-0.5)
    #ax.set_xlim3d(left=0, right=S)
    #ax.set_ylim3d(bottom=0, top=S)
    #ax.set_zlim3d(bottom=0, top=S)
    for a in range(0, S):
        for b in range(0, S):
            for c in range(0, S):
                if orientation == 0 and a == index:
                    ax.text3D(x=a, y=b, z=c, s=int(cube[a, b, c]), color="red")
                if orientation == 1 and b == index:
                    ax.text3D(x=a, y=b, z=c, s=int(cube[a, b, c]), color="red")
                if orientation == 2 and c == index:
                    ax.text3D(x=a, y=b, z=c, s=int(cube[a, b, c]), color="red")
                else:
                    ax.text3D(x=a, y=b, z=c, s=int(cube[a, b, c]), alpha=alpha)
    if save_fig:
        fig.savefig(save_fig, dpi=600)

    else:
        plt.show()




def save_slices(cube, file_name_prefix, directory_path):
    S = cube.shape[0]
    for orientation in  [0, 1, 2]:
        for slice_number, cube_slice in enumerate(slices(cube, orientation)):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlim(left=0 - 0.25, right=S-0.5)
            ax.set_ylim(bottom=0 - 0.25, top=S-0.5)
            ax.hlines(np.arange(np.sqrt(S), S+1, np.sqrt(S)) - 0.45, -1, S + 0.25)
            ax.vlines(np.arange(np.sqrt(S), S+1, np.sqrt(S)) - 0.45, -1, S + 0.25)
            for (x, y) in np.ndindex((S, S)):
                ax.text(x=x, y=y, s=int(cube_slice[x, y]))
            
            fig.savefig(os.path.join(directory_path, 
                                     file_name_prefix + "_{}_{}.png".format(orientation, slice_number)),
                                     dpi=600)

