import pyqtgraph as pg
import numpy as np

# replaces all the import statements from the existing pyqtgraph class
GraphicsObject = pg.GraphicsObject
ScatterPlotItem = pg.ScatterPlotItem
QtCore = pg.QtCore
QtGui = pg.QtGui
getConfigOption = pg.getConfigOption
TextItem = pg.TextItem
ArrowItem = pg.ArrowItem

fn = pg.fn

__all__ = ['DirectedGraphItem']


class DirectedGraphItem(GraphicsObject):
    """
    A DirectedGraphItem displays graph information as
    a set of nodes connected by arrows (as in 'graph theory', not 'graphics').
    Useful for drawing networks, trees, etc.

    Based on the GraphItem class from pyqtgraph
    """

    def __init__(self, **kwds):
        GraphicsObject.__init__(self)
        self.scatter = ScatterPlotItem()
        self.scatter.setParentItem(self)
        self.adjacency = None
        self.pos = None
        self.picture = None
        self.labels = None
        self.old_labels = None
        self.pen = 'default'
        self.symbolSize = 5
        self.setData(**kwds)

    def setData(self, **kwds):
        """
        Change the data displayed by the graph.

        ======================================================================
        **Arguments:**
        labels          (N) array with labels of each node in the graph.
        pos             (N,2) array of the positions of each node in the graph.
        adj             (M,2) array of connection data. Each row contains
                          indexes of two nodes that are connected.
        pen             The pen to use when drawing lines between connected
                        nodes. May be one of:

                        * QPen
                        * a single argument to pass to pg.mkPen
                        * a record array of length M
                          with fields (red, green, blue, alpha, width). Note
                          that using this option may have a significant
                          performance cost.
                        * None (to disable connection drawing)
                        * 'default' to use the default foreground color.

        symbolPen       The pen(s) used for drawing nodes.
        symbolBrush     The brush(es) used for drawing nodes.
        ``**opts``      All other keyword arguments are given to
                        :func:`ScatterPlotItem.setData()
                            <pyqtgraph.ScatterPlotItem.setData>`
                        to affect the appearance of nodes (symbol, size, brush,
                        etc.)
        ======================================================================
        """
        if 'labels' in kwds:
            self.labels = kwds.pop('labels')
            self._update()

        if 'adj' in kwds:
            self.adjacency = kwds.pop('adj')
            if self.adjacency.dtype.kind not in 'iu':
                raise Exception(
                    "adjacency array must have int or unsigned type.")
            self._update()
        if 'pos' in kwds:
            self.pos = kwds['pos']
            self._update()
        if 'pen' in kwds:
            self.setPen(kwds.pop('pen'))
            self._update()

        if 'size' in kwds:
            # Pop is not used as it still needs to be passed on to the symbol
            self.symbolSize = kwds['size']
        else:  # use the default value set in the init of this object
            kwds['size'] = self.symbolSize

        if 'symbolPen' in kwds:
            kwds['pen'] = kwds.pop('symbolPen')
        if 'symbolBrush' in kwds:
            kwds['brush'] = kwds.pop('symbolBrush')

        self.scatter.setData(**kwds)

        # Setting the labels
        v = self.getViewBox()
        if (self.labels is not None) and (self.old_labels != self.labels):
            for label, pos in zip(self.labels, self.pos):
                txt = TextItem(text=label, color=(60, 60, 60),
                               anchor=(0.5, 0.5))
                v.addItem(txt)
                txt.setPos(pos[0], pos[1])
        self.old_labels = self.labels

        self.informViewBoundsChanged()

    def _update(self):
        self.picture = None
        self.prepareGeometryChange()
        self.update()

    def setPen(self, *args, **kwargs):
        """
        Set the pen used to draw graph lines.
        May be:

        * None to disable line drawing
        * Record array with fields (red, green, blue, alpha, width)
        * Any set of arguments and keyword arguments accepted by
          :func:`mkPen <pyqtgraph.mkPen>`.
        * 'default' to use the default foreground color.
        """
        if len(args) == 1 and len(kwargs) == 0:
            self.pen = args[0]
        else:
            self.pen = fn.mkPen(*args, **kwargs)
        self.picture = None
        self.update()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        if (self.pen is None or self.pos is None or self.adjacency is None):
            return

        p = QtGui.QPainter(self.picture)

        # Drawing the lines between the nodes
        try:
            pts = self.pos[self.adjacency]
            pen = self.pen
            if isinstance(pen, np.ndarray):
                lastPen = None
                for i in range(pts.shape[0]):
                    pen = self.pen[i]
                    if np.any(pen != lastPen):
                        lastPen = pen
                        if pen.dtype.fields is None:
                            p.setPen(
                                fn.mkPen(color=(pen[0], pen[1],
                                                pen[2], pen[3]), width=1))
                        else:
                            p.setPen(
                                fn.mkPen(color=(pen['red'], pen['green'],
                                                pen['blue'], pen['alpha']),
                                         width=pen['width']))
                    p.drawLine(QtCore.QPointF(
                        *pts[i][0]), QtCore.QPointF(*pts[i][1]))

            else:
                if pen == 'default':
                    pen = getConfigOption('foreground')
                p.setPen(fn.mkPen(pen))
                pts = pts.reshape((pts.shape[0]*pts.shape[1], pts.shape[2]))
                path = fn.arrayToQPath(
                    x=pts[:, 0], y=pts[:, 1], connect='pairs')
                p.drawPath(path)

            # Adding arrow heads
            for i in range(0, len(pts), 2):  # pt in enumerate(pts):

                child_pos = pts[i][0] + 1j * pts[i][1]
                par_pos = pts[i+1][0] + 1j * pts[i+1][1]
                vec = par_pos-child_pos
                v = self.getViewBox()

                # Calculate the arrowangle to point towards the parent
                arrowangle = np.rad2deg(np.angle(vec)) + 180
                # The +180 have to do with 0 angle corresponding to an arrow
                # point to the left rather than from the left

                # The position of the tip of the arrow must be offset for the
                # size of the nodes, we use 1.95 to give a tiny offset
                # which I consider visually pleasing.
                arrowTipPos = par_pos - vec/abs(vec)*self.symbolSize/1.95

                arrowhead = ArrowItem(angle=arrowangle, tipAngle=40,
                                      headLen=self.symbolSize/2,
                                      pxMode=False, pen=pen, brush=pen)
                v.addItem(arrowhead)
                arrowhead.setPos(arrowTipPos.real, arrowTipPos.imag)
        finally:
            p.end()

    def paint(self, p, *args):
        if self.picture is None:
            self.generatePicture()
        if getConfigOption('antialias') is True:
            p.setRenderHint(p.Antialiasing)
        self.picture.play(p)

    def boundingRect(self):
        return self.scatter.boundingRect()

    def dataBounds(self, *args, **kwds):
        return self.scatter.dataBounds(*args, **kwds)

    def pixelPadding(self):
        return self.scatter.pixelPadding()
