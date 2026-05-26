# Interactive Selection of Training Data for 3D Volumetric Datasets

<p align="center">
  An interactive desktop tool for loading volumetric `.vti` data, exploring it in 3D, selecting labeled regions of interest, and exporting training data for machine learning workflows.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/VTK-3D%20Visualization-0F766E?style=for-the-badge" alt="VTK">
  <img src="https://img.shields.io/badge/PyQt5-Desktop%20UI-2563EB?style=for-the-badge" alt="PyQt5">
  <img src="https://img.shields.io/badge/Matplotlib-PCP%20Analytics-F97316?style=for-the-badge" alt="Matplotlib">
</p>

<p align="center">
  <img src="assets/screenshots/01-home.png" alt="Full application interface" width="900">
</p>

## Project Overview

Researchers often spend a large amount of time manually sifting through 3D volumetric datasets to identify meaningful regions for analysis and model training. This project was designed to reduce that effort through an interactive training data selection tool that supports end-to-end exploration, filtering, selection, and export of labeled data.

The system was developed collaboratively by understanding research needs, iterating on the interface based on feedback, and delivering a working prototype that significantly reduces manual data selection effort.

Built using **Python, VTK, PyQt5, Matplotlib, and NumPy**, the tool combines:

- interactive **isosurface rendering**
- real-time **volume rendering**
- **sphere widget**-based region selection
- **parallel coordinates plots (PCP)** for multivariate inspection
- **brushing and filtering** for fine-grained sample refinement
- labeled output generation for downstream **machine learning training**

## Key Highlights

- Identified a core user pain point: manual filtering of large 3D volumetric datasets for training data creation.
- Designed and developed an interactive labeled data selection workflow to solve the problem end-to-end.
- Collaborated on requirements, refined the interface through feedback, and delivered a usable research prototype.
- Enabled intuitive 3D filtering with sphere widgets, isosurface rendering, and volume rendering in one interface.
- Supported real-time visual exploration and export of labeled samples for ML model training.

## Features

| Feature | Description |
| --- | --- |
| **Load volumetric datasets** | Open `.vti` files and inspect available scalar variables dynamically |
| **Isosurface mode** | Generate and manage one or more isosurfaces with variable and opacity controls |
| **Volume rendering mode** | Visualize internal structures using transfer functions and colormap controls |
| **Combined rendering** | Run isosurface mode, volume mode, or both together in the same session |
| **Sphere widget selection** | Select spatial regions of interest directly inside the 3D view |
| **PCP visualization** | Inspect selected points across multiple variables using a parallel coordinates plot |
| **Brushing support** | Refine the selected subset interactively before export |
| **Labeled export** | Save selected samples in `X Y Z Label` format for ML pipelines |

## Workflow

This tool supports a simple research workflow:

```text
Load any .vti dataset
      ->
Enable Isosurface Mode, Volume Rendering Mode, or both
      ->
Explore the 3D data in real time
      ->
Add sphere widgets to select regions of interest
      ->
Show selected points in the PCP panel
      ->
Brush/filter the PCP to refine the subset
      ->
Assign a label value
      ->
Save the selected data for model training
```

## Demo Preview

### 1. Full Interface

Main workspace showing the 3D viewport, rendering controls, PCP variable panel, sphere selection tools, and output area.

<p align="center">
  <img src="assets/screenshots/01-home.png" alt="Full interface" width="900">
</p>

### 2. Isosurface Rendering

Interactive isosurface rendering for extracting structural regions from volumetric data.

<p align="center">
  <img src="assets/screenshots/02-isosurface-and-volume-controls.png" alt="Isosurface rendering" width="900">
</p>

### 3. Volume Rendering

Real-time volume rendering with colormap and opacity transfer function controls for internal feature visualization.

<p align="center">
  <img src="assets/screenshots/03-volume-rendering.png" alt="Volume rendering" width="900">
</p>

### 4. Sphere Widget Selection + PCP + Brushing

Selected 3D regions are pushed into the PCP view, where brushing can be used to refine the final labeled training subset.

<p align="center">
  <img src="assets/screenshots/04-sphere-selection-pcp.png" alt="Sphere widget data selection with PCP" width="900">
</p>

<p align="center">
  <img src="assets/screenshots/05-pcp-brushing.png" alt="PCP brushing feature" width="900">
</p>

## Technologies Used

- Python
- VTK
- PyQt5
- Matplotlib
- NumPy

No separate JavaScript or HTML/CSS runtime is required for this desktop application.

## Requirements

### Software Requirements

- Python 3.8 or above
- Python 3.10 recommended
- VTK 9.x
- PyQt5 5.15+
- NumPy 1.21+
- Matplotlib 3.5+

### System Configuration

- Operating System: Windows 10/11
- RAM: Minimum 4 GB
- Processor: Intel i3 or above
- Disk Space: 500 MB free space

### Python Libraries Installation

```bash
pip install vtk pyqt5 numpy matplotlib
```

Or install directly from the project requirements file:

```bash
pip install -r requirements.txt
```

## Running the Project

### Standard Run

```bash
python vtk_final.py
```

### Jupyter Notebook Run

```python
%gui qt5
%run vtk_final.py
```

## Output Format

The selected and labeled output is stored in the following format:

```text
X  Y  Z  Label
```

This makes the exported data suitable for:

- supervised learning pipelines
- scientific classification workflows
- curated training data generation
- feature-driven model experimentation

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

## Academic Context

This project was developed as an interactive research-oriented prototype for efficient selection of labeled training data from volumetric scientific datasets.

## Author

**Kritika Gupta**  
B.Tech CSE (Data Science)

## License

This project is licensed under the **MIT License**.
