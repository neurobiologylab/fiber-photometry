import pyqtgraph as pg

class Signal():
    def __init__(self, color:pg.mkPen, ymin, ymax, xlabel= "Time since start (s)", ylabel= "Intensity"):

        """
        Initialize the Signal object.
        Args:
            color (pg.mkPen):
        """
        self.plot = pg.PlotWidget()
        self.plot.setLabel("bottom", xlabel)
        self.plot.setLabel("left", ylabel)        
        self.color = color
        self.plot.setYRange(ymin,ymax)

    def set_sequence(self, timesteps, sequence):
        self.sequence = sequence
        self.timesteps = timesteps
    
    def plot(self):
        self.plot.plotItem.clear()
        self.plot.plotItem.plot(self.timesteps,self.sequence,pen=self.color)