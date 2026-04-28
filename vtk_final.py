import sys, os
import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.collections import LineCollection
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QCheckBox, QSlider, QScrollArea,
    QGroupBox, QFileDialog, QSizePolicy, QDoubleSpinBox,
    QTabWidget, QTextEdit, QComboBox, QFrame, QDialog,
    QDialogButtonBox, QSpinBox, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.util.numpy_support import vtk_to_numpy


# ================================================================
#  14 DISTINCT COLORS — Blue-Pink palette
# ================================================================
ISO_COLORS = [
    (0.15, 0.35, 0.90),
    (0.85, 0.20, 0.65),
    (0.30, 0.60, 1.00),
    (1.00, 0.40, 0.75),
    (0.10, 0.20, 0.75),
    (0.90, 0.10, 0.50),
    (0.45, 0.75, 1.00),
    (1.00, 0.60, 0.85),
    (0.20, 0.50, 0.95),
    (0.75, 0.15, 0.55),
    (0.55, 0.80, 1.00),
    (0.95, 0.75, 0.90),
    (0.05, 0.10, 0.60),
    (0.70, 0.05, 0.40),
]


# ================================================================
#  ISO ENTRY
# ================================================================
class IsoEntry:
    def __init__(self, idx, color, actor, edge_actor):
        self.idx = idx
        self.color = color
        self.actor = actor
        self.edge_actor = edge_actor


# ================================================================
#  ISO INPUT BOX
# ================================================================
class IsoInputBox(QWidget):
    def __init__(self, idx, color, all_vars, arrays, parent_win):
        super().__init__()
        self.idx = idx
        self.color = color
        self.all_vars = all_vars
        self.arrays = arrays
        self.parent_win = parent_win
        self.entry = None
        r, g, b = int(color[0]*255), int(color[1]*255), int(color[2]*255)
        self._rgb = (r, g, b)
        self.setObjectName(f"isobox_{idx}")
        self.setStyleSheet(
            f"QWidget#isobox_{idx}{{background:#eef2ff;"
            f"border:2px solid rgb({r},{g},{b});border-radius:5px;}}")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 6, 8, 8)
        lay.setSpacing(4)
        hdr = QLabel(f"  Isosurface  #{idx}")
        hdr.setStyleSheet(f"color:rgb({r},{g},{b});font-weight:bold;font-size:12px;"
                          f"border:none;background:transparent;")
        lay.addWidget(hdr)
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:rgb({r},{g},{b});max-height:1px;border:none;")
        lay.addWidget(sep)
        lay.addWidget(self._lbl("Variable:"))
        self.var_cb = QComboBox()
        self.var_cb.addItems(all_vars)
        self.var_cb.setFixedHeight(24)
        self.var_cb.setStyleSheet(
            "QComboBox{background:#fff;border:1px solid #aabbcc;color:#223344;"
            "border-radius:2px;padding:2px 4px;}"
            "QComboBox QAbstractItemView{background:#fff;color:#223344;"
            "selection-background-color:#d0d8f0;}")
        self.var_cb.currentTextChanged.connect(self._update_range)
        lay.addWidget(self.var_cb)
        self.range_lbl = QLabel("Range: —")
        self.range_lbl.setStyleSheet(
            "color:#335577;font-size:10px;padding:2px 4px;"
            "border:1px solid #aabbcc;border-radius:2px;background:#eef4ff;")
        self.range_lbl.setWordWrap(True)
        lay.addWidget(self.range_lbl)
        lay.addWidget(self._lbl("Isovalue:"))
        self.val_sp = QDoubleSpinBox()
        self.val_sp.setRange(-99999, 99999)
        self.val_sp.setValue(0.0)
        self.val_sp.setDecimals(2)
        self.val_sp.setSingleStep(10)
        self.val_sp.setFixedHeight(24)
        self.val_sp.setStyleSheet(
            "QDoubleSpinBox{background:#fff;border:1px solid #aabbcc;"
            "color:#223344;border-radius:2px;padding:2px 4px;}")
        lay.addWidget(self.val_sp)
        op_row = QHBoxLayout()
        op_row.addWidget(self._lbl("Opacity:"))
        self.opac_sl = QSlider(Qt.Horizontal)
        self.opac_sl.setRange(0, 100)
        self.opac_sl.setValue(55)
        self.opac_sl.valueChanged.connect(self._on_opac)
        op_row.addWidget(self.opac_sl)
        self.opac_lbl = QLabel("0.55")
        self.opac_lbl.setFixedWidth(32)
        self.opac_lbl.setStyleSheet("color:#445566;font-size:10px;border:none;background:transparent;")
        op_row.addWidget(self.opac_lbl)
        lay.addLayout(op_row)
        bot = QHBoxLayout()
        bot.setSpacing(4)
        self.draw_btn = QPushButton("▶  Draw / Update")
        self.draw_btn.setFixedHeight(28)
        self.draw_btn.setStyleSheet(
            f"QPushButton{{background:#e8f4e8;border:2px solid rgb({r},{g},{b});"
            f"color:rgb({r//2},{g//2},{b//2});font-weight:bold;border-radius:3px;}}"
            f"QPushButton:hover{{background:#d0ecd0;}}")
        self.draw_btn.clicked.connect(self._draw)
        bot.addWidget(self.draw_btn, 2)
        self.show_cb = QCheckBox("Show")
        self.show_cb.setChecked(True)
        self.show_cb.setStyleSheet(
            "QCheckBox{color:#333366;font-size:10px;border:none;background:transparent;}"
            "QCheckBox::indicator{width:13px;height:13px;border:1px solid #7788aa;"
            "border-radius:2px;background:#fff;}"
            "QCheckBox::indicator:checked{background:#3355cc;}")
        self.show_cb.stateChanged.connect(self._toggle_vis)
        bot.addWidget(self.show_cb)
        del_btn = QPushButton("✕")
        del_btn.setFixedSize(26, 26)
        del_btn.setStyleSheet(
            "QPushButton{background:#ffe8e8;border:1px solid #cc4444;"
            "color:#cc2222;font-size:12px;border-radius:3px;padding:0;}"
            "QPushButton:hover{background:#ffcccc;}")
        del_btn.clicked.connect(self._delete)
        bot.addWidget(del_btn)
        lay.addLayout(bot)
        self._update_range(self.var_cb.currentText())

    def _lbl(self, t):
        l = QLabel(t)
        l.setStyleSheet("color:#445566;font-size:10px;border:none;background:transparent;")
        return l

    def _update_range(self, var):
        if var in self.arrays:
            arr = self.arrays[var]
            lo, hi = float(arr.min()), float(arr.max())
            self.range_lbl.setText(f"Range:  [{lo:.4g},   {hi:.4g}]")
            self.val_sp.setRange(lo, hi)
            self.val_sp.setValue((lo+hi)/2.0)
        else:
            self.range_lbl.setText("Range: load data first")

    def _on_opac(self, val):
        self.opac_lbl.setText(f"{val/100:.2f}")
        if self.entry:
            op = val/100.0
            self.entry.actor.GetProperty().SetOpacity(op)
            self.entry.edge_actor.GetProperty().SetOpacity(op*0.5)
            self.parent_win._ren()

    def _toggle_vis(self, state):
        if self.entry:
            self.entry.actor.SetVisibility(bool(state))
            self.entry.edge_actor.SetVisibility(bool(state))
            self.parent_win._ren()

    def _draw(self):
        self.parent_win._draw_iso_box(self)

    def _delete(self):
        self.parent_win._delete_iso_box(self)


# ================================================================
#  COLORBAR CANVAS — shown in Volume Rendering mode
# ================================================================
class ColorbarCanvas(FigureCanvasQTAgg):
    def __init__(self):
        self.fig = Figure(figsize=(3.5, 0.7), facecolor="#fffaf0")
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(70)
        self._lo = 0.0
        self._hi = 1.0
        self._cmap_name = "Blue-Pink (blue->pink)"

    def update_bar(self, lo, hi, cmap_name, var_name=""):
        self._lo = lo
        self._hi = hi
        self._cmap_name = cmap_name
        self._var_name = var_name
        self.fig.clear()
        # Main gradient bar — give more room at bottom for Low/High labels
        ax = self.fig.add_axes([0.05, 0.52, 0.90, 0.28])
        gradient = np.linspace(0, 1, 512).reshape(1, -1)
        colors_list = self._get_colors_list(cmap_name)
        cmap = LinearSegmentedColormap.from_list("custom", colors_list, N=512)
        ax.imshow(gradient, aspect='auto', cmap=cmap,
                  vmin=0, vmax=1, interpolation='bilinear',
                  extent=[lo, hi, 0, 1])
        ax.set_yticks([])
        n_ticks = 5
        ticks = np.linspace(lo, hi, n_ticks)
        ax.set_xticks(ticks)
        ax.set_xticklabels([f"{t:.3g}" for t in ticks], fontsize=6.5, color='#553300')
        ax.tick_params(axis='x', which='both', length=3, colors='#553300', pad=1)
        for sp in ax.spines.values():
            sp.set_color('#ccaa88')
            sp.set_linewidth(0.8)

        # Get the actual low/high colors from the colormap
        low_color  = colors_list[0]   # first color = low values
        high_color = colors_list[-1]  # last color  = high values

        # Low label (left side) — colored swatch + text
        lo_hex = "#{:02x}{:02x}{:02x}".format(
            int(low_color[0]*255), int(low_color[1]*255), int(low_color[2]*255))
        hi_hex = "#{:02x}{:02x}{:02x}".format(
            int(high_color[0]*255), int(high_color[1]*255), int(high_color[2]*255))

        # Determine readable text color (white on dark bg, dark on light bg)
        def _text_col(rgb):
            lum = 0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2]
            return 'white' if lum < 0.55 else '#222222'

        self.fig.text(0.05, 0.10,
                      f"◀ LOW  {lo:.3g}",
                      ha='left', va='center', fontsize=7.5, fontweight='bold',
                      color=lo_hex, transform=self.fig.transFigure,
                      bbox=dict(boxstyle='round,pad=0.2', facecolor='#f0f0f0',
                                edgecolor=lo_hex, linewidth=1.2))

        self.fig.text(0.95, 0.10,
                      f"{hi:.3g}  HIGH ▶",
                      ha='right', va='center', fontsize=7.5, fontweight='bold',
                      color=hi_hex, transform=self.fig.transFigure,
                      bbox=dict(boxstyle='round,pad=0.2', facecolor='#f0f0f0',
                                edgecolor=hi_hex, linewidth=1.2))

        cmap_short = cmap_name.split('(')[0].strip()
        title = f"Colorbar — {var_name}  |  {cmap_short}"
        self.fig.text(0.5, 0.97, title, ha='center', va='top',
                      fontsize=7.5, color='#553300',
                      transform=self.fig.transFigure)
        self.fig.canvas.draw_idle()

    def _get_colors_list(self, cmap_name):
        if "Blue-Pink" in cmap_name:
            return [(0.05, 0.10, 0.70), (0.25, 0.50, 0.95),
                    (0.70, 0.60, 0.95), (0.95, 0.40, 0.75), (0.90, 0.10, 0.50)]
        elif "Rainbow" in cmap_name:
            return [(0, 0, 1), (0, 1, 1), (0, 1, 0), (1, 1, 0), (1, 0, 0)]
        elif "Hot" in cmap_name:
            return [(0, 0, 0), (0.5, 0, 0), (1, 0.2, 0), (1, 0.8, 0), (1, 1, 1)]
        elif "Cool" in cmap_name:
            return [(0, 1, 1), (1, 0, 1)]
        elif "Grayscale" in cmap_name:
            return [(0, 0, 0), (1, 1, 1)]
        elif "Jet" in cmap_name:
            return [(0, 0, 0.5), (0, 0.5, 1), (0, 1, 0.5), (1, 1, 0), (0.5, 0, 0)]
        elif "Viridis" in cmap_name:
            return [(0.27, 0.00, 0.33), (0.13, 0.37, 0.53),
                    (0.13, 0.57, 0.55), (0.37, 0.79, 0.38), (0.99, 0.91, 0.14)]
        elif "Ocean" in cmap_name:
            return [(0, 0, 0.2), (0, 0.2, 0.5), (0, 0.5, 0.8), (0.2, 0.8, 1), (0.9, 1, 1)]
        else:
            return [(0, 0, 1), (1, 0, 0)]


