#!/usr/bin/env python

import os
import sys
import subprocess

my_path = os.path.abspath(os.path.dirname(__file__))
my_path2 = "/".join(my_path.split("/")[0:-1])
sys.path.insert(0, my_path2)
sys.path.insert(0, my_path)

def apply_gbm(tmp_in):
    ''' this function calls NeoAg tool. this tool applys a gradient boosting machine based on biochemical features to epitopes (predicted seqs)
    '''
    model_path = "/".join([my_path, "neoag-master"])
    tool_path = "/".join([my_path, "neoag-master/NeoAg_immunogenicity_predicition_GBM.R"])
    print >> sys.stderr, model_path
    print >> sys.stderr, tmp_in
    #print >> sys.stderr, tmp_out_name
    cmd = "/code/R/3.6.0/bin/Rscript " + tool_path + " "+ model_path + " " + tmp_in
    p = subprocess.Popen(cmd.split(" "),stderr=subprocess.PIPE,stdout=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    print >> sys.stderr, stderrdata
    return(stdoutdata)



def prepare_tmp_for_neoag(props, tmp_file_name):
    ''' writes necessary epitope information into temporary file for neoag tool; only for epitopes with affinity < 500 nM
    '''
    header = ["Sample_ID", "mut_peptide", "Reference", "peptide_variant_position"]
    if "patient.id" in props:
        sample_id = props["patient.id"]
    else:
        sample_id = props["patient"]
    #mut_peptide = props["MHC_I_epitope_.best_prediction."]
    #ref_peptide = props["MHC_I_epitope_.WT."]
    #peptide_variant_position = props["pos_MUT_MHCI"]
    mut_peptide = props["best_affinity_epitope_netmhcpan4"]
    score_mut = props["best_affinity_netmhcpan4"]
    ref_peptide = props["best_affinity_epitope_netmhcpan4_WT"]
    peptide_variant_position = props["pos_MUT_MHCI_affinity_epi"]
    try:
        if float(score_mut) < 500:
            epi_row = "\t".join([sample_id, mut_peptide, ref_peptide, peptide_variant_position])
            #print >> sys.stderr, "NEOAG: " + epi_row
        else:
            epi_row = "\t".join(["NA", "NA", "NA", "NA"])
    except ValueError:
        epi_row = "\t".join(["NA", "NA", "NA", "NA"])
    with open(tmp_file_name, "w") as f:
        print >> sys.stderr, "NEOAG: " + epi_row
        f.write("\t".join(header) + "\n")
        f.write(epi_row + "\n")


def wrapper_neoag(props):
    ''' wrapper function to determine neoag immunogenicity score for a mutated peptide sequence
    '''
    tmp_file = tempfile.NamedTemporaryFile(prefix ="tmp_neoag_", suffix = ".txt", delete = False)
    tmp_file_name = tmp_file.name
    prepare_tmp_for_neoag(props, tmp_file_name)
    neoag_score = apply_gbm(tmp_file_name)
    with open(tmp_file_name) as f:
        for line in f:
            print >> sys.stderr, "NEOAG: "+ line
    print >> sys.stderr, "NEOAG: " + str(neoag_score)
    return neoag_score





if __name__ == '__main__':


    #test_tcga = "/".join([my_path, "neoag-master", "TCGA_neoAg_example.txt"])
    #apply_gbm(test_tcga)

    from input import predict_all_epitopes, epitope
    from input.helpers import data_import
    from input.self_similarity import self_similarity
    from input.netmhcpan4 import netmhcpan_prediction
    import tempfile

    # test with ott data set
    #file = "/projects/CM01_iVAC/immunogenicity_prediction/3rd_party_solutions/MHC_prediction_netmhcpan4/testdat_ott.txt"
    #hla_file ="/projects/SUMMIT/WP1.2/Literature_Cohorts/data_analysis/cohorts/ott/icam_ott/alleles.csv"
    file = "/projects/SUMMIT/WP1.2/immunogenicity_data/ivac/input_annotation/20190328_IS_IM_withoutfeatures.txt"
    hla_file ="/projects/SUMMIT/WP1.2/immunogenicity_data/ivac/hlahd/20190916_alleles_extended.csv"
    # test inest data set
    #file = "/flash/projects/WP3/AnFranziska/AnFranziska/head_seqs.txt"
    #hla_file = "/flash/projects/WP3/AnFranziska/AnFranziska/alleles.csv"
    dat = data_import.import_dat_icam(file, False)
    if "+-13_AA_(SNV)_/_-15_AA_to_STOP_(INDEL)" in dat[0]:
        dat = data_import.change_col_names(dat)
    # available MHC alleles
    set_available_mhc = predict_all_epitopes.Bunchepitopes().add_available_hla_alleles()
    # hla allele of patients
    patient_hlaI = predict_all_epitopes.Bunchepitopes().add_patient_hla_I_allels(hla_file)
    patient_hlaII = predict_all_epitopes.Bunchepitopes().add_patient_hla_II_allels(hla_file)

    print patient_hlaI
    print patient_hlaII

    for ii,i in enumerate(dat[1]):
        if ii < 2:
            print ii
            dict_epi = epitope.Epitope()
            dict_epi.init_properties(dat[0], dat[1][ii])
            dict_epi.add_features(self_similarity.position_of_mutation_epitope(dict_epi.properties, "mhcI"), "pos_MUT_MHCI")
            np = netmhcpan_prediction.NetmhcpanBestPrediction()
            xmer_mut = dict_epi.properties["X..13_AA_.SNV._._.15_AA_to_STOP_.INDEL."]
            tmp_fasta_file = tempfile.NamedTemporaryFile(prefix ="tmp_singleseq_", suffix = ".fasta", delete = False)
            tmp_fasta = tmp_fasta_file.name
            print >> sys.stderr, tmp_fasta
            tmp_prediction_file = tempfile.NamedTemporaryFile(prefix ="netmhcpanpred_", suffix = ".csv", delete = False)
            tmp_prediction = tmp_prediction_file.name
            print >> sys.stderr, tmp_prediction
            np.generate_fasta(dict_epi.properties, tmp_fasta, mut = True)
            alleles = np.get_hla_allels(dict_epi.properties, patient_hlaI)
            #print alleles
            np.mhc_prediction(alleles, set_available_mhc, tmp_fasta, tmp_prediction)
            dict_epi.properties["Position_Xmer_Seq"] = np.mut_position_xmer_seq(dict_epi.properties)
            preds = np.filter_binding_predictions(dict_epi.properties, tmp_prediction)
            best_epi_affinity =  np.minimal_binding_score(preds, rank = False)
            dict_epi.add_features(np.add_best_epitope_info(best_epi_affinity, "Aff(nM)"), "best_affinity_netmhcpan4")
            dict_epi.add_features(np.add_best_epitope_info(best_epi_affinity, "Icore"), "best_affinity_epitope_netmhcpan4 ")
            dict_epi.add_features(np.add_best_epitope_info(best_epi_affinity, "HLA"), "best4_affinity_allele")
            xmer_wt = dict_epi.properties["X.WT._..13_AA_.SNV._._.15_AA_to_STOP_.INDEL."]
            #print >> sys.stderr, "WT seq: " + xmer_wt
            tmp_fasta_file = tempfile.NamedTemporaryFile(prefix ="tmp_singleseq_", suffix = ".fasta", delete = False)
            tmp_fasta = tmp_fasta_file.name
            tmp_prediction_file = tempfile.NamedTemporaryFile(prefix ="netmhcpanpred_", suffix = ".csv", delete = False)
            tmp_prediction = tmp_prediction_file.name
            print >> sys.stderr, tmp_prediction
            np = netmhcpan_prediction.NetmhcpanBestPrediction()
            np.generate_fasta(dict_epi.properties, tmp_fasta, mut = False)
            np.mhc_prediction(alleles, set_available_mhc, tmp_fasta, tmp_prediction)
            preds = np.filter_binding_predictions(dict_epi.properties, tmp_prediction)
            best_epi_affinity = np.filter_for_WT_epitope(preds, dict_epi.properties["best_affinity_epitope_netmhcpan4"],  dict_epi.properties["best4_affinity_allele"])
            dict_epi.add_features(np.add_best_epitope_info(best_epi_affinity, "Aff(nM)"), "best_affinity_netmhcpan4_WT" )
            dict_epi.add_features(np.add_best_epitope_info(best_epi_affinity, "Icore"), "best_affinity_epitope_netmhcpan4_WT")
            dict_epi.add_features(self_similarity.position_of_mutation_epitope_affinity(dict_epi.properties), "pos_MUT_MHCI_affinity_epi")

            sc = wrapper_neoag(dict_epi.properties)
            print >> sys.stderr, sc
            print >> sys.stderr, type(sc)