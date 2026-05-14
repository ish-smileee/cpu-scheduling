"""
CPU Scheduling Algorithms Simulator
====================================
A GUI application simulating 6 CPU scheduling algorithms with
Gantt chart visualization and performance metrics.

Algorithms:
  1. FCFS  - First-Come, First-Served
  2. SJF   - Shortest Job First (Non-preemptive)
  3. SRT   - Shortest Remaining Time (Preemptive)
  4. RR    - Round Robin
  5. Priority - Non-preemptive (lower value = higher priority)
  6. Priority + Round Robin

Author: LAPUS, Jose Ishmael R.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import math
import colorsys

# ─────────────────────────────────────────────
#  COLOR PALETTE
# ─────────────────────────────────────────────
BG_MAIN    = "#FAF0F5"   # very light blush
BG_PANEL   = "#FFFFFF"   # white panels
BG_SIDEBAR = "#FFF0F7"   # soft pink sidebar
ACCENT1    = "#E91E8C"   # hot pink
ACCENT2    = "#FF6BB5"   # medium pink
ACCENT3    = "#C2185B"   # deep rose
TEXT_DARK  = "#1A0A12"   # near-black
TEXT_MID   = "#6B3A54"   # muted rose-gray
TEXT_LIGHT = "#B07090"   # light muted
BORDER     = "#F0C0D8"   # soft pink border
BTN_FG     = "#FFFFFF"
SUCCESS    = "#E91E8C"
WARN       = "#FF6BB5"

# Gantt palette
GANTT_COLORS = [
    "#E91E8C","#FF6BB5","#C2185B","#FF4081",
    "#AD1457","#F06292","#880E4F","#FF80AB",
    "#E040FB","#CE93D8","#7B1FA2","#BA68C8",
]

FONT_TITLE  = ("Helvetica Neue", 22, "bold")
FONT_HEAD   = ("Helvetica Neue", 13, "bold")
FONT_LABEL  = ("Helvetica Neue", 11)
FONT_SMALL  = ("Helvetica Neue", 9)
FONT_MONO   = ("Courier New", 10)
FONT_BTN    = ("Helvetica Neue", 11, "bold")


# ═══════════════════════════════════════════════
#   SCHEDULING ALGORITHMS
# ═══════════════════════════════════════════════

def run_fcfs(processes):
    """
    First-Come, First-Served (Non-preemptive)
    Processes execute in order of arrival time.
    """
    procs = sorted(processes, key=lambda p: (p["arrival"], p["pid"]))
    timeline = []
    clock = 0
    for p in procs:
        start = max(clock, p["arrival"])
        end   = start + p["burst"]
        timeline.append({"pid": p["pid"], "start": start, "end": end})
        clock = end
    return _compute_metrics(processes, timeline)


def run_sjf(processes):
    """
    Shortest Job First – Non-preemptive
    At each decision point, pick the ready process with smallest burst.
    """
    procs    = [dict(p) for p in processes]
    timeline = []
    clock    = 0
    done     = set()

    while len(done) < len(procs):
        ready = [p for p in procs if p["arrival"] <= clock and p["pid"] not in done]
        if not ready:
            # CPU idle – jump to next arrival
            clock = min(p["arrival"] for p in procs if p["pid"] not in done)
            continue
        chosen = min(ready, key=lambda p: (p["burst"], p["arrival"], p["pid"]))
        start  = clock
        end    = clock + chosen["burst"]
        timeline.append({"pid": chosen["pid"], "start": start, "end": end})
        clock  = end
        done.add(chosen["pid"])

    return _compute_metrics(processes, timeline)


def run_srt(processes):
    """
    Shortest Remaining Time – Preemptive SJF
    At every time unit, the process with the least remaining burst runs.
    """
    procs    = [dict(p) for p in processes]
    for p in procs:
        p["remaining"] = p["burst"]

    timeline = []
    clock    = 0
    last_pid = None
    done     = set()
    max_time = sum(p["burst"] for p in procs) + max(p["arrival"] for p in procs) + 1

    while len(done) < len(procs) and clock < max_time:
        ready = [p for p in procs if p["arrival"] <= clock and p["pid"] not in done]
        if not ready:
            clock += 1
            continue
        chosen = min(ready, key=lambda p: (p["remaining"], p["arrival"], p["pid"]))

        # Merge consecutive slices for the same process in Gantt
        if timeline and timeline[-1]["pid"] == chosen["pid"]:
            timeline[-1]["end"] = clock + 1
        else:
            timeline.append({"pid": chosen["pid"], "start": clock, "end": clock + 1})

        chosen["remaining"] -= 1
        clock += 1

        if chosen["remaining"] == 0:
            done.add(chosen["pid"])

    return _compute_metrics(processes, timeline)


def run_rr(processes, quantum):
    """
    Round Robin – time-sliced preemption by quantum.
    Uses a ready queue; processes re-enter when new arrivals appear.
    """
    procs = [dict(p) for p in processes]
    for p in procs:
        p["remaining"] = p["burst"]

    clock    = 0
    done     = set()
    timeline = []
    queue    = []
    arrived  = set()
    all_procs = sorted(procs, key=lambda p: p["arrival"])

    def enqueue_new(t):
        for p in all_procs:
            if p["arrival"] <= t and p["pid"] not in done and p["pid"] not in arrived:
                queue.append(p)
                arrived.add(p["pid"])

    enqueue_new(clock)

    while len(done) < len(procs):
        if not queue:
            # Idle – advance to next arrival
            future = [p for p in all_procs if p["pid"] not in done and p["pid"] not in arrived]
            if not future:
                break
            clock = future[0]["arrival"]
            enqueue_new(clock)
            continue

        p     = queue.pop(0)
        slice_  = min(quantum, p["remaining"])
        start   = clock
        end     = clock + slice_
        timeline.append({"pid": p["pid"], "start": start, "end": end})
        p["remaining"] -= slice_
        clock = end
        enqueue_new(clock)

        if p["remaining"] == 0:
            done.add(p["pid"])
        else:
            queue.append(p)

    return _compute_metrics(processes, timeline)


def run_priority(processes):
    """
    Priority Scheduling – Non-preemptive
    Lower priority number = higher priority.
    Ties broken by arrival time, then PID.
    """
    procs    = [dict(p) for p in processes]
    timeline = []
    clock    = 0
    done     = set()

    while len(done) < len(procs):
        ready = [p for p in procs if p["arrival"] <= clock and p["pid"] not in done]
        if not ready:
            clock = min(p["arrival"] for p in procs if p["pid"] not in done)
            continue
        chosen = min(ready, key=lambda p: (p["priority"], p["arrival"], p["pid"]))
        start  = clock
        end    = clock + chosen["burst"]
        timeline.append({"pid": chosen["pid"], "start": start, "end": end})
        clock  = end
        done.add(chosen["pid"])

    return _compute_metrics(processes, timeline)


def run_priority_rr(processes, quantum):
    """
    Priority Scheduling with Round Robin.
    Processes grouped by priority; within each priority group, RR is applied.
    Lower priority number = higher priority.
    """
    procs = [dict(p) for p in processes]
    for p in procs:
        p["remaining"] = p["burst"]

    clock    = 0
    done     = set()
    timeline = []
    all_procs = sorted(procs, key=lambda p: (p["arrival"], p["priority"], p["pid"]))
    queued   = set()

    def get_queue(t):
        """Build current ready queue ordered by priority then FIFO."""
        ready = [p for p in all_procs
                 if p["arrival"] <= t and p["pid"] not in done]
        return sorted(ready, key=lambda p: (p["priority"], p["pid"]))

    max_time = sum(p["burst"] for p in procs) + max(p["arrival"] for p in procs) + 5

    while len(done) < len(procs) and clock < max_time:
        queue = get_queue(clock)
        if not queue:
            future = [p for p in all_procs if p["pid"] not in done]
            if not future:
                break
            clock = min(p["arrival"] for p in future)
            continue

        # Run all processes of the highest priority in RR
        top_priority = queue[0]["priority"]
        prio_group   = [p for p in queue if p["priority"] == top_priority]

        made_progress = False
        for p in prio_group:
            if p["pid"] in done:
                continue
            # Check if a higher-priority process arrived since we started this group
            current_queue = get_queue(clock)
            if current_queue and current_queue[0]["priority"] < top_priority:
                break  # Preempt to higher priority

            slice_  = min(quantum, p["remaining"])
            start   = clock
            end     = clock + slice_
            timeline.append({"pid": p["pid"], "start": start, "end": end})
            p["remaining"] -= slice_
            clock = end
            made_progress = True

            if p["remaining"] == 0:
                done.add(p["pid"])

        if not made_progress:
            clock += 1

    return _compute_metrics(processes, timeline)


def _compute_metrics(processes, timeline):
    """
    Compute per-process Waiting Time (WT) and Turnaround Time (TAT).
    TAT = Completion Time - Arrival Time
    WT  = TAT - Burst Time
    """
    # Find completion time for each process from the last Gantt slice
    completion = {}
    for slot in timeline:
        pid = slot["pid"]
        if pid not in completion or slot["end"] > completion[pid]:
            completion[pid] = slot["end"]

    results = []
    for p in processes:
        pid  = p["pid"]
        ct   = completion.get(pid, p["arrival"] + p["burst"])
        tat  = ct - p["arrival"]
        wt   = tat - p["burst"]
        results.append({
            "pid":        pid,
            "arrival":    p["arrival"],
            "burst":      p["burst"],
            "priority":   p.get("priority", "-"),
            "completion": ct,
            "tat":        tat,
            "wt":         wt,
        })

    avg_wt  = sum(r["wt"]  for r in results) / len(results)
    avg_tat = sum(r["tat"] for r in results) / len(results)

    return {"timeline": timeline, "results": results,
            "avg_wt": avg_wt, "avg_tat": avg_tat}


# ═══════════════════════════════════════════════
#   GUI APPLICATION
# ═══════════════════════════════════════════════

class CPUSchedulerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CPU Scheduling Simulator")
        self.geometry("1200x820")
        self.minsize(480, 420)
        self.configure(bg=BG_MAIN)
        self.resizable(True, True)

        # ── State ──────────────────────────────
        self.num_processes   = tk.IntVar(value=4)
        self.algorithm       = tk.StringVar(value="FCFS")
        self.quantum_var     = tk.StringVar(value="2")
        self.process_entries = []   # list of dicts with tk vars
        self._saved_inputs   = {}   # persists user data across algo switches
                                    # key: pid, value: {arrival, burst, priority}
        self._sim_result     = None

        self._build_ui()

    # ────────────────────────────────────────────
    #  UI CONSTRUCTION
    # ────────────────────────────────────────────

    def _build_ui(self):
        """Construct the three-column layout: sidebar | input | output."""
        # ── Outer frame ─────────────────────────
        outer = tk.Frame(self, bg=BG_MAIN, padx=18, pady=18)
        outer.pack(fill="both", expand=True)

        # ── Title bar ───────────────────────────
        title_frame = tk.Frame(outer, bg=BG_MAIN)
        title_frame.pack(fill="x", pady=(0, 14))

        tk.Label(title_frame, text="CPU  Scheduling  Simulator",
                 font=FONT_TITLE, bg=BG_MAIN, fg=ACCENT1).pack(side="left")
        tk.Label(title_frame, text="OS Process Management",
                 font=FONT_LABEL, bg=BG_MAIN, fg=TEXT_LIGHT).pack(side="left", padx=14, pady=6)

        # ── Main content ────────────────────────
        content = tk.Frame(outer, bg=BG_MAIN)
        content.pack(fill="both", expand=True)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        # Left sidebar
        sidebar = self._make_panel(content, width=240)
        sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 14))
        self._build_sidebar(sidebar)

        # Right area: input table + output
        right = tk.Frame(content, bg=BG_MAIN)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        # Process table
        input_panel = self._make_panel(right)
        input_panel.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        self._build_input_table(input_panel)

        # Output notebook
        out_panel = self._make_panel(right)
        out_panel.grid(row=1, column=0, sticky="nsew")
        self._build_output_area(out_panel)

    def _make_panel(self, parent, **kwargs):
        """Create a white rounded-looking panel."""
        f = tk.Frame(parent, bg=BG_PANEL,
                     highlightbackground=BORDER,
                     highlightthickness=1,
                     **kwargs)
        return f

    # ── Sidebar ──────────────────────────────────

    def _build_sidebar(self, parent):
        inner = tk.Frame(parent, bg=BG_PANEL, padx=16, pady=16)
        inner.pack(fill="both", expand=True)

        self._section_label(inner, "ALGORITHM")

        algorithms = [
            ("FCFS",         "First-Come First-Served"),
            ("SJF",          "Shortest Job First"),
            ("SRT",          "Shortest Remaining Time"),
            ("RR",           "Round Robin"),
            ("Priority",     "Priority (Non-preemptive)"),
            ("Priority+RR",  "Priority + Round Robin"),
        ]

        for val, label in algorithms:
            self._algo_radio(inner, val, label)

        # Quantum setting
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", pady=12)
        self._section_label(inner, "TIME QUANTUM")

        qf = tk.Frame(inner, bg=BG_PANEL)
        qf.pack(fill="x", pady=(4, 0))
        tk.Label(qf, text="Quantum:", font=FONT_LABEL,
                 bg=BG_PANEL, fg=TEXT_MID).pack(side="left")
        self.quantum_entry = self._styled_entry(qf, self.quantum_var, width=5)
        self.quantum_entry.pack(side="left", padx=(8, 0))
        # Disabled by default — FCFS is the initial algorithm and needs no quantum
        self.quantum_entry.configure(state="disabled")
        tk.Label(qf, text="ms", font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_LIGHT).pack(side="left", padx=2)

        # Number of processes
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", pady=12)
        self._section_label(inner, "PROCESSES")

        nf = tk.Frame(inner, bg=BG_PANEL)
        nf.pack(fill="x", pady=(4, 0))
        tk.Label(nf, text="Count:", font=FONT_LABEL,
                 bg=BG_PANEL, fg=TEXT_MID).pack(side="left")
        # Validate spinbox so only digits are accepted when typing manually
        def _spin_validate(proposed):
            if proposed == "":
                return True
            try:
                v = int(proposed)
                return 1 <= v <= 12  # allow in-progress typing of valid range
            except ValueError:
                return False

        _spin_vcmd = (nf.register(_spin_validate), "%P")
        self.n_spin = tk.Spinbox(
            nf, from_=3, to=12, width=4,
            textvariable=self.num_processes,
            font=FONT_LABEL, bg=BG_MAIN, fg=TEXT_DARK,
            relief="flat", highlightbackground=BORDER,
            highlightthickness=1, bd=0,
            buttonbackground=BG_SIDEBAR,
            validate="key",
            validatecommand=_spin_vcmd,
        )
        self.n_spin.pack(side="left", padx=8)

        # Buttons
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", pady=12)

        self._accent_btn(inner, "⟳  Refresh Table",
                         self._refresh_table).pack(fill="x", pady=(0, 8))
        self._accent_btn(inner, "▶  Run Simulation",
                         self._run_simulation, dark=True).pack(fill="x")

        # Info note
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", pady=12)
        note = ("Priority: lower value\n= higher priority")
        tk.Label(inner, text=note, font=FONT_SMALL,
                 bg=BG_SIDEBAR, fg=TEXT_MID,
                 justify="left", padx=8, pady=6,
                 wraplength=190).pack(fill="x")

    def _algo_radio(self, parent, value, label):
        var = self.algorithm
        rb = tk.Radiobutton(
            parent, text=label, variable=var, value=value,
            font=FONT_LABEL, bg=BG_PANEL, fg=TEXT_DARK,
            selectcolor=BG_PANEL, activebackground=BG_PANEL,
            activeforeground=ACCENT1,
            indicatoron=False,
            relief="flat", bd=0,
            highlightthickness=0,
            padx=10, pady=6,
            cursor="hand2",
            command=self._on_algo_change
        )
        rb.pack(fill="x", pady=1)

        # Style: selected state via trace
        def update_style(*_):
            if var.get() == value:
                rb.configure(bg=BG_SIDEBAR, fg=ACCENT1, font=("Helvetica Neue", 11, "bold"))
            else:
                rb.configure(bg=BG_PANEL, fg=TEXT_DARK, font=FONT_LABEL)

        var.trace_add("write", update_style)
        update_style()

    def _on_algo_change(self):
        """Enable/disable quantum entry and rebuild table when algorithm changes.
        User-entered values are preserved across algorithm switches."""
        algo = self.algorithm.get()
        # Quantum only applies to Round Robin variants
        state = "normal" if algo in ("RR", "Priority+RR") else "disabled"
        self.quantum_entry.configure(state=state)
        # Save whatever the user has typed before rebuilding rows
        self._save_current_inputs()
        # Rebuild headers and rows to show/hide Priority column
        self._rebuild_col_headers()
        self._refresh_table(reset=False)

    # ── Input Table ──────────────────────────────

    def _build_input_table(self, parent):
        """Build the editable process data table."""
        header_frame = tk.Frame(parent, bg=BG_PANEL, padx=16, pady=12)
        header_frame.pack(fill="x")

        tk.Label(header_frame, text="Process Input",
                 font=FONT_HEAD, bg=BG_PANEL, fg=TEXT_DARK).pack(side="left")
        tk.Label(header_frame,
                 text="Enter arrival time, burst time, and priority for each process",
                 font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_LIGHT).pack(side="left", padx=10, pady=4)

        # Column headers (rebuilt dynamically when algorithm changes)
        self.cols_frame = tk.Frame(parent, bg=ACCENT1, padx=16, pady=8)
        self.cols_frame.pack(fill="x")
        self._rebuild_col_headers()

        # Scrollable rows container
        self.table_frame = tk.Frame(parent, bg=BG_PANEL, padx=16, pady=4)
        self.table_frame.pack(fill="x")

        self._refresh_table()

    def _uses_priority(self):
        """Return True only for algorithms that require a priority input."""
        return self.algorithm.get() in ("Priority", "Priority+RR")

    def _rebuild_col_headers(self):
        """Redraw the column header bar, showing Priority only when needed."""
        for w in self.cols_frame.winfo_children():
            w.destroy()
        headers = ["PID", "Arrival Time", "Burst Time"]
        widths  = [6, 13, 11]
        if self._uses_priority():
            headers.append("Priority")
            widths.append(9)
        for h, w in zip(headers, widths):
            tk.Label(self.cols_frame, text=h, font=("Helvetica Neue", 10, "bold"),
                     bg=ACCENT1, fg="white", width=w, anchor="center").pack(side="left")

    def _save_current_inputs(self):
        """Snapshot whatever the user has typed into _saved_inputs."""
        for row in self.process_entries:
            pid = row["pid"]
            self._saved_inputs[pid] = {
                "arrival":  row["arrival"].get(),
                "burst":    row["burst"].get(),
                "priority": row["priority"].get(),
            }

    def _refresh_table(self, reset=True):
        """Rebuild the process entry rows.

        Args:
            reset: If True (Refresh button), use preset default values and
                   clear saved data.  If False (algo switch), restore whatever
                   the user had previously typed.
        """
        # When the user explicitly resets, wipe saved state
        if reset:
            self._saved_inputs.clear()

        for w in self.table_frame.winfo_children():
            w.destroy()
        self.process_entries.clear()

        show_priority = self._uses_priority()
        n = self.num_processes.get()
        for i in range(n):
            pid = f"P{i+1}"
            row = {}
            row["pid"] = pid

            # Use saved values if available, otherwise fall back to presets
            saved = self._saved_inputs.get(pid, {})
            row["arrival"]  = tk.StringVar(value=saved.get("arrival",  str(i * 2)))
            row["burst"]    = tk.StringVar(value=saved.get("burst",    str(4 + i)))
            row["priority"] = tk.StringVar(value=saved.get("priority", str(n - i)))

            rf = tk.Frame(self.table_frame, bg=BG_PANEL if i % 2 == 0 else BG_SIDEBAR)
            rf.pack(fill="x", pady=1)

            bg = rf["bg"]
            tk.Label(rf, text=pid, font=("Helvetica Neue", 10, "bold"),
                     bg=bg, fg=ACCENT1, width=6, anchor="center").pack(side="left")

            fields = [("arrival", 13), ("burst", 11)]
            if show_priority:
                fields.append(("priority", 9))

            for var, w in fields:
                e = self._styled_entry(rf, row[var], width=w, bg=bg)
                e.pack(side="left", padx=2, pady=3)

            self.process_entries.append(row)

    # ── Output Area ──────────────────────────────

    def _build_output_area(self, parent):
        """Build the tabbed output area: Gantt Chart + Results Table."""
        header_frame = tk.Frame(parent, bg=BG_PANEL, padx=16, pady=12)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="Simulation Output",
                 font=FONT_HEAD, bg=BG_PANEL, fg=TEXT_DARK).pack(side="left")

        # Tab bar (custom styled)
        self.tab_var = tk.StringVar(value="gantt")
        tab_bar = tk.Frame(parent, bg=BG_PANEL, padx=16)
        tab_bar.pack(fill="x")

        self._tab_buttons = {}
        for val, label in [("gantt", "Gantt Chart"), ("table", "Results Table")]:
            tb = tk.Button(
                tab_bar, text=label,
                font=FONT_LABEL,
                bg=BG_PANEL, fg=TEXT_MID,
                relief="flat", bd=0,
                padx=16, pady=6,
                cursor="hand2",
                command=lambda v=val: self._switch_tab(v)
            )
            tb.pack(side="left")
            self._tab_buttons[val] = tb

        # Separator
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x")

        self.gantt_frame = tk.Frame(parent, bg=BG_PANEL)
        self.table_out_frame = tk.Frame(parent, bg=BG_PANEL)
        self._switch_tab("gantt")

        # Canvas for Gantt chart
        self.gantt_canvas = tk.Canvas(self.gantt_frame, bg=BG_PANEL,
                                      highlightthickness=0)
        gantt_scroll = tk.Scrollbar(self.gantt_frame, orient="horizontal",
                                    command=self.gantt_canvas.xview)
        self.gantt_canvas.configure(xscrollcommand=gantt_scroll.set)
        gantt_scroll.pack(side="bottom", fill="x")
        self.gantt_canvas.pack(fill="both", expand=True, padx=16, pady=12)

        self._draw_gantt_placeholder()

        # Table output
        self._build_results_table(self.table_out_frame)

    def _switch_tab(self, tab):
        """Show the selected tab content."""
        self.tab_var.set(tab)
        for val, btn in self._tab_buttons.items():
            if val == tab:
                btn.configure(fg=ACCENT1, font=("Helvetica Neue", 11, "bold"))
            else:
                btn.configure(fg=TEXT_MID, font=FONT_LABEL)

        if tab == "gantt":
            self.table_out_frame.pack_forget()
            self.gantt_frame.pack(fill="both", expand=True)
        else:
            self.gantt_frame.pack_forget()
            self.table_out_frame.pack(fill="both", expand=True)

    def _build_results_table(self, parent):
        """Build the Treeview results table."""
        cols = ("PID", "Arrival", "Burst", "Priority",
                "Completion", "Turnaround", "Waiting")
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Pink.Treeview",
                         background=BG_PANEL,
                         fieldbackground=BG_PANEL,
                         foreground=TEXT_DARK,
                         rowheight=28,
                         font=FONT_LABEL)
        style.configure("Pink.Treeview.Heading",
                         background=ACCENT1,
                         foreground="white",
                         font=("Helvetica Neue", 10, "bold"),
                         relief="flat")
        style.map("Pink.Treeview",
                  background=[("selected", ACCENT2)],
                  foreground=[("selected", "white")])

        # Averages row — packed first so it anchors to the bottom
        self.avg_label = tk.Label(parent, text="",
                                   font=FONT_LABEL, bg=BG_PANEL, fg=TEXT_MID,
                                   pady=6)
        self.avg_label.pack(side="bottom", fill="x")

        tree_frame = tk.Frame(parent, bg=BG_PANEL, padx=16, pady=8)
        tree_frame.pack(fill="both", expand=True)

        self.results_tree = ttk.Treeview(tree_frame, columns=cols,
                                          show="headings", style="Pink.Treeview")
        widths = [60, 70, 65, 65, 90, 100, 80]
        for col, w in zip(cols, widths):
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                             command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.results_tree.pack(fill="both", expand=True)

    # ────────────────────────────────────────────
    #  SIMULATION AND DISPATCH
    # ────────────────────────────────────────────

    def _run_simulation(self):
        """Collect inputs, validate, dispatch to algorithm, render output."""
        try:
            processes = self._collect_input()
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return

        algo    = self.algorithm.get()
        quantum = None

        if algo in ("RR", "Priority+RR"):
            try:
                quantum = int(self.quantum_var.get())
                if quantum <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Input Error", "Time Quantum must be a positive integer.")
                return

        # Dispatch to the appropriate algorithm
        try:
            if algo == "FCFS":
                result = run_fcfs(processes)
            elif algo == "SJF":
                result = run_sjf(processes)
            elif algo == "SRT":
                result = run_srt(processes)
            elif algo == "RR":
                result = run_rr(processes, quantum)
            elif algo == "Priority":
                result = run_priority(processes)
            elif algo == "Priority+RR":
                result = run_priority_rr(processes, quantum)
            else:
                raise ValueError("Unknown algorithm")
        except Exception as e:
            messagebox.showerror("Simulation Error", str(e))
            return

        self._sim_result = result
        self._render_gantt(result["timeline"])
        self._render_results(result["results"], result["avg_wt"], result["avg_tat"])
        self._switch_tab("gantt")

    def _collect_input(self):
        """
        Parse and validate all process entry fields.
        Returns a list of process dicts.
        """
        processes = []
        pids_seen = set()

        for row in self.process_entries:
            pid = row["pid"]
            if pid in pids_seen:
                raise ValueError(f"Duplicate PID: {pid}")
            pids_seen.add(pid)

            try:
                arrival = int(row["arrival"].get())
                if arrival < 0:
                    raise ValueError
            except ValueError:
                raise ValueError(f"{pid}: Arrival Time must be a non-negative integer.")

            try:
                burst = int(row["burst"].get())
                if burst <= 0:
                    raise ValueError
            except ValueError:
                raise ValueError(f"{pid}: Burst Time must be a positive integer.")

            # Only parse priority when the algorithm requires it
            if self._uses_priority():
                try:
                    priority = int(row["priority"].get())
                except ValueError:
                    raise ValueError(f"{pid}: Priority must be an integer.")
            else:
                priority = 0  # Default; unused by non-priority algorithms

            processes.append({
                "pid":      pid,
                "arrival":  arrival,
                "burst":    burst,
                "priority": priority,
            })

        if len(processes) < 3:
            raise ValueError("Minimum 3 processes required.")

        return processes

    # ────────────────────────────────────────────
    #  GANTT CHART RENDERING
    # ────────────────────────────────────────────

    def _draw_gantt_placeholder(self):
        """Draw an empty placeholder Gantt."""
        c = self.gantt_canvas
        c.delete("all")
        c.create_text(400, 80, text="Run a simulation to see the Gantt chart",
                      font=FONT_LABEL, fill=TEXT_LIGHT)

    def _render_gantt(self, timeline):
        """
        Draw the Gantt chart on the canvas.
        Each process slice is a colored rectangle with PID label.
        Time ticks are drawn below.
        """
        c = self.gantt_canvas
        c.delete("all")

        if not timeline:
            self._draw_gantt_placeholder()
            return

        # Collect unique PIDs for color mapping
        pids      = list(dict.fromkeys(s["pid"] for s in timeline))
        pid_color = {pid: GANTT_COLORS[i % len(GANTT_COLORS)]
                     for i, pid in enumerate(pids)}

        BAR_H   = 48
        BAR_Y   = 30
        TICK_Y  = BAR_Y + BAR_H + 6
        LABEL_Y = BAR_Y + BAR_H + 22
        SCALE   = 36   # pixels per time unit

        max_t = max(s["end"] for s in timeline)
        total_w = max_t * SCALE + 80

        c.configure(scrollregion=(0, 0, total_w, BAR_Y + BAR_H + 50))

        # Legend row
        lx = 8
        for pid in pids:
            color = pid_color[pid]
            c.create_rectangle(lx, 6, lx+14, 20, fill=color, outline="")
            c.create_text(lx+20, 13, text=pid, font=FONT_SMALL,
                          fill=TEXT_DARK, anchor="w")
            lx += 60

        # Bars
        for slot in timeline:
            x0 = slot["start"] * SCALE + 4
            x1 = slot["end"]   * SCALE + 4
            y0 = BAR_Y
            y1 = BAR_Y + BAR_H
            color = pid_color[slot["pid"]]

            # Main bar
            c.create_rectangle(x0, y0, x1, y1,
                                fill=color, outline="white", width=1.5)

            # PID label (only if wide enough)
            if (x1 - x0) >= 18:
                c.create_text((x0+x1)/2, (y0+y1)/2,
                              text=slot["pid"],
                              font=("Helvetica Neue", 9, "bold"),
                              fill="white")

        # Time ticks
        shown_ticks = set()
        for slot in timeline:
            for t in (slot["start"], slot["end"]):
                if t not in shown_ticks:
                    shown_ticks.add(t)
                    x = t * SCALE + 4
                    c.create_line(x, TICK_Y, x, TICK_Y + 6,
                                  fill=TEXT_LIGHT, width=1)
                    c.create_text(x, LABEL_Y, text=str(t),
                                  font=FONT_SMALL, fill=TEXT_MID, anchor="center")

        # Baseline
        c.create_line(4, TICK_Y, total_w - 4, TICK_Y,
                      fill=BORDER, width=1)

    # ────────────────────────────────────────────
    #  RESULTS TABLE RENDERING
    # ────────────────────────────────────────────

    def _render_results(self, results, avg_wt, avg_tat):
        """Populate the Treeview with per-process metrics."""
        tree = self.results_tree
        for row in tree.get_children():
            tree.delete(row)

        # Show/hide Priority column based on algorithm
        show_priority = self._uses_priority()
        priority_width = 65 if show_priority else 0
        tree.column("Priority", width=priority_width,
                    minwidth=priority_width, stretch=False)

        for i, r in enumerate(results):
            tag = "even" if i % 2 == 0 else "odd"
            tree.insert("", "end", values=(
                r["pid"],
                r["arrival"],
                r["burst"],
                r["priority"] if show_priority else "",
                r["completion"],
                r["tat"],
                r["wt"],
            ), tags=(tag,))

        tree.tag_configure("even", background=BG_PANEL)
        tree.tag_configure("odd",  background=BG_SIDEBAR)

        self.avg_label.configure(
            text=f"  Average Waiting Time: {avg_wt:.2f} ms    │    "
                 f"Average Turnaround Time: {avg_tat:.2f} ms",
            font=("Helvetica Neue", 11, "bold"),
            fg=ACCENT1
        )

    # ────────────────────────────────────────────
    #  WIDGET HELPERS
    # ────────────────────────────────────────────

    def _section_label(self, parent, text):
        tk.Label(parent, text=text,
                 font=("Helvetica Neue", 8, "bold"),
                 bg=BG_PANEL, fg=TEXT_LIGHT,
                 anchor="w").pack(fill="x", pady=(10, 3))

    def _styled_entry(self, parent, textvariable, width=10, bg=BG_MAIN):
        """Create a styled Entry that only accepts integer digits (and an
        optional leading minus sign for priority fields)."""

        def _validate(proposed):
            if proposed == "" or proposed == "-":
                return True
            try:
                int(proposed)
                return True
            except ValueError:
                return False

        vcmd = (parent.register(_validate), "%P")

        e = tk.Entry(
            parent, textvariable=textvariable,
            width=width, font=FONT_LABEL,
            bg=bg, fg=TEXT_DARK,
            relief="flat",
            highlightbackground=BORDER,
            highlightcolor=ACCENT1,
            highlightthickness=1,
            insertbackground=ACCENT1,
            bd=0,
            validate="key",
            validatecommand=vcmd,
        )
        return e

    def _accent_btn(self, parent, text, command, dark=False):
        bg = ACCENT1 if dark else BG_SIDEBAR
        fg = "white" if dark else ACCENT1
        b = tk.Button(
            parent, text=text, command=command,
            font=FONT_BTN, bg=bg, fg=fg,
            relief="flat", bd=0,
            activebackground=ACCENT3 if dark else BORDER,
            activeforeground="white" if dark else ACCENT1,
            padx=12, pady=9, cursor="hand2"
        )
        return b


# ═══════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    app = CPUSchedulerApp()
    # Center on screen
    app.update_idletasks()
    w, h = 1200, 820
    sw   = app.winfo_screenwidth()
    sh   = app.winfo_screenheight()
    app.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
    app.mainloop()