# ================================================================
#  TRANSFER FUNCTION EDITOR
# ================================================================
class TFCanvas(FigureCanvasQTAgg):
    def __init__(self, lo, hi, on_change_cb):
        self.fig = Figure(figsize=(3.2, 1.8), facecolor="#fffaf0")
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(155)
        self.lo = lo
        self.hi = hi
        self.on_change_cb = on_change_cb
        self._cmap_colors = None   # list of RGB tuples for current colormap
        self.points = [
            (0.00, 0.00), (0.25, 0.05), (0.50, 0.10), (0.75, 0.30), (1.00, 0.60),
        ]
        self._drag_idx = None
        self.mpl_connect("button_press_event", self._press)
        self.mpl_connect("motion_notify_event", self._motion)
        self.mpl_connect("button_release_event", self._release)
        self._draw_tf()

    def set_cmap_colors(self, colors_list):
        """Pass the current colormap color list so gradient bg can be drawn."""
        self._cmap_colors = colors_list
        self._draw_tf()

    def _draw_tf(self):
        self.fig.clear()
        # Single axes — the background IS the colormap gradient
        ax = self.fig.add_axes([0.10, 0.20, 0.86, 0.68])
        self._ax = ax

        # ── Draw colormap gradient as the axes background at FULL intensity ──
        if self._cmap_colors:
            cmap_bg = LinearSegmentedColormap.from_list("tfbg", self._cmap_colors, N=512)
            gradient = np.linspace(0, 1, 512).reshape(1, -1)
            ax.imshow(gradient, aspect='auto', cmap=cmap_bg,
                      vmin=0, vmax=1, interpolation='bilinear',
                      extent=[-0.02, 1.02, -0.02, 1.05], zorder=0)
            ax.set_facecolor('none')
        else:
            ax.set_facecolor("#fffef8")

        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        ax.fill_between(xs, ys, alpha=0.35, color='white', zorder=2)
        ax.plot(xs, ys, color='white', lw=2.0, zorder=3)
        ax.scatter(xs, ys, color='white', s=50, zorder=5,
                   edgecolors='#333333', linewidths=1.2, picker=5)
        ax.set_xlim(-0.02, 1.02)
        ax.set_ylim(-0.02, 1.05)
        ax.set_xlabel("Data value (normalized)", fontsize=7, color='#553300')
        ax.set_ylabel("Opacity", fontsize=7, color='#553300')
        ax.tick_params(labelsize=6, colors='#553300')
        ax.set_title("Opacity TF  (drag pts)", fontsize=6.5,
                     color='white' if self._cmap_colors else '#553300', pad=3,
                     fontweight='bold')
        for sp in ax.spines.values():
            sp.set_color('#ccaa88')
            sp.set_linewidth(0.8)
        xticks = [0, 0.25, 0.5, 0.75, 1.0]
        xlabels = [f"{self.lo + t*(self.hi-self.lo):.3g}" for t in xticks]
        ax.set_xticks(xticks)
        ax.set_xticklabels(xlabels, fontsize=6)
        ax.tick_params(colors='white' if self._cmap_colors else '#553300')
        ax.xaxis.label.set_color('white' if self._cmap_colors else '#553300')
        ax.yaxis.label.set_color('white' if self._cmap_colors else '#553300')
        self.fig.canvas.draw_idle()

    def _nearest_point(self, x, y):
        if not self.points:
            return None
        dists = [(abs(p[0]-x)**2 + abs(p[1]-y)**2) for p in self.points]
        idx = int(np.argmin(dists))
        return idx if dists[idx] < 0.02 else None

    def _press(self, event):
        if event.inaxes != self._ax:
            return
        idx = self._nearest_point(event.xdata, event.ydata)
        if idx is not None:
            self._drag_idx = idx
        else:
            x = float(np.clip(event.xdata, 0, 1))
            y = float(np.clip(event.ydata, 0, 1))
            self.points.append((x, y))
            self.points.sort(key=lambda p: p[0])
            self._draw_tf()
            self.on_change_cb(self.points)

    def _motion(self, event):
        if self._drag_idx is None:
            return
        if event.inaxes != self._ax:
            return
        x = float(np.clip(event.xdata, 0, 1))
        y = float(np.clip(event.ydata, 0, 1))
        if self._drag_idx == 0:
            x = 0.0
        if self._drag_idx == len(self.points)-1:
            x = 1.0
        self.points[self._drag_idx] = (x, y)
        self.points.sort(key=lambda p: p[0])
        self._draw_tf()
        self.on_change_cb(self.points)

    def _release(self, event):
        self._drag_idx = None

    def reset_default(self):
        self.points = [(0.0, 0.0), (0.25, 0.05), (0.50, 0.10), (0.75, 0.30), (1.0, 0.60)]
        self._draw_tf()
        self.on_change_cb(self.points)

    def set_range(self, lo, hi):
        self.lo = lo
        self.hi = hi
        self._draw_tf()

    def get_vtk_otf(self):
        otf = vtk.vtkPiecewiseFunction()
        for nx, op in self.points:
            val = self.lo + nx*(self.hi - self.lo)
            otf.AddPoint(val, op)
        return otf


