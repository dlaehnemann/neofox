# **INPuT - Immunogenictiy Neoantigen Prediction Toolbox**


Annotation of mutated peptide sequences (mps) with published or novel potential neo-epitope descriptors

**Published Descriptors:**  
- IEDB immunogenicity *(Calis et al, 2013, PLoS Comput Biol.)*  
- Self-similarity, Conserved vs. Improved Binding  *(Bjerregaard et al, 2017, Front Immunol.)*  
- Priority Score *(Bjerregaard et al, 2017, Cancer Immunol Immunother.)*  
- DAI *(Duan et al., 2014, JEM; Ghorani et al., 2018, Ann Oncol.)*  
- Neoantigen Fitness *(Luksza et al., 2017, Nature; Balachandran et al, 2017, Nature)*  
- Residue-centric presentation score (best_rank) & Patient harmonic Best Rank (PHBR-I/II) *(Marty et al, 2017, Cell; Marty et al, 2018, Cell)*  
- Classically vs Alternatively Defined Neopitopes & Generator Rate *(Rech et al., 2018, Cancer Immunology Research)*  
- Tcell_predictor *(Besser et al, 2019, Journal for ImmunoTherapy of Cancer)*  


**Novel Potential Descriptors:**  
- Amnino Acid Index  
- Differential Expression  
- Amino acid Frequency  
- Conservation Scores (e.g PROVEAN: Choi et al, 2012, PLoS One)  
- Multiplexed Representation  


## **Requirements**

**Specific Input:**  
- icam_output.txt --> icam output file; either patient-specific, or several patients combineds
- allele.csv --> ";" separated file with mhc I and mhc II alleles for all patients of a cohort  


**Required Columns of iCaM Table:**  
- MHC_I_epitope_.best_prediction.  
- 	MHC_I_epitope_.WT.  
-   MHC_II_epitope_.best_prediction.  
- 	MHC_II_epitope_.WT.  
- 	MHC_I_score_.best_prediction.  
- 	MHC_I_score_.WT.  
- 	MHC_II_score_.best_prediction.  
- 	MHC_II_score_.WT.  
- 	MHC_I_peptide_length_.best_prediction.
- 	MHC_I_allele_.best_prediction.  
- 	MHC_II_allele_.best_prediction.  
- 	transcript_expression  
- 	VAF_in_RNA  
- 	VAF_in_tumor  
- 	X..13_AA_.SNV._._.15_AA_to_STOP_.INDEL.  

**Required Additional Files:**  
- RNA reference *(/projects/CM27_IND_patients/GTEX_normal_tissue_data/Skin .csv, predict_all_epitopes.py)*  
- protein database *(/projects/data/human/2018_uniprot_with_isoforms/uniprot_human_with_isoforms.fasta, predict_all_epitopes.py)*  
- amino acid frequencies *(./new_features/20181108_AA_freq_prot.csv, predict_all_epitopes.py)*  
- 4mer amino acid frequnecies *(./new_features/20181108_4mer_freq.csv, predict_all_epitopes.py)*  
- PROVEAN score matrix *(./new_features/PROV_scores_mapped3.csv, predict_all_epitopes.py)*  
- available HLA I alleles for netmhcpan4 *(./netmhcpan4/MHC_available.csv, predict_all_epitopes.py)*  
- available HLA II alleles for netmhcIIpan3.2 *(./netmhcIIpan/avail_mhcII.txt, predict_all_epitopes.py)*  
- aaindex1 *("aa_index/aaindex1", predict_all_epitopes.py)*  
- aanindex2 *("aa_index/aaindex1", predict_all_epitopes.py)*  

**Required Software/Tools:**  
- python2 *(anaconda/2/2018)*
- BLAST *(/code/ncbi-blast/2.8.1+/bin/blastp, neoantigen_fitness.py)*  
- netmhcpan *(/code/netMHCpan-4.0/netMHCpan, netmhcpan_prediction.py)*  
- netmhcIIpan *(/code/net/MHCIIpan/3.2/netMHCIIpan, netmhcIIpan_prediction.py)*  
- Tcell_predictor: python3 + scripts/pickle/mat files of Tcell_predictor tool *(/code/Anaconda/3/2018/bin/python + tool under ./Tcell_predictor, tcellpredictor_wrapper.py )*  

## **Usage**  

**Singel iCaM File**  
```
python predict_all_epitopes.py --icam_file testseq_head.txt  -allele_file alleles.csv [-tissue skin --frameshift False]> test07.txt
```  

--> annotation of one iCaM file

**Singel iCaM File**  
```
sh start_annotation_multiple_patientfiles.sh cohort_folder_with_patient_icam_folders output_folder allele_table cohort_name
```  

--> parallel mps annotation of patients of a cohort, iCaM files stored in cohort_folder_with_patient_icam_folders
