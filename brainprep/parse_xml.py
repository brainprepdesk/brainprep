import glob
import xml.etree.ElementTree as ET

import pandas as pd

from brainprep.utils.utils import parse_bids_keys



def parse_cat12_report_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    subjectmeasures = root.find('subjectmeasures')

    # get tiv
    tiv = float(subjectmeasures.find("vol_TIV").text)
    # get tissue volumes
    tissue_volumes = subjectmeasures.find("vol_abs_CGW").text
    tissue_volumes = tissue_volumes.strip('[]').split(' ')[:3]

    # group all the volumes in a dataframe
    volumes = {'tiv': [tiv],
               'CSF_Vol': [float(tissue_volumes[0])],
               'GM_Vol': [float(tissue_volumes[1])],
               'WM_Vol': [float(tissue_volumes[2])]}
    sub_vols = pd.DataFrame(volumes)

    # add the bids keys
    bids_keys = parse_bids_keys(xml_file)
    bids_keys_df = pd.DataFrame(
        {'participant_id': [bids_keys['sub']],
         'session': [bids_keys['ses']],
         'run': [bids_keys['run']],}
    )
    sub_vols = pd.concat([bids_keys_df, sub_vols], axis=1)

    return sub_vols


def flatten_sub_roi(sub_roi):
    # define the columns names
    flatten_region_names = []
    for brain_tissue in sub_roi.index.values:
        tissue_name = brain_tissue[1:].upper()
        flatten_region_names.extend([col+f'_{tissue_name}_Vol' for col in sub_roi.columns])
    # flatten the data
    data = sub_roi.values.flatten()
    # create a new flattened dataframe
    new_sub_roi = pd.DataFrame(data.reshape(1,data.shape[0]), columns=flatten_region_names)
    return new_sub_roi


def parse_cat12_label_xml(xml_file, atlas_name='neuromorphometrics'):

    tree = ET.parse(xml_file)
    root = tree.getroot()
    atlas = root.find(atlas_name)

    # get the region names
    names = [item.text for item in atlas.find("names").findall("item")]

    # get actual data
    sub_roi = {}
    data = atlas.find("data")
    for brain_region in data:
        tissue_data = [float(x) for x in brain_region.text.strip("[]").split(';')]
        sub_roi[brain_region.tag] = tissue_data
    # convert to dataframe with only one row
    sub_roi_df = pd.DataFrame(sub_roi, index=names)
    sub_roi_df = sub_roi_df.transpose()
    sub_roi_df = flatten_sub_roi(sub_roi_df)

    # add the bids keys
    bids_keys = parse_bids_keys(xml_file)
    bids_keys_df = pd.DataFrame(
        {'participant_id': [bids_keys['sub']],
         'session': [bids_keys['ses']],
         'run': [bids_keys['run']],}
    )
    sub_roi_df = pd.concat([bids_keys_df, sub_roi_df], axis=1)

    return sub_roi_df


def parse_cat12_roi_dataset(report_xml_files: list, label_xml_files: list,
                            atlas_name="neuromorphometrics"):

    # parse all the xml
    report_df = pd.DataFrame()
    for report_file in report_xml_files:
        df = parse_cat12_report_xml(report_file)
        report_df = pd.concat([report_df, df], axis=0, ignore_index=True)
    label_df = pd.DataFrame()
    for label_file in label_xml_files:
        df = parse_cat12_label_xml(label_file, atlas_name=atlas_name)
        label_df = pd.concat([label_df, df], axis=0, ignore_index=True)
    
    # merge the dataframes
    bids_cols = ['participant_id', 'session', 'run']
    roi_df = pd.merge(report_df, label_df, how='outer',
                      on=bids_cols)
    roi_df = roi_df.sort_values(by=bids_cols)

    return roi_df
