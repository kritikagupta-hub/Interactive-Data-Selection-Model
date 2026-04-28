# Interactive 3D Scientific Data Visualization and ML Annotation Tool

<p align="center">
  Explore volumetric scientific data, isolate 3D regions of interest, analyze 14 variables together, and export labeled samples for ML workflows.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/VTK-3D%20Visualization-0F766E?style=for-the-badge" alt="VTK">
  <img src="https://img.shields.io/badge/PyQt5-Desktop%20UI-2563EB?style=for-the-badge" alt="PyQt5">
  <img src="https://img.shields.io/badge/Matplotlib-PCP%20Analytics-F97316?style=for-the-badge" alt="Matplotlib">
</p>

<p align="center">
  <img src="assets/screenshots/01-home.png" alt="Application home screen" width="900">
</p>

## Overview

This project is an interactive desktop application built for **scientific data exploration, visual analytics, and machine learning data annotation**. It is designed around the **Isabel hurricane dataset** and combines 3D rendering with parallel-coordinates-based analysis in one workflow.

Instead of only visualizing a dataset, the tool helps you:

- inspect scalar fields in 3D
- isolate regions of interest using sphere widgets
- compare multiple variables simultaneously
- interactively brush high-dimensional patterns
- export labeled samples for downstream ML training

## Why This Project Stands Out

- **3D + ML workflow in one interface**: visualization, selection, filtering, and labeling happen in the same app
- **Dual rendering modes**: use isosurface rendering and volume rendering independently or together
- **High-dimensional analytics**: selected points are projected into a parallel coordinates plot across 14 variables
- **Interactive annotation**: assign labels on a `0.0 -> 1.0` scale for curated ML-ready outputs
- **Research-friendly export**: save selected coordinates directly in `X Y Z Label` format

## Core Features

| Feature | What it does |
| --- | --- |
| **Load `.vti` data** | Opens volumetric VTK image datasets with multiple scalar variables |
| **Isosurface rendering** | Generates multiple isosurfaces with per-surface variable, opacity, and visibility controls |
| **Volume rendering** | Applies GPU-based volume rendering with colormap and opacity transfer function editing |
| **Sphere selection** | Lets you place one or more 3D sphere widgets to isolate local regions |
| **Parallel Coordinates Plot** | Displays selected samples across multiple variables for high-dimensional inspection |
| **Brushing** | Filters selected samples directly inside the PCP before export |
| **Labeled export** | Saves curated points as training-ready output with user-defined labels |

## Dataset Context

This tool is designed for the **Isabel hurricane dataset**, a well-known scientific visualization dataset.

**Supported variables**

`P`, `TC`, `CLOUD`, `PRECIP`, `QCLOUD`, `QGRAUP`, `QICE`, `QRAIN`, `QSNOW`, `QVAPOR`, `U`, `V`, `W`, `Velocity`

## Visual Workflow

```text
Load .vti dataset
      ->
Choose Isosurface and/or Volume Rendering
      ->
Adjust opacity, visibility, colormap, and transfer function
      ->
Add sphere widgets to mark regions of interest
      ->
Show selection in PCP
      ->
Brush axes to refine the subset
      ->
Assign label
      ->
Export ML-ready points
```

## Interface Highlights

### 1. Main Workspace

Clean layout with 3D viewport, rendering controls, PCP variable toggles, and output panel.

<p align="center">
  <img src="assets/screenshots/01-home.png" alt="Main workspace" width="900">
</p>

### 2. Isosurface and Volume Controls

The right panel supports both rendering pipelines independently, making it easy to compare extracted structures with full volumetric context.

<p align="center">
  <img src="assets/screenshots/02-isosurface-and-volume-controls.png" alt="Isosurface and volume controls" width="900">
</p>

### 3. Volume Rendering with Transfer Function

Adjust colormaps and opacity mapping to reveal internal volumetric structures more clearly.

<p align="center">
  <img src="assets/screenshots/03-volume-rendering.png" alt="Volume rendering view" width="900">
</p>

### 4. Sphere-Based Selection + PCP

Selected regions are sent directly into a parallel coordinates plot for multivariate inspection.

<p align="center">
  <img src="assets/screenshots/04-sphere-selection-pcp.png" alt="Sphere selection and PCP output" width="900">
</p>

### 5. PCP Brushing for Fine Filtering

Interactive brushing helps narrow the subset before saving labeled output.

<p align="center">
  <img src="assets/screenshots/05-pcp-brushing.png" alt="PCP brushing" width="900">
</p>

## Tech Stack

- **Python**
- **VTK** for 3D visualization and interaction
- **PyQt5** for the desktop interface
- **Matplotlib** for the PCP and transfer function views
- **NumPy** for data operations
- **SciPy** for scientific utilities

## Project Structure

```text
.
|-- vtk_final.py
|-- interface for interactive data selection.ipynb
|-- requirements.txt
|-- assets/
|   `-- screenshots/
|-- LICENSE
`-- README.md
```

## Installation

```bash
pip install -r requirements.txt
```

## Run the Application

### Standard Python Run

```bash
python vtk_final.py
```

### Jupyter Notebook Run

```python
%gui qt5
%run vtk_final.py
```

## Export Format

Saved output follows this structure:

```text
X  Y  Z  Label
```

This makes it convenient to build datasets for:

- supervised learning
- anomaly/stall detection experiments
- scientific classification workflows
- feature engineering pipelines

## Requirements

```text
vtk>=9.0.0
PyQt5>=5.15.0
matplotlib>=3.5.0
numpy>=1.21.0
scipy>=1.7.0
```

## Potential Use Cases

- **Scientific visualization** for climate and simulation data
- **Interactive ML annotation** for training data creation
- **Pattern discovery** in high-dimensional volumetric datasets
- **Research demos** and academic project presentations

## Author

**Kritika Gupta**  
B.Tech CSE (Data Science)

## License

This project is licensed under the **MIT License**.