# ================================================================
#  PCP CANVAS — Density-based Alpha
# ================================================================
class PCPCanvas(FigureCanvasQTAgg):
    BRUSH_THRESH = 0.18

    def __init__(self):
        self.fig = Figure(figsize=(9, 3.0), facecolor="white")
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._arrays_dict = {}
        self._label_val = 0.5
        self._title = ""
        self._ordered = []
        self._norm = {}
        self._lo = {}
        self._hi = {}
        self._idx = np.array([], dtype=int)
        self._line_color = (0.5, 0.5, 0.5)
        self.brushes = {}
        self._drag_axis = None
        self._drag_start_y = None
        self._brush_rect = None
        self.mpl_connect("button_press_event", self._on_press)
        self.mpl_connect("motion_notify_event", self._on_motion)
        self.mpl_connect("button_release_event", self._on_release)
        self.show_empty()

    def show_empty(self):
        self.fig.clear()
        self.fig.patch.set_facecolor("white")
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("white")
        ax.text(0.5, 0.5,
                "Select region using Sphere Widget\nthen click  Show Selection",
                ha="center", va="center", color="#999999",
                fontsize=12, transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        self.fig.canvas.draw_idle()
        self._ordered = []

    def show_pcp(self, arrays_dict, label_val=0.5, title=""):
        self._arrays_dict = arrays_dict
        self._label_val = label_val
        self._title = title
        self.brushes = {}
        self._redraw()

    def _compute_density_alphas(self, segs, n_ax, bins=20):
        if len(segs) == 0:
            return np.array([])
        all_x, all_y = [], []
        for seg in segs:
            for (x, y) in seg:
                all_x.append(x)
                all_y.append(y)
        all_x = np.array(all_x)
        all_y = np.array(all_y)
        H, xedges, yedges = np.histogram2d(
            all_x, all_y,
            bins=[max(n_ax, 2), bins],
            range=[[-0.5, n_ax - 0.5], [0.0, 1.0]]
        )
        H = H.astype(float)
        line_densities = []
        for seg in segs:
            d_vals = []
            for (x, y) in seg:
                xi = int(np.clip(np.searchsorted(xedges, x, side='right') - 1, 0, H.shape[0]-1))
                yi = int(np.clip(np.searchsorted(yedges, y, side='right') - 1, 0, H.shape[1]-1))
                d_vals.append(H[xi, yi])
            line_densities.append(np.mean(d_vals))
        line_densities = np.array(line_densities, dtype=float)
        d_min = line_densities.min()
        d_max = line_densities.max()
        if d_max - d_min < 1e-9:
            return np.full(len(segs), 0.18)
        norm_d = (line_densities - d_min) / (d_max - d_min)
        alphas = 0.55 - norm_d * 0.51
        return alphas

    def _redraw(self):
        arrays_dict = self._arrays_dict
        label_val = self._label_val
        title = self._title
        self.fig.clear()
        self.fig.patch.set_facecolor("white")
        ordered = [k for k in arrays_dict if len(arrays_dict[k]) > 0]
        if not ordered:
            self.show_empty()
            return
        n_ax = len(ordered)
        n_pts = len(arrays_dict[ordered[0]])
        if n_pts == 0:
            self.show_empty()
            return
        self._ordered = ordered
        raw = {f: np.array(arrays_dict[f], dtype=float) for f in ordered}
        lo = {f: raw[f].min() for f in ordered}
        hi = {f: raw[f].max() for f in ordered}
        norm = {f: (raw[f]-lo[f])/(hi[f]-lo[f]+1e-12) for f in ordered}
        self._lo = lo
        self._hi = hi
        self._norm = norm
        MAX_LINES = 1000
        idx = (np.random.choice(n_pts, MAX_LINES, replace=False)
               if n_pts > MAX_LINES else np.arange(n_pts))
        self._idx = idx
        lv = float(np.clip(label_val, 0, 1))
        if lv <= 0.5:
            t = lv/0.5
            lc = (t*0.85, 0.35+t*0.25, 0.85-t*0.55)
        else:
            t = (lv-0.5)/0.5
            lc = (0.85, 0.60-t*0.55, 0.30-t*0.25)
        self._line_color = lc
        active = self._active_mask(idx, ordered, norm)
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("white")
        self.fig.subplots_adjust(left=0.04, right=0.84, top=0.88, bottom=0.18)
        self._ax = ax
        xs = list(range(n_ax))
        active_segs = []
        inactive_segs = []
        for k, i in enumerate(idx):
            ys = [float(norm[f][i]) for f in ordered]
            seg = list(zip(xs, ys))
            if active[k]:
                active_segs.append(seg)
            else:
                inactive_segs.append(seg)
        if inactive_segs:
            inactive_alphas = self._compute_density_alphas(inactive_segs, n_ax)
            for seg, alpha_val in zip(inactive_segs, inactive_alphas):
                ax.add_collection(LineCollection([seg], colors=['#aaaaaa'],
                                                  alpha=float(alpha_val)*0.5,
                                                  linewidths=0.6, zorder=1))
        if active_segs:
            active_alphas = self._compute_density_alphas(active_segs, n_ax)
            for seg, alpha_val in zip(active_segs, active_alphas):
                ax.add_collection(LineCollection([seg], colors=[lc],
                                                  alpha=float(alpha_val),
                                                  linewidths=0.9, zorder=2))
        for j, f in enumerate(ordered):
            ax.axvline(j, color='#333333', lw=2.0, zorder=10)
            ax.text(j, 1.03, f"{hi[f]:.4g}", ha='center', va='bottom',
                    fontsize=7, color='#222222', fontweight='bold', zorder=11)
            ax.text(j, -0.03, f"{lo[f]:.4g}", ha='center', va='top',
                    fontsize=7, color='#222222', zorder=11)
            for t_pos in [0.25, 0.50, 0.75]:
                val = lo[f]+t_pos*(hi[f]-lo[f])
                ax.plot([j-0.04, j+0.04], [t_pos, t_pos],
                        color='#444444', lw=1.2, zorder=12)
                ax.text(j+0.06, t_pos, f"{val:.3g}", ha='left', va='center',
                        fontsize=6, color='#555555', zorder=12)
            ax.text(j, -0.17, f, ha='center', va='top', fontsize=9,
                    fontweight='bold', color='#111111', zorder=11)
        for j, (blo, bhi) in self.brushes.items():
            rect = mpatches.Rectangle(
                (j-0.06, blo), 0.12, bhi-blo,
                linewidth=1.5, edgecolor='#ffcc00',
                facecolor='#ffee0033', zorder=15)
            ax.add_patch(rect)
        cmap_lbl = LinearSegmentedColormap.from_list(
            'lbl', [(0, '#1155cc'), (0.5, '#ddaa00'), (1, '#cc1100')])
        sm = cm.ScalarMappable(cmap=cmap_lbl, norm=mcolors.Normalize(0, 1))
        sm.set_array([])
        cb = self.fig.colorbar(sm, ax=ax, fraction=0.022, pad=0.02, aspect=20)
        cb.set_label("Label  (0=stable  1=stalled)", color="#333333", fontsize=8)
        cb.ax.tick_params(colors="#444444", labelsize=7)
        n_active = int(active.sum())
        brush_info = f"  [brush: {n_active}/{len(idx)}]" if self.brushes else ""
        ax.set_xlim(-0.3, n_ax-0.7)
        ax.set_ylim(-0.22, 1.12)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color('#dddddd')
            sp.set_linewidth(0.5)
        ax.set_title(
            (title if title else
             f"PCP  n={n_pts} (showing {len(idx)})  label={label_val:.2f}")
            + brush_info,
            fontsize=10,
            color='#cc2200' if label_val > 0.5 else '#004499', pad=6)
        self.fig.canvas.draw_idle()

    def _active_mask(self, idx, ordered, norm):
        mask = np.ones(len(idx), dtype=bool)
        for j, f in enumerate(ordered):
            if j in self.brushes:
                blo, bhi = self.brushes[j]
                vals = norm[f][idx]
                mask &= (vals >= blo) & (vals <= bhi)
        return mask

    def _nearest_axis(self, xdata):
        if not self._ordered:
            return None, None
        dists = [abs(xdata - j) for j in range(len(self._ordered))]
        j = int(np.argmin(dists))
        return j, dists[j]

    def _on_press(self, event):
        if event.inaxes is None or not self._ordered:
            return
        j, dist = self._nearest_axis(event.xdata)
        if j is None or dist > self.BRUSH_THRESH:
            return
        self._drag_axis = j
        self._drag_start_y = event.ydata

    def _on_motion(self, event):
        if self._drag_axis is None or event.inaxes is None:
            return
        y0 = self._drag_start_y
        y1 = event.ydata
        j = self._drag_axis
        if self._brush_rect is not None:
            try:
                self._brush_rect.remove()
            except:
                pass
        self._brush_rect = mpatches.Rectangle(
            (j-0.06, min(y0, y1)), 0.12, max(abs(y1-y0), 0.005),
            linewidth=1.5, edgecolor='#ffcc00',
            facecolor='#ffee0055', zorder=20)
        self._ax.add_patch(self._brush_rect)
        self.fig.canvas.draw_idle()

    def _on_release(self, event):
        if self._drag_axis is None:
            return
        j = self._drag_axis
        y0 = self._drag_start_y
        y1 = event.ydata if event.ydata is not None else y0
        self._drag_axis = None
        self._drag_start_y = None
        self._brush_rect = None
        ylo = max(0.0, min(y0, y1))
        yhi = min(1.0, max(y0, y1))
        if abs(yhi-ylo) < 0.01:
            if j in self.brushes:
                del self.brushes[j]
        else:
            self.brushes[j] = (ylo, yhi)
        self._redraw()


# ================================================================
#  SPHERE ENTRY
# ================================================================
class SphereEntry:
    def __init__(self, widget, actor, pts, poly, verts, name):
        self.widget = widget
        self.actor = actor
        self.pts = pts
        self.poly = poly
        self.verts = verts
        self.name = name
        self.ids = []
        self.coords = []


# ================================================================
#  MAIN WINDOW
# ================================================================
class MainWindow(QMainWindow):

    ALL_VARS = ['P', 'TC', 'CLOUD', 'PRECIP', 'QCLOUD', 'QGRAUP',
                'QICE', 'QRAIN', 'QSNOW', 'QVAPOR', 'U', 'V', 'Velocity', 'W']

    STYLE = """
        QMainWindow,QWidget{background:#f5f5f5;color:#222222;
            font-family:Consolas,monospace;font-size:12px;}
        QTabWidget::pane{border:1px solid #bbbbcc;background:#ffffff;}
        QTabBar::tab{background:#e8e8f0;color:#444466;
            padding:5px 14px;border:1px solid #bbbbcc;margin-right:2px;}
        QTabBar::tab:selected{background:#ffffff;color:#1133aa;
            border-bottom:2px solid #3355cc;}
        QGroupBox{border:1px solid #aabbcc;border-radius:4px;
            margin-top:8px;color:#2244aa;font-weight:bold;
            padding:6px;background:#ffffff;}
        QGroupBox::title{subcontrol-origin:margin;left:8px;padding:0 4px;
            background:#ffffff;}
        QPushButton{background:#e8eaf6;border:1px solid #7788cc;
            color:#223388;border-radius:3px;padding:5px 10px;}
        QPushButton:hover{background:#d0d4f0;border-color:#3355bb;}
        QPushButton:pressed{background:#b8bfe8;}
        QPushButton:disabled{background:#eeeeee;color:#aaaaaa;border-color:#cccccc;}
        QLabel{background:transparent;border:none;color:#333355;}
        QCheckBox{color:#333366;spacing:5px;}
        QCheckBox::indicator{width:13px;height:13px;
            border:1px solid #7788aa;border-radius:2px;background:#ffffff;}
        QCheckBox::indicator:checked{background:#3355cc;}
        QSlider::groove:horizontal{height:4px;background:#ccccdd;border-radius:2px;}
        QSlider::handle:horizontal{background:#3355cc;width:12px;height:12px;
            border-radius:6px;margin:-4px 0;}
        QSlider::sub-page:horizontal{background:#6677cc;border-radius:2px;}
        QScrollArea{border:none;background:#f5f5f5;}
        QTextEdit{background:#ffffff;border:1px solid #aabbcc;
            color:#223344;font-size:10px;font-family:Consolas,monospace;}
        QDoubleSpinBox,QComboBox{background:#ffffff;border:1px solid #aabbcc;
            color:#223344;border-radius:2px;padding:2px 4px;}
        QComboBox QAbstractItemView{background:#ffffff;color:#223344;
            selection-background-color:#d0d8f0;}
        QLineEdit{background:#ffffff;border:1px solid #aabbcc;
            color:#223344;border-radius:2px;padding:3px 5px;}
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Data Selection — Isabel Dataset")
        self.resize(1680, 960)
        self.setStyleSheet(self.STYLE)
        self.img = None
        self.arrays = {}
        self.center = [0, 0, 0]
        self.max_ext = 10.0
        self.spheres = []
        self.samples = []
        self.save_path = None
        self.orient_mk = None
        self.iso_boxes = []
        self.iso_count = 0
        self.pcp_var_checks = {}
        self.vol_actor = None
        # NEW: separate enable flags
        self._iso_enabled = True
        self._vol_enabled = False
        self._build_ui()
        self._setup_vtk()

    # ------------------------------------------------------------------
    #  UI BUILD
    # ------------------------------------------------------------------
    def _build_ui(self):
        c = QWidget()
        self.setCentralWidget(c)
        root = QHBoxLayout(c)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(4)

        # ── LEFT: VTK + PCP ──
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)
        lv.setSpacing(4)
        self.vtk_widget = QVTKRenderWindowInteractor()
        self.vtk_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lv.addWidget(self.vtk_widget, 3)
        self.tabs = QTabWidget()
        self.tabs.setMinimumHeight(260)
        self.pcp = PCPCanvas()
        self.tabs.addTab(self.pcp, "PCP")
        self.out_text = QTextEdit()
        self.out_text.setReadOnly(True)
        self.out_text.setPlaceholderText("Output preview...\nFormat: X  Y  Z  Label")
        self.tabs.addTab(self.out_text, "Output Preview")
        lv.addWidget(self.tabs, 2)
        root.addWidget(left, 3)

        # ── MIDDLE PANEL ──
        mid_scroll = QScrollArea()
        mid_scroll.setWidgetResizable(True)
        mid_scroll.setFixedWidth(370)
        mid_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        panel = QWidget()
        self.pv = QVBoxLayout(panel)
        self.pv.setContentsMargins(6, 6, 6, 6)
        self.pv.setSpacing(8)

        tl = QLabel("Isabel Dataset — Isosurface & Volume Rendering")
        tl.setAlignment(Qt.AlignCenter)
        tl.setStyleSheet("color:#1133cc;font-size:13px;font-weight:bold;"
                         "padding:5px;border-bottom:1px solid #aabbcc;")
        self.pv.addWidget(tl)

        # Data group
        g1 = QGroupBox("Data")
        v1 = QVBoxLayout(g1)
        v1.setSpacing(5)
        self.file_lbl = QLabel("No file loaded")
        self.file_lbl.setWordWrap(True)
        self.file_lbl.setStyleSheet("color:#335566;font-size:10px;")
        v1.addWidget(self.file_lbl)
        self.load_btn = QPushButton("Load Data  (.vti)")
        self.load_btn.setStyleSheet(
            "background:#ddeeff;border-color:#3366bb;color:#1133aa;font-weight:bold;padding:7px;")
        self.load_btn.clicked.connect(self._load_data)
        v1.addWidget(self.load_btn)
        self.arr_status = QLabel("Variables: not loaded")
        self.arr_status.setWordWrap(True)
        self.arr_status.setStyleSheet("color:#335566;font-size:10px;")
        v1.addWidget(self.arr_status)
        self.pv.addWidget(g1)

        # ── COMBINED MODE GROUP ──
        mode_group = QGroupBox("Rendering Mode  (can enable BOTH simultaneously)")
        mv = QVBoxLayout(mode_group)
        mv.setSpacing(6)
        mv.setContentsMargins(8, 8, 8, 8)

        mode_hint = QLabel("✓ Check one or both modes. They work independently and together.")
        mode_hint.setWordWrap(True)
        mode_hint.setStyleSheet("color:#445566;font-size:10px;padding:2px;")
        mv.addWidget(mode_hint)

        # Isosurface checkbox row
        iso_hdr_row = QHBoxLayout()
        self.iso_enable_cb = QCheckBox("  ● Isosurface Mode")
        self.iso_enable_cb.setChecked(True)
        self.iso_enable_cb.setStyleSheet(
            "QCheckBox{color:#1133aa;font-weight:bold;font-size:12px;}"
            "QCheckBox::indicator{width:16px;height:16px;"
            "border:2px solid #3366bb;border-radius:3px;background:#ddeeff;}"
            "QCheckBox::indicator:checked{background:#3366bb;}")
        self.iso_enable_cb.stateChanged.connect(self._on_iso_enable_changed)
        iso_hdr_row.addWidget(self.iso_enable_cb)
        iso_hdr_row.addStretch()
        mv.addLayout(iso_hdr_row)

        # Isosurface sub-panel
        self.iso_subpanel = QWidget()
        iso_sp_lay = QVBoxLayout(self.iso_subpanel)
        iso_sp_lay.setContentsMargins(4, 2, 4, 2)
        iso_sp_lay.setSpacing(4)
        self.iso_add_btn = QPushButton("＋   Add New Isosurface")
        self.iso_add_btn.setEnabled(False)
        self.iso_add_btn.setFixedHeight(34)
        self.iso_add_btn.setStyleSheet(
            "QPushButton{background:#e0f0e0;border:2px solid #338833;"
            "color:#1a5e1a;font-weight:bold;font-size:12px;border-radius:4px;}"
            "QPushButton:hover{background:#cceecc;}"
            "QPushButton:disabled{background:#eee;border-color:#cdc;color:#888;}")
        self.iso_add_btn.clicked.connect(self._add_iso_box)
        iso_sp_lay.addWidget(self.iso_add_btn)
        inner_sc = QScrollArea()
        inner_sc.setWidgetResizable(True)
        inner_sc.setMinimumHeight(60)
        inner_sc.setMaximumHeight(340)
        inner_sc.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        inner_sc.setStyleSheet("QScrollArea{border:1px solid #aabbcc;border-radius:3px;}")
        self.iso_boxes_container = QWidget()
        self.iso_boxes_layout = QVBoxLayout(self.iso_boxes_container)
        self.iso_boxes_layout.setContentsMargins(2, 2, 2, 2)
        self.iso_boxes_layout.setSpacing(6)
        self.iso_boxes_layout.addStretch()
        inner_sc.setWidget(self.iso_boxes_container)
        iso_sp_lay.addWidget(inner_sc)
        mv.addWidget(self.iso_subpanel)

        # Separator
        sep_line = QFrame()
        sep_line.setFrameShape(QFrame.HLine)
        sep_line.setStyleSheet("background:#ccccdd;max-height:1px;")
        mv.addWidget(sep_line)

        # Volume checkbox row
        vol_hdr_row = QHBoxLayout()
        self.vol_enable_cb = QCheckBox("  ◎ Volume Rendering Mode")
        self.vol_enable_cb.setChecked(False)
        self.vol_enable_cb.setStyleSheet(
            "QCheckBox{color:#883300;font-weight:bold;font-size:12px;}"
            "QCheckBox::indicator{width:16px;height:16px;"
            "border:2px solid #bb6633;border-radius:3px;background:#fff8f0;}"
            "QCheckBox::indicator:checked{background:#bb6633;}")
        self.vol_enable_cb.stateChanged.connect(self._on_vol_enable_changed)
        vol_hdr_row.addWidget(self.vol_enable_cb)
        vol_hdr_row.addStretch()
        mv.addLayout(vol_hdr_row)

        # Volume sub-panel
        self.vol_subpanel = QWidget()
        self.vol_subpanel.setVisible(False)
        vsp_lay = QVBoxLayout(self.vol_subpanel)
        vsp_lay.setContentsMargins(4, 2, 4, 4)
        vsp_lay.setSpacing(5)

        vsp_lay.addWidget(self._lbl2("Variable:"))
        self.vol_var_cb = QComboBox()
        self.vol_var_cb.addItems(self.ALL_VARS)
        self.vol_var_cb.setFixedHeight(24)
        self.vol_var_cb.currentTextChanged.connect(self._on_vol_var_changed)
        vsp_lay.addWidget(self.vol_var_cb)

        vsp_lay.addWidget(self._lbl2("Colormap:"))
        self.vol_cmap_cb = QComboBox()
        self.vol_cmap_cb.addItems([
            "Blue-Pink (blue->pink)",
            "Rainbow (blue->red)",
            "Hot (black->red->yellow->white)",
            "Cool (cyan->magenta)",
            "Grayscale",
            "Jet",
            "Viridis (blue->green->yellow)",
            "Ocean (blue tones)",
        ])
        self.vol_cmap_cb.setFixedHeight(24)
        self.vol_cmap_cb.currentTextChanged.connect(self._on_cmap_changed)
        vsp_lay.addWidget(self.vol_cmap_cb)

        # ── COLORBAR DISPLAY ──
        cbar_lbl = QLabel("Colorbar:")
        cbar_lbl.setStyleSheet("color:#883300;font-weight:bold;font-size:11px;")
        vsp_lay.addWidget(cbar_lbl)
        self.colorbar_canvas = ColorbarCanvas()
        vsp_lay.addWidget(self.colorbar_canvas)

        tf_hdr = QLabel("Opacity Transfer Function:")
        tf_hdr.setStyleSheet("color:#883300;font-weight:bold;font-size:11px;")
        vsp_lay.addWidget(tf_hdr)
        tf_hint = QLabel("• Drag points to change opacity\n"
                         "• Click empty area to add point\n"
                         "• X-axis = data value, Y-axis = opacity")
        tf_hint.setStyleSheet("color:#886644;font-size:9px;")
        vsp_lay.addWidget(tf_hint)
        self.tf_canvas = TFCanvas(0.0, 1.0, self._on_tf_changed)
        vsp_lay.addWidget(self.tf_canvas)
        tf_reset_btn = QPushButton("Reset Transfer Function")
        tf_reset_btn.setFixedHeight(24)
        tf_reset_btn.setStyleSheet(
            "QPushButton{background:#fff8f0;border:1px solid #cc9944;"
            "color:#885500;font-size:10px;border-radius:3px;}"
            "QPushButton:hover{background:#ffe8cc;}")
        tf_reset_btn.clicked.connect(self._reset_tf)
        vsp_lay.addWidget(tf_reset_btn)

        # ── IMPORT DATA FILE (txt / csv / xml) ──
        imp_hdr = QLabel("Import Data File:")
        imp_hdr.setStyleSheet("color:#334488;font-weight:bold;font-size:11px;margin-top:4px;")
        vsp_lay.addWidget(imp_hdr)
        imp_hint = QLabel("Supported: .txt  .csv  .xml\n"
                          "Imported data is shown in Output Preview tab.")
        imp_hint.setStyleSheet("color:#445577;font-size:9px;padding:3px;"
                               "border:1px solid #aabbcc;border-radius:2px;background:#eef4ff;")
        imp_hint.setWordWrap(True)
        vsp_lay.addWidget(imp_hint)
        imp_row = QHBoxLayout()
        self.imp_browse_btn = QPushButton("📂  Browse & Import File")
        self.imp_browse_btn.setFixedHeight(28)
        self.imp_browse_btn.setStyleSheet(
            "QPushButton{background:#e8eeff;border:2px solid #5566cc;"
            "color:#223388;font-weight:bold;font-size:10px;border-radius:3px;}"
            "QPushButton:hover{background:#d0d8f8;border-color:#3344bb;}")
        self.imp_browse_btn.clicked.connect(self._browse_import_file)
        imp_row.addWidget(self.imp_browse_btn)
        self.imp_clear_btn = QPushButton("✕")
        self.imp_clear_btn.setFixedSize(28, 28)
        self.imp_clear_btn.setStyleSheet(
            "QPushButton{background:#ffe8e8;border:1px solid #cc4444;"
            "color:#cc2222;font-size:12px;border-radius:3px;padding:0;}"
            "QPushButton:hover{background:#ffcccc;}")
        self.imp_clear_btn.clicked.connect(self._clear_import_file)
        imp_row.addWidget(self.imp_clear_btn)
        vsp_lay.addLayout(imp_row)
        self.imp_status_lbl = QLabel("No file imported.")
        self.imp_status_lbl.setWordWrap(True)
        self.imp_status_lbl.setStyleSheet(
            "color:#445577;font-size:9px;padding:2px 3px;"
            "border:1px solid #aabbcc;border-radius:2px;background:#f8f8ff;")
        vsp_lay.addWidget(self.imp_status_lbl)
        # custom CTF not used from file import — reset
        self._custom_ctf_points = None

        self.vol_apply_btn = QPushButton("▶  Apply Volume Rendering")
        self.vol_apply_btn.setEnabled(False)
        self.vol_apply_btn.setFixedHeight(32)
        self.vol_apply_btn.setStyleSheet(
            "QPushButton{background:#fff0e0;border:2px solid #bb6633;"
            "color:#883300;font-weight:bold;border-radius:3px;font-size:12px;}"
            "QPushButton:hover{background:#ffe0c0;}"
            "QPushButton:disabled{background:#f0f0f0;border-color:#ccc;color:#aaa;}")
        self.vol_apply_btn.clicked.connect(self._apply_volume)
        vsp_lay.addWidget(self.vol_apply_btn)

        self.vol_remove_btn = QPushButton("Remove Volume")
        self.vol_remove_btn.setEnabled(False)
        self.vol_remove_btn.setFixedHeight(26)
        self.vol_remove_btn.setStyleSheet(
            "QPushButton{background:#ffe8e8;border:1px solid #cc4444;"
            "color:#cc2222;border-radius:3px;}"
            "QPushButton:hover{background:#ffcccc;}"
            "QPushButton:disabled{background:#f0f0f0;border-color:#ccc;color:#aaa;}")
        self.vol_remove_btn.clicked.connect(self._remove_volume)
        vsp_lay.addWidget(self.vol_remove_btn)

        self.vol_status_lbl = QLabel("Volume: not applied")
        self.vol_status_lbl.setStyleSheet(
            "color:#886644;font-size:10px;padding:2px 3px;"
            "border:1px solid #ddccaa;border-radius:2px;background:#fffaf0;")
        self.vol_status_lbl.setWordWrap(True)
        vsp_lay.addWidget(self.vol_status_lbl)

        # ── SHADE ON / OFF ──
        shade_sep = QFrame()
        shade_sep.setFrameShape(QFrame.HLine)
        shade_sep.setStyleSheet("background:#ddccaa;max-height:1px;margin:3px 0;")
        vsp_lay.addWidget(shade_sep)
        shade_hdr = QLabel("Surface Shading:")
        shade_hdr.setStyleSheet("color:#883300;font-weight:bold;font-size:11px;")
        vsp_lay.addWidget(shade_hdr)
        shade_hint = QLabel("Shade ON = shiny/glossy surface\nShade OFF = flat/matte surface")
        shade_hint.setStyleSheet("color:#886644;font-size:9px;")
        vsp_lay.addWidget(shade_hint)
        shade_row = QHBoxLayout()
        self.shade_on_cb = QCheckBox("Shade ON  (shiny)")
        self.shade_on_cb.setChecked(True)
        self.shade_on_cb.setStyleSheet(
            "QCheckBox{color:#1a5e1a;font-weight:bold;font-size:11px;padding:3px;}"
            "QCheckBox::indicator{width:15px;height:15px;"
            "border:2px solid #338833;border-radius:3px;background:#e8f5e8;}"
            "QCheckBox::indicator:checked{background:#338833;}")
        self.shade_on_cb.stateChanged.connect(self._on_shade_changed)
        shade_row.addWidget(self.shade_on_cb)
        self.shade_off_cb = QCheckBox("Shade OFF  (matte)")
        self.shade_off_cb.setChecked(False)
        self.shade_off_cb.setStyleSheet(
            "QCheckBox{color:#883300;font-weight:bold;font-size:11px;padding:3px;}"
            "QCheckBox::indicator{width:15px;height:15px;"
            "border:2px solid #bb6633;border-radius:3px;background:#fff8f0;}"
            "QCheckBox::indicator:checked{background:#bb6633;}")
        self.shade_off_cb.stateChanged.connect(self._on_shade_changed)
        shade_row.addWidget(self.shade_off_cb)
        vsp_lay.addLayout(shade_row)

        mv.addWidget(self.vol_subpanel)
        self.pv.addWidget(mode_group)

        # Sphere Selection group
        g4 = QGroupBox("Sphere Selection  (→ PCP)")
        v4 = QVBoxLayout(g4)
        v4.setSpacing(5)
        self.add_sph_btn = QPushButton("Add New Sphere Widget")
        self.add_sph_btn.setEnabled(False)
        self.add_sph_btn.setStyleSheet(
            "background:#e8f5e8;border-color:#338833;color:#1a5e1a;font-weight:bold;padding:6px;")
        self.add_sph_btn.clicked.connect(self._add_sphere)
        v4.addWidget(self.add_sph_btn)
        self.active_lbl = QLabel("Active: -")
        self.active_lbl.setStyleSheet("color:#cc6600;font-size:11px;")
        v4.addWidget(self.active_lbl)
        rr = QHBoxLayout()
        rr.addWidget(QLabel("Radius:"))
        self.rad_sl = QSlider(Qt.Horizontal)
        self.rad_sl.setRange(1, 500)
        self.rad_sl.setValue(20)
        self.rad_sl.valueChanged.connect(self._on_radius)
        rr.addWidget(self.rad_sl)
        self.rad_lbl = QLabel("20")
        self.rad_lbl.setFixedWidth(30)
        rr.addWidget(self.rad_lbl)
        v4.addLayout(rr)
        self.clear_brush_btn = QPushButton("Clear All Brushes")
        self.clear_brush_btn.setStyleSheet(
            "background:#eef0ff;border-color:#6677aa;color:#223366;padding:4px;")
        self.clear_brush_btn.clicked.connect(self._clear_brushes)
        v4.addWidget(self.clear_brush_btn)
        rsb = QHBoxLayout()
        self.sel_btn = QPushButton("Show Selection")
        self.sel_btn.setEnabled(False)
        self.sel_btn.setStyleSheet(
            "background:#e8f5e8;border-color:#338833;color:#1a5e1a;font-weight:bold;")
        self.sel_btn.clicked.connect(self._show_selection)
        rsb.addWidget(self.sel_btn)
        self.clr_btn = QPushButton("Clear")
        self.clr_btn.clicked.connect(self._clear_all)
        rsb.addWidget(self.clr_btn)
        v4.addLayout(rsb)
        self.rem_btn = QPushButton("Remove Last Sphere")
        self.rem_btn.clicked.connect(self._remove_last)
        v4.addWidget(self.rem_btn)
        v4.addWidget(QLabel("Label  (0=stable  1=stalled):"))
        rst = QHBoxLayout()
        self.lbl_sl = QSlider(Qt.Horizontal)
        self.lbl_sl.setRange(0, 100)
        self.lbl_sl.setValue(50)
        rst.addWidget(self.lbl_sl)
        self.lbl_val = QLabel("0.50")
        self.lbl_val.setFixedWidth(35)
        rst.addWidget(self.lbl_val)
        self.lbl_sl.valueChanged.connect(lambda v: self.lbl_val.setText(f"{v/100:.2f}"))
        v4.addLayout(rst)
        self.sph_list_lbl = QLabel("Spheres: none")
        self.sph_list_lbl.setWordWrap(True)
        self.sph_list_lbl.setStyleSheet(
            "color:#334455;font-size:10px;padding:3px;border:1px solid #aabbcc;border-radius:3px;")
        v4.addWidget(self.sph_list_lbl)
        self.pv.addWidget(g4)

        # Save Output group
        g5 = QGroupBox("Save Output  (X  Y  Z  Label)")
        v5 = QVBoxLayout(g5)
        v5.setSpacing(6)
        self.path_lbl = QLabel("File: not created yet")
        self.path_lbl.setWordWrap(True)
        self.path_lbl.setStyleSheet(
            "color:#335577;font-size:10px;padding:3px;border:1px solid #aabbcc;border-radius:3px;")
        v5.addWidget(self.path_lbl)
        self.addlist_btn = QPushButton("Add to List  (save / append)")
        self.addlist_btn.setStyleSheet(
            "background:#e8f5e8;border-color:#338833;color:#1a5e1a;font-weight:bold;padding:8px;font-size:13px;")
        self.addlist_btn.clicked.connect(self._add_to_list)
        v5.addWidget(self.addlist_btn)
        self.sample_count = QLabel("Total saved: 0 rows")
        self.sample_count.setStyleSheet("color:#335566;font-size:10px;")
        v5.addWidget(self.sample_count)
        self.pv.addWidget(g5)

        self.info = QLabel("Load a .vti file to begin.")
        self.info.setWordWrap(True)
        self.info.setStyleSheet(
            "color:#335566;font-size:10px;padding:5px;border:1px solid #aabbcc;border-radius:3px;")
        self.pv.addWidget(self.info)
        self.pv.addStretch()
        mid_scroll.setWidget(panel)
        root.addWidget(mid_scroll, 0)

        # ── RIGHT PANEL: PCP variable checkboxes ──
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFixedWidth(160)
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        right_panel = QWidget()
        right_panel.setStyleSheet("background:#ffffff;")
        rv = QVBoxLayout(right_panel)
        rv.setContentsMargins(6, 6, 6, 6)
        rv.setSpacing(4)
        pcp_hdr = QLabel("PCP Variables")
        pcp_hdr.setAlignment(Qt.AlignCenter)
        pcp_hdr.setStyleSheet(
            "color:#1133cc;font-weight:bold;font-size:12px;"
            "padding:4px;border-bottom:1px solid #aabbcc;"
            "background:#eef2ff;border-radius:3px;")
        rv.addWidget(pcp_hdr)
        hint = QLabel("✓ = show in PCP\nUncheck to hide")
        hint.setStyleSheet("color:#667788;font-size:9px;padding:2px;")
        rv.addWidget(hint)
        sa_row = QHBoxLayout()
        all_btn = QPushButton("All")
        all_btn.setFixedHeight(22)
        all_btn.setStyleSheet("font-size:10px;padding:2px;")
        all_btn.clicked.connect(self._pcp_check_all)
        sa_row.addWidget(all_btn)
        none_btn = QPushButton("None")
        none_btn.setFixedHeight(22)
        none_btn.setStyleSheet("font-size:10px;padding:2px;")
        none_btn.clicked.connect(self._pcp_check_none)
        sa_row.addWidget(none_btn)
        rv.addLayout(sa_row)
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("background:#cccccc;max-height:1px;")
        rv.addWidget(sep2)
        self.pcp_checks_widget = QWidget()
        self.pcp_checks_layout = QVBoxLayout(self.pcp_checks_widget)
        self.pcp_checks_layout.setContentsMargins(2, 2, 2, 2)
        self.pcp_checks_layout.setSpacing(3)
        self._build_pcp_checkboxes(self.ALL_VARS)
        rv.addWidget(self.pcp_checks_widget)
        rv.addStretch()
        right_scroll.setWidget(right_panel)
        root.addWidget(right_scroll, 0)

    def _lbl2(self, t):
        l = QLabel(t)
        l.setStyleSheet("color:#445566;font-size:10px;")
        return l

    # ------------------------------------------------------------------
    #  ISO / VOLUME ENABLE CALLBACKS
    # ------------------------------------------------------------------
    def _on_iso_enable_changed(self, state):
        self._iso_enabled = bool(state)
        self.iso_subpanel.setVisible(self._iso_enabled)
        if self._iso_enabled:
            # Show all drawn isosurfaces
            for box in self.iso_boxes:
                if box.entry and box.show_cb.isChecked():
                    box.entry.actor.SetVisibility(True)
                    box.entry.edge_actor.SetVisibility(True)
        else:
            # Hide all isosurfaces
            for box in self.iso_boxes:
                if box.entry:
                    box.entry.actor.SetVisibility(False)
                    box.entry.edge_actor.SetVisibility(False)
            # Clear PCP plot when isosurface disabled
            self.pcp.show_empty()
            self._info("Isosurface Mode OFF\n  PCP cleared (no selection context).")
        self._ren()

    def _on_vol_enable_changed(self, state):
        self._vol_enabled = bool(state)
        self.vol_subpanel.setVisible(self._vol_enabled)
        if self._vol_enabled:
            # Show volume if exists
            if self.vol_actor:
                self.vol_actor.VisibilityOn()
            self._info("Volume Mode ON\n  Choose Variable + Colormap → Apply.")
        else:
            # Hide volume
            if self.vol_actor:
                self.vol_actor.VisibilityOff()
            self._info("Volume Mode OFF\n  Volume hidden (isosurface still active if checked).")
        self._ren()

    def _on_shade_changed(self, state):
        """Toggle shade on/off — keep the two checkboxes mutually exclusive."""
        if not state:
            return   # ignore uncheck signals; only react to the one being checked
        sender = self.sender()
        if sender is self.shade_on_cb:
            self.shade_off_cb.blockSignals(True)
            self.shade_off_cb.setChecked(False)
            self.shade_off_cb.blockSignals(False)
        else:
            self.shade_on_cb.blockSignals(True)
            self.shade_on_cb.setChecked(False)
            self.shade_on_cb.blockSignals(False)
        # Live-update volume if already rendered
        if self.vol_actor and self._vol_enabled:
            self._apply_volume(silent=True)

    # ------------------------------------------------------------------
    #  IMPORT DATA FILE (txt / csv / xml)
    # ------------------------------------------------------------------
    def _browse_import_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Data File", "",
            "Data Files (*.txt *.csv *.xml);;Text Files (*.txt);;CSV Files (*.csv);;XML Files (*.xml);;All Files (*)")
        if not path:
            return
        self._do_import_file(path)

    def _do_import_file(self, path):
        fname = os.path.basename(path)
        ext = os.path.splitext(fname)[1].lower()
        try:
            lines_preview = []
            row_count = 0
            if ext == '.xml':
                import xml.etree.ElementTree as ET
                tree = ET.parse(path)
                root_el = tree.getroot()
                # Flatten all text content for preview
                for elem in root_el.iter():
                    text = (elem.text or "").strip()
                    if text:
                        lines_preview.append(f"<{elem.tag}>: {text}")
                        row_count += 1
            else:
                # txt / csv
                with open(path, 'r', errors='replace') as f:
                    all_lines = f.readlines()
                row_count = len(all_lines)
                lines_preview = all_lines[:60]
            preview_text = (f"# Imported: {fname}\n"
                            f"# Rows/entries: {row_count}\n"
                            f"# Format: {ext.upper()}\n"
                            "# " + "-"*50 + "\n")
            preview_text += "".join(lines_preview)
            if row_count > 60:
                preview_text += f"\n... ({row_count} total rows)"
            self.out_text.setPlainText(preview_text)
            self.tabs.setCurrentIndex(1)
            self.imp_status_lbl.setText(
                f"✓ Imported: {fname}\n  {row_count} rows  |  {ext.upper()}")
            self.imp_status_lbl.setStyleSheet(
                "color:#115511;font-size:9px;padding:2px 3px;"
                "border:1px solid #88bb88;border-radius:2px;background:#eeffee;")
            self._info(f"File imported!\n  {fname}\n  {row_count} rows  ({ext.upper()})\n"
                       f"  See Output Preview tab.")
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to read file:\n{e}")

    def _clear_import_file(self):
        self.imp_status_lbl.setText("No file imported.")
        self.imp_status_lbl.setStyleSheet(
            "color:#445577;font-size:9px;padding:2px 3px;"
            "border:1px solid #aabbcc;border-radius:2px;background:#f8f8ff;")
        self._info("Import cleared.")

    # ------------------------------------------------------------------
    #  PCP CHECKBOXES
    # ------------------------------------------------------------------
    def _build_pcp_checkboxes(self, var_list):
        for i in reversed(range(self.pcp_checks_layout.count())):
            w = self.pcp_checks_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
        self.pcp_var_checks = {}
        for var in var_list:
            cb = QCheckBox(var)
            cb.setChecked(True)
            cb.setStyleSheet(
                "QCheckBox{color:#223344;font-size:11px;padding:2px;}"
                "QCheckBox::indicator{width:14px;height:14px;"
                "border:1px solid #7788aa;border-radius:2px;background:#fff;}"
                "QCheckBox::indicator:checked{background:#3355cc;}")
            cb.stateChanged.connect(self._on_pcp_check_changed)
            self.pcp_checks_layout.addWidget(cb)
            self.pcp_var_checks[var] = cb

    def _pcp_check_all(self):
        for cb in self.pcp_var_checks.values():
            cb.setChecked(True)

    def _pcp_check_none(self):
        for cb in self.pcp_var_checks.values():
            cb.setChecked(False)

    def _on_pcp_check_changed(self):
        if self.pcp._arrays_dict:
            self._refresh_pcp()

    def _get_pcp_vars(self):
        return [v for v, cb in self.pcp_var_checks.items()
                if cb.isChecked() and v in self.arrays]

    def _refresh_pcp(self):
        if not self.spheres:
            return
        pcp_vars = self._get_pcp_vars()
        if not pcp_vars:
            return
        collected = {v: [] for v in pcp_vars}
        total_ids = []
        for entry in self.spheres:
            total_ids.extend(entry.ids)
            for v in pcp_vars:
                if v in self.arrays:
                    collected[v].extend(self.arrays[v][entry.ids].tolist())
        lv = self.lbl_sl.value()/100.0
        arr_dict = {v: np.array(collected[v]) for v in pcp_vars if len(collected[v]) > 0}
        if arr_dict:
            self.pcp.show_pcp(arr_dict, label_val=lv,
                              title=f"PCP  n={len(total_ids)}  label={lv:.2f}")

    # ------------------------------------------------------------------
    #  VTK SETUP
    # ------------------------------------------------------------------
    def _setup_vtk(self):
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0.95, 0.95, 0.98)
        self.ren.GradientBackgroundOn()
        self.ren.SetBackground2(0.85, 0.88, 0.95)
        rw = self.vtk_widget.GetRenderWindow()
        rw.AddRenderer(self.ren)
        self.iren = rw.GetInteractor()
        self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.iren.Initialize()

    def _ren(self):
        self.vtk_widget.GetRenderWindow().Render()

    def _info(self, t):
        self.info.setText(t)

    # ------------------------------------------------------------------
    #  LOAD DATA
    # ------------------------------------------------------------------
    def _load_data(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select VTI File", "", "VTI Files (*.vti);;All Files (*)")
        if not path:
            return
        rd = vtk.vtkXMLImageDataReader()
        rd.SetFileName(path)
        rd.Update()
        self.img = rd.GetOutput()
        b = self.img.GetBounds()
        dims = self.img.GetDimensions()
        self.center = [(b[0]+b[1])/2, (b[2]+b[3])/2, (b[4]+b[5])/2]
        self.max_ext = max(b[1]-b[0], b[3]-b[2], b[5]-b[4])
        self.arrays = {}
        pd = self.img.GetPointData()
        for i in range(pd.GetNumberOfArrays()):
            a = pd.GetArray(i)
            if a:
                self.arrays[a.GetName()] = vtk_to_numpy(a)
        self.arr_status.setText(
            f"Variables ({len(self.arrays)}): " + ", ".join(self.arrays.keys()))
        self.rad_sl.setRange(1, max(1, int(self.max_ext*0.55)))
        self.rad_sl.setValue(max(1, int(self.max_ext*0.13)))
        self.rad_lbl.setText(str(self.rad_sl.value()))
        self.iso_add_btn.setEnabled(True)
        self.add_sph_btn.setEnabled(True)
        self.sel_btn.setEnabled(True)
        self.vol_apply_btn.setEnabled(True)
        self.vol_var_cb.clear()
        self.vol_var_cb.addItems(list(self.arrays.keys()))
        self._build_pcp_checkboxes(list(self.arrays.keys()))
        if self.vol_actor:
            self.ren.RemoveVolume(self.vol_actor)
            self.vol_actor = None
        self.vol_remove_btn.setEnabled(False)
        self.vol_status_lbl.setText("Volume: not applied")
        for box in self.iso_boxes:
            if box.entry:
                self.ren.RemoveActor(box.entry.actor)
                self.ren.RemoveActor(box.entry.edge_actor)
            box.deleteLater()
        self.iso_boxes.clear()
        self.iso_count = 0
        self.spheres.clear()
        self._upd_sph_list()
        self.ren.RemoveAllViewProps()
        of = vtk.vtkOutlineFilter()
        of.SetInputData(self.img)
        om = vtk.vtkPolyDataMapper()
        om.SetInputConnection(of.GetOutputPort())
        oa = vtk.vtkActor()
        oa.SetMapper(om)
        oa.GetProperty().SetColor(0.3, 0.3, 0.8)
        oa.GetProperty().SetLineWidth(1.5)
        self.ren.AddActor(oa)
        if self.orient_mk:
            self.orient_mk.SetEnabled(False)
        axact = vtk.vtkAxesActor()
        self.orient_mk = vtk.vtkOrientationMarkerWidget()
        self.orient_mk.SetOrientationMarker(axact)
        self.orient_mk.SetInteractor(self.iren)
        self.orient_mk.SetViewport(0, 0, 0.18, 0.18)
        self.orient_mk.EnabledOn()
        self.orient_mk.InteractiveOff()
        self.ren.ResetCamera()
        self._ren()
        fname = os.path.basename(path)
        self.file_lbl.setText(f"OK  {fname}")
        self._info(f"Loaded: {fname}\nDims: {dims}\n"
                   f"Variables: {list(self.arrays.keys())}")

    # ------------------------------------------------------------------
    #  ISOSURFACE
    # ------------------------------------------------------------------
    def _add_iso_box(self):
        self.iso_count += 1
        color = ISO_COLORS[(self.iso_count-1) % len(ISO_COLORS)]
        vars_list = list(self.arrays.keys()) if self.arrays else self.ALL_VARS
        box = IsoInputBox(idx=self.iso_count, color=color,
                          all_vars=vars_list, arrays=self.arrays, parent_win=self)
        self.iso_boxes.append(box)
        self.iso_boxes_layout.insertWidget(self.iso_boxes_layout.count()-1, box)
        self._info(f"Isosurface #{self.iso_count} added!\n  Choose variable → Draw")

    def _draw_iso_box(self, box: IsoInputBox):
        if self.img is None:
            self._info("Load data first!")
            return
        if not self._iso_enabled:
            self._info("Enable Isosurface Mode first!")
            return
        var_name = box.var_cb.currentText()
        iso_val = box.val_sp.value()
        opac = box.opac_sl.value() / 100.0
        color = box.color
        if var_name not in self.arrays:
            self._info(f"Variable '{var_name}' not found!")
            return
        if box.entry:
            self.ren.RemoveActor(box.entry.actor)
            self.ren.RemoveActor(box.entry.edge_actor)
        img_copy = vtk.vtkImageData()
        img_copy.DeepCopy(self.img)
        img_copy.GetPointData().SetActiveScalars(var_name)
        contour = vtk.vtkContourFilter()
        contour.SetInputData(img_copy)
        contour.SetValue(0, iso_val)
        smoother = vtk.vtkSmoothPolyDataFilter()
        smoother.SetInputConnection(contour.GetOutputPort())
        smoother.SetNumberOfIterations(10)
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputConnection(smoother.GetOutputPort())
        normals.SetFeatureAngle(60)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(normals.GetOutputPort())
        mapper.SetScalarVisibility(False)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)
        actor.GetProperty().SetOpacity(opac)
        actor.GetProperty().SetSpecular(0.3)
        self.ren.AddActor(actor)
        edges = vtk.vtkExtractEdges()
        edges.SetInputConnection(normals.GetOutputPort())
        em = vtk.vtkPolyDataMapper()
        em.SetInputConnection(edges.GetOutputPort())
        em.SetScalarVisibility(False)
        edge_actor = vtk.vtkActor()
        edge_actor.SetMapper(em)
        edge_actor.GetProperty().SetColor(
            min(color[0]+0.2, 1), min(color[1]+0.2, 1), min(color[2]+0.2, 1))
        edge_actor.GetProperty().SetLineWidth(0.6)
        edge_actor.GetProperty().SetOpacity(opac*0.5)
        self.ren.AddActor(edge_actor)
        contour.Update()
        smoother.Update()
        normals.Update()
        edges.Update()
        box.entry = IsoEntry(idx=box.idx, color=color, actor=actor, edge_actor=edge_actor)
        vis = box.show_cb.isChecked() and self._iso_enabled
        actor.SetVisibility(vis)
        edge_actor.SetVisibility(vis)
        self._ren()
        r, g, b = box._rgb
        self._info(f"Isosurface #{box.idx} drawn!\n"
                   f"  Variable : {var_name}\n"
                   f"  Isovalue : {iso_val:.3f}\n"
                   f"  Color    : rgb({r},{g},{b})")

    def _delete_iso_box(self, box: IsoInputBox):
        if box.entry:
            self.ren.RemoveActor(box.entry.actor)
            self.ren.RemoveActor(box.entry.edge_actor)
            self._ren()
        if box in self.iso_boxes:
            self.iso_boxes.remove(box)
        box.deleteLater()
        self._info(f"Isosurface #{box.idx} deleted.")

    # ------------------------------------------------------------------
    #  VOLUME RENDERING
    # ------------------------------------------------------------------
    def _on_vol_var_changed(self, var_name):
        if var_name in self.arrays:
            arr = self.arrays[var_name]
            lo, hi = float(arr.min()), float(arr.max())
            self.tf_canvas.set_range(lo, hi)
            # Also refresh colorbar with new variable range
            cmap_name = self.vol_cmap_cb.currentText()
            self._update_cmap_visuals(cmap_name, lo, hi, var_name)

    def _on_cmap_changed(self, cmap_name):
        """Instantly update colorbar and TF gradient when colormap dropdown changes."""
        var_name = self.vol_var_cb.currentText()
        if var_name in self.arrays:
            arr = self.arrays[var_name]
            lo, hi = float(arr.min()), float(arr.max())
        else:
            lo, hi = self.tf_canvas.lo, self.tf_canvas.hi
        self._update_cmap_visuals(cmap_name, lo, hi, var_name)
        # If volume already rendered, re-apply with new colormap live
        if self.vol_actor and self._vol_enabled:
            self._apply_volume(silent=True)

    def _update_cmap_visuals(self, cmap_name, lo, hi, var_name=""):
        """Sync colorbar canvas and TF canvas gradient strip to the given colormap."""
        colors_list = self.colorbar_canvas._get_colors_list(cmap_name)
        self.colorbar_canvas.update_bar(lo, hi, cmap_name, var_name)
        self.tf_canvas.set_cmap_colors(colors_list)

    def _on_tf_changed(self, points):
        if self.vol_actor and self._vol_enabled:
            self._apply_volume(silent=True)

    def _reset_tf(self):
        self.tf_canvas.reset_default()

    def _make_color_tf(self, cmap_name, lo, hi):
        """Build CTF from standard colormap or custom file points."""
        ctf = vtk.vtkColorTransferFunction()
        # If custom RGB file is loaded, use it
        if self._custom_ctf_points:
            for (val, r, g, b) in self._custom_ctf_points:
                ctf.AddRGBPoint(val, r, g, b)
            return ctf
        mid = (lo+hi)/2.0
        q1 = lo+(hi-lo)*0.25
        q3 = lo+(hi-lo)*0.75
        if "Blue-Pink" in cmap_name:
            ctf.AddRGBPoint(lo,  0.05, 0.10, 0.70)
            ctf.AddRGBPoint(q1,  0.25, 0.50, 0.95)
            ctf.AddRGBPoint(mid, 0.70, 0.60, 0.95)
            ctf.AddRGBPoint(q3,  0.95, 0.40, 0.75)
            ctf.AddRGBPoint(hi,  0.90, 0.10, 0.50)
        elif "Rainbow" in cmap_name:
            ctf.AddRGBPoint(lo, 0.0, 0.0, 1.0)
            ctf.AddRGBPoint(q1, 0.0, 1.0, 1.0)
            ctf.AddRGBPoint(mid, 0.0, 1.0, 0.0)
            ctf.AddRGBPoint(q3, 1.0, 1.0, 0.0)
            ctf.AddRGBPoint(hi, 1.0, 0.0, 0.0)
        elif "Hot" in cmap_name:
            ctf.AddRGBPoint(lo, 0.0, 0.0, 0.0)
            ctf.AddRGBPoint(q1, 0.5, 0.0, 0.0)
            ctf.AddRGBPoint(mid, 1.0, 0.2, 0.0)
            ctf.AddRGBPoint(q3, 1.0, 0.8, 0.0)
            ctf.AddRGBPoint(hi, 1.0, 1.0, 1.0)
        elif "Cool" in cmap_name:
            ctf.AddRGBPoint(lo, 0.0, 1.0, 1.0)
            ctf.AddRGBPoint(hi, 1.0, 0.0, 1.0)
        elif "Grayscale" in cmap_name:
            ctf.AddRGBPoint(lo, 0.0, 0.0, 0.0)
            ctf.AddRGBPoint(hi, 1.0, 1.0, 1.0)
        elif "Jet" in cmap_name:
            ctf.AddRGBPoint(lo, 0.0, 0.0, 0.5)
            ctf.AddRGBPoint(q1, 0.0, 0.5, 1.0)
            ctf.AddRGBPoint(mid, 0.0, 1.0, 0.5)
            ctf.AddRGBPoint(q3, 1.0, 1.0, 0.0)
            ctf.AddRGBPoint(hi, 0.5, 0.0, 0.0)
        elif "Viridis" in cmap_name:
            ctf.AddRGBPoint(lo, 0.27, 0.00, 0.33)
            ctf.AddRGBPoint(q1, 0.13, 0.37, 0.53)
            ctf.AddRGBPoint(mid, 0.13, 0.57, 0.55)
            ctf.AddRGBPoint(q3, 0.37, 0.79, 0.38)
            ctf.AddRGBPoint(hi, 0.99, 0.91, 0.14)
        elif "Ocean" in cmap_name:
            ctf.AddRGBPoint(lo, 0.0, 0.0, 0.2)
            ctf.AddRGBPoint(q1, 0.0, 0.2, 0.5)
            ctf.AddRGBPoint(mid, 0.0, 0.5, 0.8)
            ctf.AddRGBPoint(q3, 0.2, 0.8, 1.0)
            ctf.AddRGBPoint(hi, 0.9, 1.0, 1.0)
        else:
            ctf.AddRGBPoint(lo, 0.0, 0.0, 1.0)
            ctf.AddRGBPoint(hi, 1.0, 0.0, 0.0)
        return ctf

    def _apply_volume(self, silent=False):
        if self.img is None:
            if not silent:
                self._info("Load data first!")
            return
        if not self._vol_enabled:
            if not silent:
                self._info("Enable Volume Rendering Mode first!")
            return
        var_name = self.vol_var_cb.currentText()
        cmap_name = self.vol_cmap_cb.currentText()
        if var_name not in self.arrays:
            if not silent:
                self._info(f"Variable '{var_name}' not found!")
            return
        if self.vol_actor:
            self.ren.RemoveVolume(self.vol_actor)
            self.vol_actor = None
        img_copy = vtk.vtkImageData()
        img_copy.DeepCopy(self.img)
        img_copy.GetPointData().SetActiveScalars(var_name)
        arr = self.arrays[var_name]
        lo = float(arr.min())
        hi = float(arr.max())
        # Build CTF (custom or standard)
        ctf = self._make_color_tf(cmap_name, lo, hi)
        self.tf_canvas.set_range(lo, hi)
        # Sync TF canvas background gradient to match current colormap
        colors_for_tf = self.colorbar_canvas._get_colors_list(cmap_name)
        self.tf_canvas.set_cmap_colors(colors_for_tf)
        otf = self.tf_canvas.get_vtk_otf()
        vp = vtk.vtkVolumeProperty()
        vp.SetColor(ctf)
        vp.SetScalarOpacity(otf)
        vp.SetInterpolationTypeToLinear()
        # ── Shade ON / OFF from checkbox ──
        if self.shade_on_cb.isChecked():
            vp.ShadeOn()
            vp.SetAmbient(0.4)
            vp.SetDiffuse(0.7)
            vp.SetSpecular(0.2)
        else:
            vp.ShadeOff()
            vp.SetAmbient(1.0)
            vp.SetDiffuse(0.0)
            vp.SetSpecular(0.0)
        mapper = vtk.vtkSmartVolumeMapper()
        mapper.SetInputData(img_copy)
        mapper.SetBlendModeToComposite()
        self.vol_actor = vtk.vtkVolume()
        self.vol_actor.SetMapper(mapper)
        self.vol_actor.SetProperty(vp)
        self.ren.AddVolume(self.vol_actor)
        # Respect visibility flag
        if self._vol_enabled:
            self.vol_actor.VisibilityOn()
        else:
            self.vol_actor.VisibilityOff()
        self.vol_remove_btn.setEnabled(True)
        # Determine display cmap name
        if self._custom_ctf_points:
            cmap_disp = f"Custom RGB ({len(self._custom_ctf_points)} pts)"
        else:
            cmap_disp = cmap_name.split('(')[0].strip()
        self.vol_status_lbl.setText(
            f"Variable : {var_name}\n"
            f"Colormap : {cmap_disp}\n"
            f"Range    : [{lo:.3g}, {hi:.3g}]")
        # ── Update colorbar ──
        self.colorbar_canvas.update_bar(lo, hi,
                                         cmap_name if not self._custom_ctf_points else "Custom",
                                         var_name)
        self._ren()
        if not silent:
            self._info(f"Volume Rendering applied!\n"
                       f"  Variable : {var_name}\n"
                       f"  Colormap : {cmap_disp}\n"
                       f"  Range    : [{lo:.3g}, {hi:.3g}]\n\n"
                       f"  Isosurface still active if checked ✓\n"
                       f"  Drag TF points → live update!")

    def _remove_volume(self):
        if self.vol_actor:
            self.ren.RemoveVolume(self.vol_actor)
            self.vol_actor = None
            self.vol_remove_btn.setEnabled(False)
            self.vol_status_lbl.setText("Volume: not applied")
            self._ren()
            self._info("Volume removed.")

    # ------------------------------------------------------------------
    #  SPHERE SELECTION
    # ------------------------------------------------------------------
    def _make_red_actor(self):
        pts = vtk.vtkPoints()
        poly = vtk.vtkPolyData()
        poly.SetPoints(pts)
        verts = vtk.vtkCellArray()
        poly.SetVerts(verts)
        mp = vtk.vtkPolyDataMapper()
        mp.SetInputData(poly)
        ac = vtk.vtkActor()
        ac.SetMapper(mp)
        ac.GetProperty().SetColor(1.0, 0.0, 0.0)
        ac.GetProperty().SetPointSize(7)
        ac.GetProperty().SetRenderPointsAsSpheres(True)
        ac.VisibilityOff()
        self.ren.AddActor(ac)
        return ac, pts, poly, verts

    def _add_sphere(self):
        n = len(self.spheres)+1
        nm = f"Sphere {n}"
        rep = vtk.vtkSphereRepresentation()
        rep.SetCenter(*self.center)
        rep.SetRadius(self.rad_sl.value())
        rep.GetSphereProperty().SetColor(1.0, 0.15, 0.15)
        rep.GetSphereProperty().SetOpacity(0.22)
        rep.HandleVisibilityOff()
        w = vtk.vtkSphereWidget2()
        w.SetInteractor(self.iren)
        w.SetRepresentation(rep)
        w.On()
        ac, pts, poly, verts = self._make_red_actor()
        entry = SphereEntry(w, ac, pts, poly, verts, nm)
        self.spheres.append(entry)
        self._upd_sph_list()
        self.active_lbl.setText(f"Active: {nm}  (total {n})")
        self._ren()
        self._info(f"{nm} added\nLEFT DRAG=move  RIGHT DRAG=resize")

    def _on_radius(self, val):
        self.rad_lbl.setText(str(val))
        if self.spheres:
            self.spheres[-1].widget.GetRepresentation().SetRadius(val)
            self._ren()

    def _remove_last(self):
        if not self.spheres:
            return
        e = self.spheres.pop()
        e.widget.Off()
        self.ren.RemoveActor(e.actor)
        self._upd_sph_list()
        nm = self.spheres[-1].name if self.spheres else "-"
        self.active_lbl.setText(f"Active: {nm}")
        self._ren()

    def _upd_sph_list(self):
        if not self.spheres:
            self.sph_list_lbl.setText("Spheres: none")
            return
        lines = []
        for e in self.spheres:
            r = e.widget.GetRepresentation()
            cx, cy, cz = r.GetCenter()
            rad = r.GetRadius()
            lines.append(f"  {e.name}  c=({cx:.1f},{cy:.1f},{cz:.1f})  r={rad:.1f}  n={len(e.ids)}")
        self.sph_list_lbl.setText("Spheres:\n"+"\n".join(lines))

    def _clear_brushes(self):
        self.pcp.brushes = {}
        if self.pcp._ordered:
            self.pcp._redraw()
        self._info("All brushes cleared.")

    def _show_selection(self):
        if not self._iso_enabled:
            self._info("Enable Isosurface Mode to use PCP selection!")
            return
        if not self.spheres:
            self._info("Add Sphere first!")
            return
        pcp_vars = self._get_pcp_vars()
        if not pcp_vars:
            self._info("No variable checked in right panel!")
            return
        collected = {v: [] for v in pcp_vars}
        total = 0
        for entry in self.spheres:
            rep = entry.widget.GetRepresentation()
            cx, cy, cz = rep.GetCenter()
            r2 = rep.GetRadius()**2
            ids, coords = [], []
            for i in range(self.img.GetNumberOfPoints()):
                px, py, pz = self.img.GetPoint(i)
                if (px-cx)**2+(py-cy)**2+(pz-cz)**2 <= r2:
                    ids.append(i)
                    coords.append((px, py, pz))
            entry.ids = ids
            entry.coords = coords
            total += len(ids)
            entry.pts.Reset()
            entry.verts.Reset()
            for k, (px, py, pz) in enumerate(coords):
                entry.pts.InsertNextPoint(px, py, pz)
                entry.verts.InsertNextCell(1)
                entry.verts.InsertCellPoint(k)
            entry.poly.Modified()
            entry.actor.VisibilityOn()
            for v in pcp_vars:
                if v in self.arrays:
                    collected[v].extend(self.arrays[v][ids].tolist())
        self._ren()
        self._upd_sph_list()
        lv = self.lbl_sl.value()/100.0
        arr_dict = {v: np.array(collected[v]) for v in pcp_vars if len(collected[v]) > 0}
        self.pcp.show_pcp(arr_dict, label_val=lv,
                          title=f"{len(self.spheres)} sphere(s)  n={total}  label={lv:.2f}")
        self.tabs.setCurrentIndex(0)
        self._info(f"Selection done!\n   Points: {total}\n"
                   f"   PCP vars: {pcp_vars}\n   Label: {lv:.2f}")

    def _clear_all(self):
        for e in self.spheres:
            e.actor.VisibilityOff()
            e.ids = []
            e.coords = []
        self._ren()
        self.pcp.show_empty()
        self._info("Cleared.")

    def _add_to_list(self):
        lv = self.lbl_sl.value() / 100.0
        pcp_vars = self._get_pcp_vars()
        all_coords = []
        all_ids = []
        for entry in self.spheres:
            for coord, pid in zip(entry.coords, entry.ids):
                all_coords.append(coord)
                all_ids.append(pid)
        if not all_coords:
            self._info("Run Show Selection first!")
            return
        brushes = self.pcp.brushes
        if brushes and pcp_vars:
            norm_vals = {}
            for v in pcp_vars:
                if v in self.arrays and v in (self.pcp._lo or {}):
                    lo = self.pcp._lo[v]
                    hi = self.pcp._hi[v]
                    norm_vals[v] = (self.arrays[v][all_ids]-lo)/(hi-lo+1e-12)
            ordered = self.pcp._ordered
            keep = np.ones(len(all_coords), dtype=bool)
            for j, (blo, bhi) in brushes.items():
                if j < len(ordered):
                    v = ordered[j]
                    if v in norm_vals:
                        keep &= (norm_vals[v] >= blo) & (norm_vals[v] <= bhi)
            filtered = [all_coords[i] for i in range(len(all_coords)) if keep[i]]
            brush_info = f"Brush: {len(filtered)}/{len(all_coords)} pts\n  "
        else:
            filtered = all_coords
            brush_info = "All sphere points\n  "
        if not filtered:
            self._info("No points in brush range!\nExpand or clear brush.")
            return
        rows = [(c[0], c[1], c[2], lv) for c in filtered]
        if self.save_path is None:
            path, _ = QFileDialog.getSaveFileName(
                self, "Output file", "selected_points.txt",
                "Text Files (*.txt);;All Files (*)")
            if not path:
                self._info("No file chosen.")
                return
            self.save_path = path
            header = ("# Interactive Data Selection Output\n"
                      "# Format: X  Y  Z  Label\n#\n"
                      f"{'X':>14}  {'Y':>14}  {'Z':>14}  {'Label':>10}\n"+"-"*60+"\n")
            data_lines = "\n".join(
                f"{x:>14.6f}  {y:>14.6f}  {z:>14.6f}  {lv2:>10.4f}"
                for x, y, z, lv2 in rows)
            with open(self.save_path, "w") as f:
                f.write(header+data_lines+"\n")
            self.samples.extend(rows)
            self.sample_count.setText(f"Total saved: {len(self.samples)} rows")
            self.path_lbl.setText(f"File: {os.path.basename(self.save_path)}")
            self._info(f"File created!\n  {os.path.basename(self.save_path)}\n"
                       f"  {brush_info}Rows: {len(rows)}  Label: {lv:.2f}")
        else:
            data_lines = "\n".join(
                f"{x:>14.6f}  {y:>14.6f}  {z:>14.6f}  {lv2:>10.4f}"
                for x, y, z, lv2 in rows)
            with open(self.save_path, "a") as f:
                f.write(data_lines+"\n")
            self.samples.extend(rows)
            self.sample_count.setText(f"Total saved: {len(self.samples)} rows")
            self._info(f"APPENDED!\n  {brush_info}Rows: {len(rows)}\n"
                       f"  Total: {len(self.samples)}")
        try:
            with open(self.save_path, "r") as f:
                all_lines = f.readlines()
            preview = "".join(all_lines[:40])
            if len(all_lines) > 40:
                preview += f"\n...({len(self.samples)} total rows)"
            self.out_text.setPlainText(preview)
            self.tabs.setCurrentIndex(1)
        except:
            pass

    def closeEvent(self, event):
        self.vtk_widget.GetRenderWindow().Finalize()
        self.iren.TerminateApp()
        super().closeEvent(event)


# ================================================================
#  LAUNCH
# ================================================================
def launch():
    app = QApplication.instance()
    created_app = app is None
    if created_app:
        app = QApplication(sys.argv)

    win = MainWindow()
    win.show()

    is_ipython = False
    try:
        from IPython import get_ipython
        ip = get_ipython()
        if ip is not None:
            ip.run_line_magic("gui", "qt5")
            is_ipython = True
    except Exception:
        pass

    print("Window opened!")
    print("WORKFLOW:")
    print("  1. Load Data -> .vti file")
    print("  2. Check Isosurface Mode -> Add isosurfaces (checkbox)")
    print("  3. Check Volume Mode -> choose Variable + Colormap -> Apply")
    print("     Both modes can be active simultaneously!")
    print("  4. Uncheck Isosurface -> PCP plot clears automatically")
    print("  5. Custom RGB File -> load your value/R/G/B file -> Apply Volume")
    print("  6. Sphere -> Show Selection -> PCP brushing -> Add to List")

    if created_app and not is_ipython:
        return app.exec_()
    return win


if __name__ == "__main__":
    sys.exit(launch() or 0)
