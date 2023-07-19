import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

class MyMplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig, self.ax = plt.subplots(figsize=(8, 3), dpi=70)
        super(MyMplCanvas, self).__init__(fig)
        self.setParent(parent)
        fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.1)
        
    def plot(self, data, time_steps, color="#8C6BB1"):
        self.ax.clear()
        sns.lineplot(x=time_steps, y=data, ax=self.ax, color=color, linewidth=3)    
        self.draw()
    
    def clear(self):
        self.ax.clear()
        self.draw()