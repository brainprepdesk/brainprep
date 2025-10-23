# -*- coding: utf-8 -*-
##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2022
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Brain parcellation pre-processing.
"""

import os
from pathlib import Path
import shutil
from typing import Optional

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
    coerceparams,
    find_stack_level,
    parse_bids_keys,
    print_deprecated,
    print_info,
)


@bids(
    process="brain_parcellation",
    bids_file="t1_file",
    container="neurospin/brainprep-brainparc")
@log_runtime(
    title="Brain parcellation")
@save_runtime
@coerceparams
def brainprep_brainparc(
        t1_file: File,
        template_dir: Directory,
        output_dir: Directory,
        do_lgi: bool = False,
        wm_file: Optional[File] = None) -> Bunch:
    """
    Brain parcellation pre-processing.

    Applies the brain parcellation pre-processing described in
    :footcite:p:`dufumier2022openbhb`. This includes:

    1) Automated cortical reconstruction and volumetric segmentation from
       structural T1w MRI data using FreeSurfer's `recon-all`.
    2) Compute local Gyrification Index (localGI or lGI) - optional.
    3) Interhemispheric surface-based registration using the `fsaverage_sym`
       template.
    4) Project the different cortical features to the 'fsaverage_sym' template
       space.
    5) Convert FreeSurfer images back to original Nifti space.

    Parameters
    ----------
    t1_file : File
        Path to the input T1w image file.
    template_dir : Directory
        Path to the 'fsaverage_sym' template.
    output_dir : Directory
        FreeSurfer working directory containing all the subjects.
    do_lgi : bool, default False
        Perform the Local Gyrification Index (LGI) computation - requires
        Matlab.
    wm_file : Optional[File], default None
        Path to the custom white matter mask - we assume `recon-all` has been
        run at least upto the 'wm.mgz' file creation. It has to be
        in the subject's FreeSurfer space (1mm iso + aligned with brain.mgz)
        with values in [0, 1] (i.e. probability of being white matter).
        For example, it can be the 'brain_pve_2.nii.gz' white matter
        probability map created by FSL `fast`.

        .. deprecated:: 1.0.0

        .. admonition:: Do not use ``wm_file``!
           :class: important

           This option was removed as it is never used in Population Imaging
           studies. This parameter has no effect!

    Returns
    -------
    Bunch
        A dictionary-like object containing:
        - left_reg_file : File - left hemisphere registered to
          `fsaverage_sym` symmetric template.
        - right_reg_file : File - right hemisphere registered to
          `fsaverage_sym` symmetric template via xhemi.
        - features : tuple[File] - a tuple containing features in the
          `fsaverage_sym` symmetric template - each feature file is a MGH
          file with the suffix "fsaverage_sym" and is available in the
          'surf' folder.
        - images : tuple[File] — a tuple containing converted images - a
          Nifti file available in the 'mri' folder.

    Notes
    -----
    This workflow assumes the T1w image is organized in BIDS.

    Examples
    --------
    >>> from brainprep.workflow import brainprep_brainparc
    >>> brainprep_brainparc(t1_file, template_dir, output_dir)

    Raises
    ------
    ValueError
        If the input T1w file is not BIDS-compliant.

    References
    ----------

    .. footbibliography::
    """
    entities = parse_bids_keys(t1_file)
    if len(entities) == 0:
        raise ValueError(
            f"The T1w file '{t1_file}' is not BIDS-compliant."
        )
    if wm_file is not None:
        print_deprecated(
            "You passed a white matter file as input. This behavior is "
            "deprecated and will be removed in version >1."
        )
    log_file = interfaces.reconall(
        t1_file,
        output_dir,
        entities,
        resume=False,
    )
    interfaces.freesurfer_command_status(
        log_file,
        command="recon-all",
    )
    if do_lgi:
        left_lgi_file, right_lgi_file = interfaces.localgi(
            output_dir,
            entities,
        )
        interfaces.freesurfer_command_status(
            log_file,
            command="recon-all",
        )
    left_reg_file, right_reg_file = interfaces.fsaveragesym_surfreg(
        template_dir,
        output_dir,
        entities,
    )
    (lh_thickness_file, rh_thickness_file, lh_curv_file, rh_curv_file,
     lh_area_file, rh_area_file, lh_pial_lgi_file, rh_pial_lgi_file,
     lh_sulc_file, rh_sulc_file) = interfaces.fsaveragesym_projection(
        left_reg_file,
        right_reg_file,
        template_dir,
        output_dir,
        entities,
    )
    (aparc_aseg_file, aparc_a2009s_aseg_file, aseg_file, wm_file,
     rawavg_file, ribbon_file, brain_file) = interfaces.mgz_to_nii(
        output_dir,
        entities,
    )

    return Bunch(
        left_reg_file=left_reg_file,
        right_reg_file=right_reg_file,
        lh_thickness_file=lh_thickness_file,
        rh_thickness_file=rh_thickness_file,
        lh_curv_file=lh_curv_file,
        rh_curv_file=rh_curv_file,
        lh_area_file=lh_area_file,
        rh_area_file=rh_area_file,
        lh_pial_lgi_file=lh_pial_lgi_file,
        rh_pial_lgi_file=rh_pial_lgi_file,
        lh_sulc_file=lh_sulc_file,
        rh_sulc_file=rh_sulc_file,
        aparc_aseg_file=aparc_aseg_file,
        aparc_a2009s_aseg_file=aparc_a2009s_aseg_file,
        aseg_file=aseg_file,
        wm_file=wm_file,
        rawavg_file=rawavg_file,
        ribbon_file=ribbon_file,
        brain_file=brain_file,
    )


def brainprep_fsreconall_longitudinal(
        sid, fsdirs, outdir, timepoints, do_lgi=False, wm=None):
    """ Assuming you have run recon-all for all timepoints of a given subject,
    and that the results are stored in one subject directory per timepoint,
    this function will:

    - create a template for the subject and process it with recon-all
    - rerun recon-all for all timepoints of the subject using the template

    Parameters
    ----------
    fsdirs: list of str
        the FreeSurfer working directory where to find the the subject
        associated timepoints.
    sid: str
        the current subject identifier.
    outdir: str
        destination folder.
    timepoints: list of str, default None
        the timepoint names in the same order as the ``subjfsdirs``.
        Used to create the subject longitudinal IDs. By default timepoints
        are "1", "2"...
    """
    print_title("Launch FreeSurfer reconall longitudinal...")
    fsdirs = listify(fsdirs)
    timepoints = listify(timepoints)
    template_id, long_sids = brainprep.recon_all_longitudinal(
        fsdirs, sid, outdir, timepoints)
    print_result(template_id)
    print_result(long_sids)


def brainprep_fsreconall_summary(fsdir, outdir):
    """ Generate text/ascii tables of freesurfer parcellation stats data
    '?h.aparc.stats' for both templates (Desikan & Destrieux) and
    'aseg.stats'.

    Parameters
    ----------
    fsdir: str
        the FreeSurfer working directory with all the subjects.
    outdir: str
        the destination folder.
    """
    print_title("Launch FreeSurfer reconall summary...")
    brainprep.stats2table(fsdir, outdir)

    print_title("Make datasets...")
    regex = os.path.join(outdir, "{0}_stats_{1}_{2}.csv")
    for template in ("aparc", "aparc2009s"):
        data, labels = [], []
        subjects, columns = None, None
        for hemi in ("lh", "rh"):
            for meas in ("area", "volume", "thickness", "thicknessstd",
                         "meancurv", "gauscurv", "foldind", "curvind"):
                table_file = regex.format(template, hemi, meas)
                if not os.path.isfile(table_file):
                    warnings.warn(
                        "Table file not found: {}".format(table_file),
                        UserWarning)
                    continue
                df = pd.read_csv(table_file, sep=",")
                todrop = []
                for name in (
                        "MeanThickness", "WhiteSurfArea", "BrainSegVolNotVent",
                        "eTIV"):
                    if name in df:
                        todrop.append(name)
                df.drop(columns=todrop, inplace=True)
                values = df.values
                if subjects is None:
                    subjects = values[:, 0]
                else:
                    assert (subjects == values[:, 0]).all(), (
                        "Inconsistent subjects list.")
                if columns is None:
                    columns = df.columns[1:]
                else:
                    assert all(columns == df.columns[1:]), (
                        "Inconsistent regions list.")
                values = values[:, 1:]
                values = np.expand_dims(values, axis=1)
                key = "hemi-{}_measure-{}".format(hemi, meas)
                print("- {}: {}".format(key, values.shape))
                data.append(values)
                labels.append(key)
        data = np.concatenate(data, axis=1)
        print("- data:", data.shape)
        destfile = os.path.join(outdir, "channels-{}.txt".format(template))
        np.savetxt(destfile, labels, fmt="%s")
        print_result(destfile)
        destfile = os.path.join(outdir, "subjects-{}.txt".format(template))
        np.savetxt(destfile, subjects, fmt="%s")
        print_result(destfile)
        destfile = os.path.join(outdir, "rois-{}.txt".format(template))
        np.savetxt(destfile, columns, fmt="%s")
        print_result(destfile)
        destfile = os.path.join(outdir, "roi-{}.npy".format(template))
        np.save(destfile, data)
        print_result(destfile)


def brainprep_fsreconall_qc(fs_regex, outdir, euler_thr=-217):
    """ Define the FreeSurfer recon-all quality control workflow.

    Parameters
    ----------
    fs_regex: str
        regex to the FreeSurfer recon-all directories for all subjects.
    outdir: str
        the destination folder.
    euler_thr: int, default -217
        control the quality control threshold on the Euler number score.
    """
    print_title("Parse data...")
    if not os.path.isdir(outdir):
        raise ValueError("Please specify a valid output directory.")
    fs_dirs = sorted(glob.glob(fs_regex))
    print("  FreeSurfer directories:", len(fs_dirs))

    print_title("Parse quality control scores...")
    df_scores = parse_fsreconall_stats(fs_dirs)

    print_title("Save quality control scores...")
    df_qc = df_scores
    df_qc["qc"] = (df_qc["euler"] > euler_thr).astype(int)
    qc_path = os.path.join(outdir, "qc.tsv")
    df_qc.sort_values(by=["euler"], inplace=True)
    df_qc.to_csv(qc_path, index=False, sep="\t")
    print(df_qc)
    print_result(qc_path)

    print_title("Save scores histograms...")
    data = {"euler": {"data": df_qc["euler"].values, "bar": euler_thr}}
    snap = plot_hists(data, outdir)
    print_result(snap)

    print_title("Save brain images ordered by Euler number...")
    sorted_indices = df_qc.index.values.tolist()
    snaps, snapdir = plot_fsreconall(
        np.asarray(fs_dirs)[sorted_indices], outdir)
    df_report = df_qc.copy()
    df_report["snap_path"] = snaps
    df_report["snap_path"] = df_report["snap_path"].apply(
        create_clickable)
    print_result(snapdir)

    print_title("Save quality check ordered by Euler number...")
    report_path = os.path.join(outdir, "qc.html")
    html_report = df_report.to_html(index=False, table_id="table-brainprep")
    html_report = unescape(html_report)
    with open(report_path, "wt") as of:
        of.write(html_report)
    print_result(report_path)
