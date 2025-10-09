##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Interface for MRIQC.
"""

import os
import shutil

import brainprep.interfaces as interfaces

from ..reporting import (
    log_runtime,
    save_runtime,
)
from ..typing import (
    Directory,
    File,
)
from ..utils import (
    Bunch,
    bids,
)


@bids(
    process="quality_assurance",
    bids_file="image_files",
    container="neurospin/brainprep-qa")
@log_runtime(
    title="Subject Level Quality Assurance")
@save_runtime
def brainprep_quality_assurance(
        image_files: list[File],
        output_dir: Directory,
        keep_intermediate: bool = False) -> Bunch:
    """
    Subject level quality assurance pre-processing workflow for MRI images.

    Applies MRIQC tool :footcite:p:`esteban2017mriqc` with subject level
    default settings.

    Parameters
    ----------
    image_files : list[File]
        Path to the input image files of one subject.
    output_dir : Directory
        Directory where the quality assurance related outputs will be saved
        (i.e., the root of your dataset).
    keep_intermediate : bool, default False
        If True, retains intermediate results (i.e., the workspace); useful
        for debugging.

    Returns
    -------
    Bunch
        A dictionary-like object containing:
        - iqm_files : list[File] — paths to the subject level Image Quality
          Metrics (IQMs).

    Notes
    -----
    This workflow assumes the input images are organized in BIDS.

    Examples
    --------
    >>> from brainprep.workflow import brainprep_quality_assurance
    >>> brainprep_quality_assurance([t1_file, dwi_file], output_dir)

    References
    ----------

    .. footbibliography::
    """
    workspace_dir, iqm_files = interfaces.subject_level_qa(
        image_files,
        output_dir,
    )

    if not keep_intermediate:
        shutil.rmtree(workspace_dir)

    return Bunch(
        iqm_files=iqm_files,
    )


@bids(
    process="quality_assurance")
@log_runtime(
    title="Group Level Quality Assurance")
@save_runtime
def brainprep_group_quality_assurance(
        output_dir: Directory,
        keep_intermediate: bool = False) -> Bunch:
    """
    Group lebel quality assurance pre-processing workflow for MRI images.

    Applies MRIQC tool :footcite:p:`esteban2017mriqc` with group level
    default settings.

    Parameters
    ----------
    output_dir : Directory
        Directory where the quality assurance related outputs will be saved
        (i.e., the root of your dataset).
    keep_intermediate : bool, default False
        If True, retains intermediate results (no effect on this workflow).

    Returns
    -------
    Bunch
        A dictionary-like object containing:
        - iqm_file : File — paths to the group level Image Quality Metrics
          (IQMs).

    Notes
    -----
    This workflow assumes the subject level analysis have already been.

    Examples
    --------
    >>> from brainprep.workflow import brainprep_group_quality_assurance
    >>> brainprep_group_quality_assurance(output_dir)

    References
    ----------

    .. footbibliography::
    """
    iqm_file = interfaces.group_level_qa(
        output_dir,
    )

    return Bunch(
        iqm_file=iqm_file,
    )


def brainprep_mriqc(rawdir, subjid, outdir="/out", workdir="/work",
                    mriqc="mriqc"):
    """ Define the mriqc pre-processing workflow.

    Parameters
    ----------
    rawdir: str
        the BIDS raw folder.
    subjid: str
        the subject identifier.
    outdir: str
        the destination folder.
    workdir: str
        the working folder.
    mriqc: str
        path to the mriqc binary.
    """
    print_title("Launch mriqc...")
    status = os.path.join(outdir, subjid, "ok")
    if not os.path.isfile(status):
        cmd = [
            mriqc,
            rawdir,
            outdir,
            "participant",
            "-w", workdir,
            "--no-sub",
            "--participant-label", subjid]
        brainprep.execute_command(cmd)
        open(status, "a").close()


def compute_score(data, dtype_iqms):
    """ Compute an agregation score.

    Parameters
    ----------
    data: DataFrame
        the table with the raw scores.
    dtype_iqms: dict
        specify which IQM needs to be maximized/minimized.

    Returns
    -------
    score: array
        the generated summary score.
    """
    score = np.zeros((len(data), ), dtype=data.values.dtype)
    if "dummy_trs" in data.columns:
        _data = data.drop(columns=["_id", "source", "dummy_trs"])
    else:
        _data = data.drop(columns=["_id", "source"])
    _columns = _data.columns.tolist()
    _data = MinMaxScaler().fit_transform(_data.values)
    for key in _columns:
        to_maximize = dtype_iqms[key]
        index = _columns.index(key)
        if to_maximize:
            score += _data[:, index]
        else:
            score += (1 - _data[:, index])
    score /= len(_columns)
    return score


def detect_outliers(data, percentiles=[95, 5]):
    """ Detect outliers.
    Lower outlier threshold is calculated as 5% quartile(data) -
    1.5*IQR(data); upper outlier threshold calculated as 95% quartile(data) +
    1.5*IQR(data).

    Parameters
    ----------
    data: DataFrame
        the table with the data to QC.
    percentiles: 2-uplet, default [95, 5]
        sequence of percentiles to compute.

    Returns
    -------
    qc: array
        the QC result as a binary vector.
    """
    qc = []
    for key in data.columns:
        if key in ["_id", "source", "dummy_trs"]:
            continue
        api_data = data[data["source"] == "api"]
        q2, q1 = np.percentile(api_data[key], percentiles)
        iqr = q2 - q1
        min_out = q1 - 1.5 * iqr
        max_out = q2 + 1.5 * iqr
        qc.append(np.logical_and((data[key].values <= max_out),
                                 (data[key].values >= min_out)))
    qc = np.all(np.asarray(qc), axis=0)
    return qc


def load_iqms(files):
    """ Load/merge individual IQM file.

    Parameters
    ----------
    files: list
        the input mriqc IQM files.

    Returns
    -------
    mergedf: DataFrame
        the merged IQM data.
    """
    data = []
    for path in files:
        name = os.path.basename(path).split(".")[0]
        with open(path, "rt") as of:
            _data = json.load(of)
        _data["_id"] = name
        data.append(_data)
    return pd.json_normalize(data)


def plot_iqms(data, dtype, outdir, rm_outliers=False):
    """ Make a violin plot of the api and user IQMs.

    Parameters
    ----------
    data: DataFrame
        a table including the api and uer data. Must have a column labeled
        'source' with 'user' or 'api' defined.
    dtype: str
        the data type in the input table.
    outdir: str
        the destination folder.
    rm_outliers: bool, default False
        remove outliers from the API data.

    Returns
    -------
    A violin plot of each MRIQC metric, comparing the user-level data to
    the API data.
    """
    # Filter outliers
    if rm_outliers:
        data = data.reset_index(drop=True)
        var_name = "snr_total"
        if var_name not in data.columns:
            var_name = "snr"
        user_index = data[data["source"] == "user"].index
        api_data = data[data["source"] == "api"]
        q75, q25 = np.percentile(api_data[var_name].values, [75, 25])
        iqr = q75 - q25
        min_out = q25 - 1.5 * iqr
        max_out = q75 + 1.5 * iqr
        api_data = api_data[api_data[var_name] <= max_out]
        api_data = api_data[api_data[var_name] >= min_out]
        api_index = api_data.index
        index = user_index.values.tolist() + api_index.values.tolist()
        data = data.iloc[index]

    # Change the table from short format to long format
    df_long = pd.melt(data, id_vars=["_id", "source"], var_name="var",
                      value_name="val")

    # Make colors dictionary for family:
    # temporal: #D2691E
    # spatial: #DAA520
    # noise: #A52A2A
    # motion: #66CDAA
    # artifact: #6495ED
    # descriptive: #00008B
    # other: #9932CC
    plot_dict = {
        "tsnr": "#D2691E", "gcor": "#D2691E", "dvars_vstd": "#D2691E",
        "dvars_std": "#D2691E", "dvars_nstd": "#D2691E",
        "fwhm_x": "#DAA520", "fwhm_y": "#DAA520", "fwhm_z": "#DAA520",
        "fwhm_avg": "#DAA520", "fber": "#DAA520", "efc": "#DAA520",
        "cjv": "#A52A2A", "cnr": "#A52A2A", "qi_2": "#A52A2A",
        "snr": "#A52A2A", "snr_csf": "#A52A2A", "snr_gm": "#A52A2A",
        "snr_wm": "#A52A2A", "snr_total": "#A52A2A", "snrd_csf": "#A52A2A",
        "snrd_gm": "#A52A2A", "snrd_wm": "#A52A2A",
        "fd_mean": "#66CDAA", "fd_num": "#66CDAA", "fd_perc": "#66CDAA",
        "inu_med": "#6495ED", "inu_range": "#6495ED", "wm2max": "#6495ED",
        "aor": "#9932CC", "aqi": "#9932CC", "dummy_trs": "#9932CC",
        "gsr_x": "#9932CC", "gsr_y": "#9932CC", "qi_1": "#9932CC",
        "rpve_csf": "#9932CC", "rpve_gm": "#9932CC", "rpve_wm": "#9932CC",
        "tpm_overlap_csf": "#9932CC", "tpm_overlap_gm": "#9932CC",
        "tpm_overlap_wm": "#9932CC",
        "icvs_csf": "#00008B", "icvs_gm": "#00008B", "icvs_wm": "#00008B",
        "summary_bg_k": "#00008B", "summary_bg_mad": "#00008B",
        "summary_bg_mean": "#00008B", "summary_bg_median": "#00008B",
        "summary_bg_n": "#00008B", "summary_bg_p05": "#00008B",
        "summary_bg_p95": "#00008B", "summary_bg_stdv": "#00008B",
        "summary_csf_k": "#00008B", "summary_csf_mad": "#00008B",
        "summary_csf_mean": "#00008B", "summary_csf_median": "#00008B",
        "summary_csf_n": "#00008B", "summary_csf_p05": "#00008B",
        "summary_csf_p95": "#00008B", "summary_csf_stdv": "#00008B",
        "summary_fg_k": "#00008B", "summary_fg_mad": "#00008B",
        "summary_fg_mean": "#00008B", "summary_fg_median": "#00008B",
        "summary_fg_n": "#00008B", "summary_fg_p05": "#00008B",
        "summary_fg_p95": "#00008B", "summary_fg_stdv": "#00008B",
        "summary_gm_k": "#00008B", "summary_gm_mad": "#00008B",
        "summary_gm_mean": "#00008B", "summary_gm_median": "#00008B",
        "summary_gm_n": "#00008B", "summary_gm_p05": "#00008B",
        "summary_gm_p95": "#00008B", "summary_gm_stdv": "#00008B",
        "summary_wm_k": "#00008B", "summary_wm_mad": "#00008B",
        "summary_wm_mean": "#00008B", "summary_wm_median": "#00008B",
        "summary_wm_n": "#00008B", "summary_wm_p05": "#00008B",
        "summary_wm_p95": "#00008B", "summary_wm_stdv": "#00008B"
        }

    for var_name, df in df_long.groupby(by="var"):
        plt.figure()
        df = df.assign(hue=1)
        sns.boxplot(x="source", y="val", data=df, color=plot_dict[var_name],
                    hue="hue", hue_order=[1, 0])
        graph = sns.violinplot(x="source", y="val", data=df, color="0.8",
                               hue="hue", hue_order=[0, 1], split=True)
        graph.legend_.remove()
        graph = sns.stripplot(x="source", y="val", data=df, jitter=True,
                              alpha=0.4, color=plot_dict[var_name])
        ax = plt.gca()
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_ylabel(var_name)
        plt.savefig(os.path.join(outdir, "{}_{}.png".format(dtype, var_name)))
