"""
Interpretability of the image quality metrics
=============================================

Tutorial.

MRIQC provides a comprehensive framework for assessing the quality of
MR images in research studies. Alongside its visual reports, it generates
a large collection of Image Quality Metrics (IQMs) that quantify different
aspects of image integrity. While this breadth of information is valuable,
the sheer number of available metrics can make it challenging for researchers
to determine which IQMs are most informative when judging the quality of a
specific image. Clear guidance on which metrics to prioritize can help
streamline quality assessment and support more consistent decision‑making
across studies.

Data
----

The T1w IQMs used in this analysis were downloaded from the MRIQC
Quality Control REST API:

``https://mriqc.nimh.nih.gov/api/v1/T1w``

This endpoint provides community‑contributed Image Quality Metrics (IQMs)
for T1‑weighted structural MRI scans, enabling comparisons against large
normative datasets.
"""

import brainprep
import numpy as np
import pandas as pd
from pathlib import Path


resource_dir = Path(brainprep.__file__).parent / "resources"
data_df = pd.read_csv(resource_dir / "iqm_T1w.csv")
columns = [
    name
    for name in data_df.columns
    if not name.startswith(("provenance.", "bids_meta.", "size_", "spacing_",
                            "summary_", "tpm_"))
]
data_df = data_df[sorted(columns)]
iqms = data_df.drop([
    "_created",
    "_etag",
    "_id",
    "_links.self.href",
    "_links.self.title",
    "_updated"
], axis=1)
print(iqms)


# %%
# Data scaling
# ------------
# 
# Normalizing the IQMs is essential because the metrics span very different
# numerical ranges, and many downstream analyses assume comparable scales.
# Bringing all features onto a similar magnitude improves numerical stability
# and prevents any single metric from dominating purely due to its units.

from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
iqms_scaled = scaler.fit_transform(iqms)
iqms_scaled = pd.DataFrame(
    iqms_scaled,
    columns=iqms.columns,
    index=iqms.index
)

# %%
# Visualizing the IQMs
# --------------------
# 
# To gain an initial sense of how the IQMs relate to one another, we
# visualize their pairwise scatterplots. Because MRIQC provides a large
# number of IQMs, we display only a selected subset here.

import matplotlib.pyplot as plt
import seaborn as sns

sns.pairplot(iqms_scaled[iqms_scaled.columns[-2:]])

# %%
# Interesting patterns emerge in the scatterplots: several IQMs show
# clear non‑linear relationships, which is important to keep in mind if
# linear dimensionality‑reduction methods struggle to capture the structure
# of the data. At the same time, many metrics are strongly correlated,
# underscoring how much redundancy exists within the full set of IQMs.
# 
# Feature selection
# -----------------
# 
# The redundancy among the IQMs makes the dataset especially suitable for
# feature selection, because many metrics capture overlapping aspects
# of image quality and therefore contribute similar information. Reducing the
# feature space helps isolate the dominant sources of variation and yields a
# more interpretable, lower‑dimensional representation of the data.


def greedy_uncorrelated(df, threshold=0.8):
    """
    Select a subset of approximately uncorrelated features from a DataFrame.

    This function iterates through the columns of the input DataFrame and
    greedily builds a set of features whose pairwise absolute correlations
    remain below a specified threshold. The first column is always selected,
    and each subsequent column is included only if it is sufficiently
    uncorrelated with all previously selected features.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing the features to evaluate.
    threshold : float
        Maximum allowed absolute correlation between any pair of selected
        features. Columns with correlations above this value are excluded.
        Default is 0.8.

    Returns
    -------
    selected : list of str
        List of column names corresponding to the selected uncorrelated
        features.

    Notes
    -----
    This is a greedy algorithm: the order of columns in `df` affects the
    resulting selection.
    """
    corr_df = df.corr().abs()
    selected = []
    for col in corr_df.columns:
        if all(corr_df.loc[col, sel_col] < threshold for sel_col in selected):
            selected.append(col)
    return selected


uncorrelated = greedy_uncorrelated(iqms_scaled, threshold=0.45)
iqms_reduced = iqms_scaled[uncorrelated]
print(iqms_reduced)

# %%
# The metrics should not be too strongly correlated.

plt.figure(figsize=(12, 10))
corr = iqms_reduced.corr()
sns.heatmap(
    corr,
    mask=np.triu(np.ones_like(corr, dtype=bool), k=0),
    cmap="coolwarm",
    vmin=-1, vmax=1,
    square=True,
    linewidths=0.5,
    cbar_kws={"shrink": 0.8}
)
