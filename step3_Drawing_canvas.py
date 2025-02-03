import numpy as np
import matplotlib.pyplot as plt

class SimpleDrawTool:
    def __init__(self):
        # Set up the plot
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], color='blue')
        self.cid_click = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.ax.set_ylim(-1, 1)
        self.ax.set_xlim(0, 1000)  # Adjust the x-axis range as needed
        self.is_drawing = False
        self.drawing = np.zeros(1000)  # Blank canvas for drawing
        self.prev_idx = None  # To store the previous index for continuous line
        plt.show()

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        self.is_drawing = True
        self.prev_idx = int(event.xdata)
        self.update_drawing(event)

    def on_hover(self, event):
        if self.is_drawing and event.inaxes == self.ax:
            self.update_drawing(event)

    def on_release(self, event):
        self.is_drawing = False
        self.prev_idx = None

    def update_drawing(self, event):
        idx = int(event.xdata)
        if 0 <= idx < len(self.drawing):
            if self.prev_idx is not None:
                # Create a continuous line between the previous point and the current point
                self.drawing[self.prev_idx:idx + 1] = np.linspace(self.drawing[self.prev_idx], event.ydata, idx - self.prev_idx + 1)
            self.drawing[idx] = event.ydata
            self.prev_idx = idx
            self.line.set_data(np.arange(len(self.drawing)), self.drawing)
            self.fig.canvas.draw()

# Example usage
SimpleDrawTool()
