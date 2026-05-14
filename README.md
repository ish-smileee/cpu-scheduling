# CPU Scheduling Algorithms Simulator
 
A Windows desktop application that simulates six fundamental CPU scheduling algorithms with a graphical user interface built using Python and `tkinter`. Available as a standalone executable — no Python installation required. Developed as a case study for the Operating Systems course at Tarlac State University, College of Computer Studies.
 
---
 
## Table of Contents
 
- [Overview](#overview)
- [Features](#features)
- [Algorithms Implemented](#algorithms-implemented)
- [Requirements](#requirements)
- [How to Run](#how-to-run)
- [How to Use](#how-to-use)
- [Input Parameters](#input-parameters)
- [Output](#output)
- [Input Validation Rules](#input-validation-rules)
- [Performance Metrics](#performance-metrics)
- [Author](#author)
---
 
## Overview
 
This simulator provides a hands-on environment for experimenting with CPU scheduling algorithms. Users can define their own process parameters, run a simulation, and immediately observe the execution timeline through a color-coded Gantt chart alongside a detailed results table showing per-process and average performance metrics.
 
The goal is to bridge the gap between theoretical scheduling concepts and observable, measurable outcomes.
 
---
 
## Features
 
- Six CPU scheduling algorithms in one application
- Color-coded, interactive Gantt chart visualization
- Per-process and average Waiting Time and Turnaround Time computation
- Real-time input validation — blocks non-numeric characters at the keystroke level
- State persistence when switching between algorithms (values are not reset unless explicitly refreshed)
- Time Quantum field automatically enabled/disabled based on the selected algorithm
- Minimum process count enforcement (at least 3 processes required)
- Dedicated error dialog for runtime logical inconsistencies
---
 
## Algorithms Implemented
 
| Algorithm | Type | Time Quantum Required |
|---|---|---|
| First-Come, First-Served (FCFS) | Non-Preemptive | No |
| Shortest Job First (SJF) | Non-Preemptive | No |
| Shortest Remaining Time (SRT) | Preemptive | No |
| Round Robin (RR) | Preemptive | Yes |
| Priority Scheduling | Non-Preemptive | No |
| Priority Scheduling with Round Robin | Preemptive | Yes |
 
---
 
## Requirements
 
- **Windows 10 or later** (64-bit recommended)
- No Python installation required
- No additional libraries or dependencies needed
The executable is fully self-contained.
 
---
 
## How to Run
 
1. Download or clone this repository.
2. Locate `cpu_scheduler.exe` in the repository root.
3. Double-click `cpu_scheduler.exe` to launch the application.
The GUI window will open immediately — no installation or setup required.
 
> **Note:** Windows may display a SmartScreen warning the first time you run the executable since it is unsigned. Click **More info → Run anyway** to proceed.
 
---
 
## How to Use
 
1. **Select an Algorithm** from the list on the left panel.
2. **Set the Process Count** using the spinner control (minimum of 3).
3. **Enter Process Parameters** in the input table (Arrival Time, Burst Time, and Priority if applicable).
4. **Set the Time Quantum** if the selected algorithm requires it (Round Robin or Priority+RR).
5. Click **Run Simulation** to execute and view results.
6. Toggle between the **Gantt Chart** and **Results Table** tabs to explore the output.
7. Click **Refresh Table** to reset all input values back to default presets.
---
 
## Input Parameters
 
| Field | Description | Constraints |
|---|---|---|
| Arrival Time | The time at which the process enters the ready queue | Non-negative integer (≥ 0) |
| Burst Time | The total CPU time the process requires | Positive integer (> 0) |
| Priority | Importance level of the process (lower value = higher priority) | Positive integer; only available for Priority-based algorithms |
| Time Quantum | The fixed time slice for Round Robin-based algorithms | Positive integer; only applicable to RR and Priority+RR |
 
---
 
## Output
 
After running a simulation, the application displays:
 
**Gantt Chart tab**
- A color-coded horizontal bar chart representing the CPU execution timeline
- Each process is assigned a distinct color
- Idle CPU periods are shown where applicable

**Results Table tab**
- A table with the following columns for each process:
  - PID
  - Arrival Time
  - Burst Time
  - Priority (if applicable)
  - Completion Time
  - Turnaround Time
  - Waiting Time
- Average Waiting Time and Average Turnaround Time displayed at the bottom
---
 
## Input Validation Rules
 
- Only numeric characters are accepted in input fields; non-numeric keystrokes are blocked in real time
- Arrival Time must be a non-negative integer (0 or greater)
- Burst Time must be a positive integer (greater than 0)
- A minimum of 3 processes must be defined before running a simulation
- Any remaining logical inconsistencies detected at runtime are reported via a dedicated error dialog
---
 
## Performance Metrics
 
| Metric | Formula |
|---|---|
| Turnaround Time (TAT) | Completion Time − Arrival Time |
| Waiting Time (WT) | Turnaround Time − Burst Time |
| Average Waiting Time | Sum of all Waiting Times ÷ Number of Processes |
| Average Turnaround Time | Sum of all Turnaround Times ÷ Number of Processes |
 
---
 
## Author
 
**Lapus, Jose Ishmael R.**
Bachelor of Science in Computer Science — 3B
College of Computer Studies, Tarlac State University
 
Submitted to: **Jo Anne G. Cura**
Course: Operating Systems
Date: May 7, 2026
