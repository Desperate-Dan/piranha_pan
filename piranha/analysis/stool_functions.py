#!/usr/bin/env python3
import os
import collections
from Bio import SeqIO
import csv

from piranha.utils.config import *

def gather_fasta_files(summary_info, barcodes_csv, input_cns_list,all_metdata, output_file,publish_dir):
    if not os.path.exists(publish_dir):
        os.mkdir(publish_dir)
    
    analysis_info = collections.defaultdict(list)
    with open(summary_info, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            analysis_info[row[KEY_BARCODE]].append(row)

    input_metadata = {}
    handle_dict = {}
    with open(barcodes_csv,"r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            barcode = row[KEY_BARCODE]
            input_metadata[barcode] = row
            
            if barcode not in handle_dict:
                if not os.path.exists(os.path.join(publish_dir, f"{barcode}")):
                    os.mkdir(os.path.join(publish_dir, f"{barcode}"))
                handle_dict[barcode] = open(os.path.join(publish_dir, f"{barcode}",f"{barcode}.consensus.fasta"),"w")

    with open(output_file,"w") as fw:
        for cns_file in input_cns_list:
            for record in SeqIO.parse(cns_file, KEY_FASTA):
                cns_info= record.description.split(" ")
                ref,barcode,var_count,var_string=cns_info[0].split("|")
                
                info = []
                for row in analysis_info[barcode]:
                    if row[KEY_REFERENCE] == ref:
                        info = row
                metadata = input_metadata[barcode]
                record_id = f"{metadata[KEY_SAMPLE]}|{barcode}|{info[KEY_REFERENCE_GROUP]}|{ref}|{var_count}|{var_string}"
                if all_metdata:
                    for col in metadata:
                        if col != KEY_SAMPLE and col != KEY_BARCODE:
                            record_id += f"|{col}={metadata[col]}"
                else:
                    if KEY_DATE in metadata:
                        record_id += f"|{KEY_DATE}={metadata[KEY_DATE]}"
                    
                    if KEY_EPID in metadata:
                        record_id += f"|{KEY_EPID}={metadata[KEY_EPID]}"
                fw.write(f">{record_id}\n{record.seq}\n")
                handle_dict[barcode].write(f">{record_id}\n{record.seq}\n")
    
    for handle in handle_dict:
        handle_dict[handle].close()

def get_sample(barcodes_csv,barcode):
    sample = ""
    with open(barcodes_csv,"r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row[KEY_BARCODE] == barcode:
                    sample = row[KEY_SAMPLE]
    return sample