import numpy as np
from matplotlib import pyplot as plt
from celluloid import Camera
from matplotlib import animation, rc
from IPython.display import HTML
import config


def animate_traffic(fname='animation.mp4', save=False):
    # initiate camera to take snaps after every road update
    fig = plt.figure()
    cam = Camera(fig)

    frame = 0
    for state in config.plot_data:
        frame += 1
        plt.gca().set_xlim([0, len(state)])
        plt.gca().set_ylim([0, 2])
        plt.gca().axis('off')
        plt.gca().grid(b=None)
        plt.text(0, 1.5, str(z))
        # draws filled block at car position and empty block at empty position
        for i in range(len(state)):
            if state[i] != 0:
                rectangle = plt.Rectangle((i, 0.05), 1, 1.04, color="k")
            else:
                rectangle = plt.Rectangle((i, 0.05), 1, 1.04, fill=False)
            plt.gca().add_patch(rectangle)
        plt.gca().autoscale(tight=False, axis="x")
        cam.snap()
    ani = cam.animate(interval=500, blit=False)
    if save:
        ani.save(fname)
    return HTML(ani.to_html5_video())
