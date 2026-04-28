# Interactive 3D Scientific Data Visualization and ML Annotation Tool

An interactive desktop application for exploring the Isabel hurricane dataset in 3D, selecting regions of interest with sphere widgets, analyzing high-dimensional variables through parallel coordinates, and exporting labeled samples for machine learning workflows.

## Features

- Load `.vti` scientific datasets with multiple scalar variables
- Render interactive isosurfaces with per-surface controls
- Perform GPU-based volume rendering with custom transfer functions
- Select 3D regions using one or more sphere widgets
- Visualize selected samples in a parallel coordinates plot
- Brush PCP axes to refine selection before export
- Export labeled output in `X Y Z Label` format

## Tech Stack

- Python
- VTK
- PyQt5
- Matplotlib
- NumPy
- SciPy

## Repository Contents

- `vtk_final.py`: runnable desktop application
- `interface for interactive data selection.ipynb`: original notebook version
- `requirements.txt`: Python dependencies
- `assets/screenshots/`: UI screenshots

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
python vtk_final.py
```

If you want to launch it from Jupyter as well:

```python
%gui qt5
%run vtk_final.py
```

## Workflow

1. Load a `.vti` dataset.
2. Enable isosurface mode and/or volume rendering mode.
3. Tune variables, opacity, colormap, and transfer function.
4. Add one or more sphere widgets to select regions of interest.
5. Click `Show Selection` to inspect selected points in the PCP view.
6. Brush PCP axes to narrow the subset if needed.
7. Set the label value and save the selected rows.

## Dataset

This project is designed around the Isabel hurricane dataset and supports variables such as:

`P`, `TC`, `CLOUD`, `PRECIP`, `QCLOUD`, `QGRAUP`, `QICE`, `QRAIN`, `QSNOW`, `QVAPOR`, `U`, `V`, `W`, `Velocity`

## Screenshots

### Home Screen

![Home screen](assets/screenshots/01-home.png)

### Isosurface and Volume Controls

![Isosurface and volume controls](assets/screenshots/02-isosurface-and-volume-controls.png)

### Volume Rendering

![Volume rendering](assets/screenshots/03-volume-rendering.png)

### Sphere Selection with PCP Output

![Sphere selection with PCP output](assets/screenshots/04-sphere-selection-pcp.png)

### PCP Brushing

![PCP brushing](assets/screenshots/05-pcp-brushing.png)

## Author

Kritika Gupta
