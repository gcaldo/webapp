# webapp
This is the repository of my first ever web application.

## Setup

### Conda / Anaconda / Miniforge

```bash
conda env create -f environment.yml
conda activate webapp
```

Or with mamba: `mamba env create -f environment.yml`.

### Pip only

```bash
pip install -r requirements.txt
```

## Running the notebook

`EDA.ipynb` explores the vehicle listings data.

1. Create and activate the `webapp` environment (see above).
2. Open `EDA.ipynb` and select the **webapp** Python interpreter / kernel.

VS Code, Cursor, and Jupyter usually detect the conda env automatically once `ipykernel` is installed (included in `environment.yml`).

If the env does not appear as a kernel (common in classic JupyterLab / Notebook), register it once:

```bash
conda activate webapp
python -m ipykernel install --user --name webapp --display-name "Python (webapp)"
```

Then choose **Python (webapp)** as the notebook kernel.

## Running the Streamlit app

```bash
conda activate webapp
streamlit run app.py
```
