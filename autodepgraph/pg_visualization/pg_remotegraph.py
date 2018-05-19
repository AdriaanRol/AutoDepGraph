# import pyqtgraph as pg
# import pyqtgraph.multiprocess as pgmp


# class pg_DiGraph_window():
#     """
#     """
#     proc = None
#     rpg = None

#     def __init__(self, *args, figsize=(1000, 600), interval=0.25,
#                  window_title='', theme=((60, 60, 60), 'w'), show_window=True,
#                  remote=True, **kwargs):
#         super().__init__()
#         self.theme = theme
#         self.interval = interval

#         if remote:
#             if not self.__class__.proc:
#                 self._init_qt()
#         else:
#             # overrule the remote pyqtgraph class
#             self.rpg = pg
#         self.win = self.rpg.GraphicsWindow(title=window_title)
#         self.win.setBackground(theme[1])
#         self.win.resize(*figsize)

#         if args or kwargs:
#             self.add(*args, **kwargs)

#         if not show_window:
#             self.win.hide()
#         self.add_DiGraphViewbox()

#     def add_DiGraphViewbox(self):
#         # Adding the viewbox to which the graph gets added
#         self.viewbox = self.win.addViewBox()
#         self.viewbox.setAspectLocked()
#         self.DiGraph = self.rpgG.DirectedGraphItem()
#         self.viewbox.addItem(self.DiGraph)

#     def _init_qt(self):
#         # starting the process for the pyqtgraph plotting
#         # You do not want a new process to be created every time you start a
#         # run, so this only starts once and stores the process in the class
#         pg.mkQApp()
#         self.__class__.proc = pgmp.QtProcess()  # pyqtgraph multiprocessing
#         self.__class__.rpg = self.proc._import('pyqtgraph')
#         self.__class__.rpgG = self.proc._import(
#             'autodepgraph.pg_visualization.pg_DirectedGraphItem')

#         # self.rpg refers to self.__class__.rpg
#         self.rpg.setConfigOptions(antialias=True)

#     def clear(self):
#         """
#         Clears the plot window and removes all subplots and traces
#         so that the window can be reused.
#         """
#         self.win.clear()
#         self.add_DiGraphViewbox()

#     def _repr_png_(self):
#         """
#         Create a png representation of the current window.
#         """
#         image = self.win.grab()
#         byte_array = self.rpg.QtCore.QByteArray()
#         buffer = self.rpg.QtCore.QBuffer(byte_array)
#         buffer.open(self.rpg.QtCore.QIODevice.ReadWrite)
#         image.save(buffer, 'PNG')
#         buffer.close()
#         return bytes(byte_array._getValue())

#     def save(self, filename=None):
#         """
#         Save current plot to filename, by default
#         to the location corresponding to the default
#         title.

#         Args:
#             filename (Optional[str]): Location of the file
#         """
#         default = "{}.png".format(self.get_default_title())
#         filename = filename or default
#         image = self.win.grab()
#         image.save(filename, "PNG", 0)

#     def setGeometry(self, x, y, w, h):
#         """ Set geometry of the plotting window """
#         self.win.setGeometry(x, y, w, h)

#     def setData(self, **kw):
#         self.DiGraph.setData(**kw)
