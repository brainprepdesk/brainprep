"""
HTML reporting
==============

Simple example.

Example on how to aggregate QC information in an HTML report.
See :ref:`user guide <reporting>` for details.

Data
----

Let's first get some data to display. Here 'step 1' is composed of an
image with an overlay and a table, and 'step 2' is composed of a
carousel of two images.
"""

import pandas as pd
from pathlib import Path

from brainprep.datasets import git_download


working_dir = Path("/tmp/brainprep-reporting")
working_dir.mkdir(parents=True, exist_ok=True)


git_download(
    url=("https://raw.githubusercontent.com/neurospin-deepinsight/brainprep/"
         "dev/doc/logos/brainprep.png"),
    destination=working_dir / "im1.png",
)
git_download(
    url=("https://raw.githubusercontent.com/neurospin-deepinsight/brainprep/"
         "dev/doc/logos/brainprep.png"),
    destination=working_dir / "im2.png",
)

data = [
  {
    "name": "Step 1",
    "content": working_dir / "im1.png",
    "overlay": working_dir / "im2.png",
    "tables": pd.DataFrame(
        data={'col1': [1, 2], 'col2': [4, 3]}
    ),
  },
  {
    "name": "Step 2",
    "content": [
        working_dir / "im1.png",
        working_dir / "im2.png",
    ],
  },
]


# %%
# Reporting
# ---------
# 
# Now let's geerate the HTML report.

from brainprep.reporting import generate_qc_report

report = generate_qc_report(
  title="Simple QC Example",
  docstring="""
  This is a simple example.
  
  ..note::
      Please adapt this code.
  """,
  version="0.0.0",
  date="01.01.2000",
  data=data,
)
report
report.save_as_html(working_dir / "report.html")
