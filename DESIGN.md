# Program design

This app follows the **six-step design recipe** from
[*How to Design Programs*](https://htdp.org/) (HtDP). The recipe turns a
problem statement into working code by producing a fixed set of intermediate
products at each step.

| Step | Product |
|------|---------|
| 1. Data analysis | Data definitions and data examples |
| 2. Interface | Signature and purpose statement |
| 3. Examples | Worked input → output examples |
| 4. Template | Skeleton from the data shape |
| 5. Definition | Complete function body |
| 6. Tests | Checks against the examples |

Below, each major piece of the Streamlit app is documented with that process.
Python and Streamlit replace Racket and `check-expect`, but the steps are the
same: **understand the data, then invent the functions**.

---

## Problem statement

**Domain:** used-vehicle market analysis (dataset `vehicles_us.csv`).

**Goal:** let a user explore price and mileage interactively:

1. Optionally show a scatter plot of odometer vs price (log scale), colored by brand.
2. Optionally show a histogram of prices, colored by condition.
3. Exclude placeholder listings (e.g. price of $1) so charts reflect real asking prices.

**I/O of the program as a whole:**

- **Input:** checkbox choices from the user (show scatter? show histogram?).
- **Output:** zero, one, or two Plotly figures rendered in the browser.

---

## 1. Data analysis

### Information vs data

| Information (domain) | Data representation |
|----------------------|---------------------|
| Vehicle listing row | One row of a `pandas.DataFrame` loaded from CSV |
| Full catalog of listings | `DataFrame` after cleaning and enrichment |
| User wants scatter / histogram | Two booleans |
| Optional chart | `plotly.graph_objs` figure **or** `None` |

### Data definitions

```text
; A VehicleDF is a DataFrame with at least:
;   - price        : Number  (USD asking price; rows with price <= 1 are dropped)
;   - odometer     : Int or NA
;   - model_year   : Int or NA
;   - model        : String
;   - condition    : String (category for histogram color)
;   - brand        : String  (first token of model; derived)
;   - age          : Int or NA  (2020 - model_year; derived)
;   - log_price, log_odometer : Number (derived; available for analysis)
;
; Interpretation: one used-vehicle listing after EDA-style prep.

; A ControlFlags is:
;   ControlFlags(show_scatter: bool, show_histo: bool)
;
; Interpretation: which plots the user requested in the UI.

; A OptionalFigure is one of:
;   - a Plotly figure
;   - None
;
; Interpretation: a chart to render, or "no chart" when the user did not request it.

; A PlotPair is:
;   (OptionalFigure, OptionalFigure)
;
; Interpretation: (scatter, histogram) in that order.
```

### Data examples (illustrative)

```text
; Minimal VehicleDF idea (conceptual rows):
;   price=15000, odometer=80000, model="toyota camry", condition="good"
;     → brand="toyota", age=2020-model_year, kept (price > 1)
;   price=1, ...
;     → dropped by the price filter

; ControlFlags examples:
;   ControlFlags(False, False)  ; show nothing
;   ControlFlags(True, False)   ; scatter only
;   ControlFlags(False, True)   ; histogram only
;   ControlFlags(True, True)    ; both
```

---

## 2. Signatures and purpose statements

### `data_prep`

```text
; data_prep : [path: String] -> VehicleDF
; Purpose: load vehicles_us.csv, coerce types, enrich with brand/age/log
;   columns, and remove placeholder prices so downstream plots use clean data.
; Header:
def data_prep(path: str = "vehicles_us.csv") -> pd.DataFrame: ...
```

Cached with `@st.cache_data` so toggling checkboxes does not re-read the CSV
on every interaction (performance detail; does not change the signature).

### `ControlFlags`

```text
; make-control-flags : Boolean Boolean -> ControlFlags
; Purpose: bundle the two UI choices into one value so plot generation
;   takes a single control argument instead of a growing parameter list.
@dataclass
class ControlFlags:
    show_scatter: bool
    show_histo: bool
```

### `gen_plots`

```text
; gen_plots : VehicleDF ControlFlags -> PlotPair
; Purpose: build the scatter and/or histogram the user asked for; use None
;   for any plot that was not requested.
def gen_plots(df, control: ControlFlags): ...
```

### Top-level program (Streamlit script)

```text
; main : -> void (side effects: render UI)
; Purpose: present title and checkboxes, prepare data once, generate plots
;   from the current flags, and display each non-None figure.
```

---

## 3. Examples (input → output)

Examples guide the implementation before (and after) coding.

| `ControlFlags` | Expected `PlotPair` |
|----------------|---------------------|
| `(False, False)` | `(None, None)` — page shows no charts |
| `(True, False)` | `(scatter, None)` — only odometer vs price |
| `(False, True)` | `(None, histo)` — only price distribution |
| `(True, True)` | `(scatter, histo)` — both charts |

For `data_prep`:

| Situation | Expected result |
|-----------|-----------------|
| Row with `price == 1` | Not present in returned `DataFrame` |
| Row with `model == "ford f-150"` | `brand == "ford"` |
| `model_year` present | `age == 2020 - model_year` |
| Numeric columns with bad strings | Coerced with `errors='coerce'` (may become NA) |

Scatter design choices reflected in examples:

- y-axis is **log scale** on price (spread of cheap vs expensive cars).
- Color encodes **brand**.
- Histogram color encodes **condition**, ~60 bins.

---

## 4. Templates

Templates come from the **shape of the data**, not from inventing code ad hoc.

### Template for something that consumes `ControlFlags`

```text
def fn_for_flags(control: ControlFlags):
    # inventory:
    control.show_scatter  # Boolean
    control.show_histo    # Boolean
    ...
```

### Template for `gen_plots` (product of two independent options)

```text
def gen_plots(df, control: ControlFlags):
    scatter = None
    histo = None
    if control.show_scatter:
        scatter = ...  # build scatter from df
    if control.show_histo:
        histo = ...    # build histogram from df
    return (scatter, histo)
```

Each boolean is a two-case distinction (`True` / `False`); the plot is only
constructed on the `True` branch.

### Template for `data_prep` (pipeline over a table)

```text
def data_prep(path=...):
    df = load(path)
    df = coerce_types(df)
    df = enrich(df)      # brand, age, logs
    df = filter_rows(df) # price > 1
    return df
```

### Template for the main script (world program / interaction)

```text
# 1. fixed presentation
st.title(...)
st.write(...)
# 2. inputs (big-bang style "handlers" as widgets)
show_scatter = st.checkbox(...)
show_histo = st.checkbox(...)
# 3. pure-ish core
dataset = data_prep()
flags = ControlFlags(show_scatter, show_histo)
scatter_fig, histo_fig = gen_plots(dataset, flags)
# 4. view: render optional figures
if scatter_fig is not None: st.plotly_chart(scatter_fig)
if histo_fig is not None: st.plotly_chart(histo_fig)
```

---

## 5. Function definitions

The filled-in bodies live in [`app.py`](app.py). Mapping recipe → code:

| Design product | Implementation |
|----------------|----------------|
| `ControlFlags` data def | `@dataclass class ControlFlags` |
| `data_prep` | load → dtype coercion → brand/age/logs → `query('price > 1')` |
| `gen_plots` | conditional `px.scatter` / `px.histogram`; return pair |
| Main | checkboxes → flags → plots → conditional `st.plotly_chart` |

**Composition (wish list):**

1. Wish: clean table → `data_prep`
2. Wish: flags + table → figures → `gen_plots`
3. Wish: package UI booleans → `ControlFlags`
4. Main only wires Streamlit I/O around those helpers

That separation keeps **data prep** and **plot construction** testable without
the UI, which is the HtDP habit of not putting everything in one function.

---

## 6. Tests

HtDP closes the loop with automated checks. In this project the “tests” are
layered:

1. **Examples as manual checks** — toggle both checkboxes on the live app
   ([Render deployment](https://webapp-8ze9.onrender.com)) and confirm the four
   `ControlFlags` cases from step 3.
2. **EDA notebook** — [`EDA.ipynb`](EDA.ipynb) explores distributions and
   motivated filters (e.g. dropping `$1` placeholders) and chart choices
   *before* they were wired into Streamlit.
3. **Future automated tests** (if added) would mirror `check-expect`:

```python
# Sketch only — not necessarily in the repo yet
def test_price_filter():
    df = data_prep()
    assert (df["price"] > 1).all()

def test_gen_plots_none():
    df = data_prep()
    s, h = gen_plots(df, ControlFlags(False, False))
    assert s is None and h is None

def test_gen_plots_both():
    df = data_prep()
    s, h = gen_plots(df, ControlFlags(True, True))
    assert s is not None and h is not None
```

---

## Design checklist (how to extend the app)

When adding a new feature (e.g. a third chart or a year filter), re-run the
recipe for that wish:

1. **Data** — What new information must be represented? Extend a data def or add one.
2. **Signature / purpose** — One sentence: what does the new function consume and produce?
3. **Examples** — At least two concrete cases (edge + normal).
4. **Template** — Branch on the new data shape (booleans, enums, columns).
5. **Define** — Fill the template; keep Streamlit widgets at the edges.
6. **Test** — Check examples manually or with `pytest`.

Do not start at step 5. The earlier steps are what keep interactive apps from
becoming an unplanned pile of widgets.
