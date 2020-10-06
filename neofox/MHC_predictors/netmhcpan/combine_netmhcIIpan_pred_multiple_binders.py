#!/usr/bin/env python
#
# Copyright (c) 2020-2030 Translational Oncology at the Medical Center of the Johannes Gutenberg-University Mainz gGmbH.
#
# This file is part of Neofox
# (see https://github.com/tron-bioinformatics/neofox).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.#
from typing import List, Set
import scipy.stats as stats
from logzero import logger
from neofox import MHC_II
from neofox.MHC_predictors.netmhcpan.multiple_binders import MultipleBinding
from neofox.MHC_predictors.netmhcpan.netmhcIIpan_prediction import NetMhcIIPanPredictor
from neofox.helpers import intermediate_files
from neofox.model.neoantigen import Annotation, MhcTwo, MhcTwoGeneName
from neofox.model.wrappers import AnnotationFactory
import neofox.helpers.casting as casting


class BestAndMultipleBinderMhcII:

    def __init__(self, runner, configuration):
        """
        :type runner: neofox.helpers.runner.Runner
        :type configuration: neofox.references.DependenciesConfiguration
        """
        self.runner = runner
        self.configuration = configuration
        self._initialise()

    def _initialise(self):
        self.phbr_ii = None
        self.best_mhcII_pan_score = None
        self.best_mhcII_pan_epitope = "-"
        self.best_mhcII_pan_allele = None
        self.best_mhcII_pan_position = None
        self.best_mhcII_pan_affinity = None
        self.best_mhcII_pan_affinity_epitope = "-"
        self.best_mhcII_pan_affinity_allele = None
        self.best_mhcII_pan_affinity_position = None
        # WT features
        self.best_mhcII_pan_score_WT = None
        self.best_mhcII_pan_epitope_WT = "-"
        self.best_mhcII_pan_allele_WT = None
        self.best_mhcII_affinity_WT = None
        self.best_mhcII_affinity_epitope_WT = "-"
        self.best_mhcII_affinity_allele_WT = None

    def calculate_phbr_ii(self, mhc_ii_alleles_with_best_scores):
        """returns list of multiple binding scores for mhcII considering best epitope per allele,
        applying different types of means (harmonic ==> PHRB-II, Marty et al).
        2 copies of DRA - DRB1 --> consider this gene 2x when averaging mhcii binding scores
        """
        # TODO: what is this method actually doing?
        mhc_ii_alleles_with_best_scores_new = list(mhc_ii_alleles_with_best_scores)
        phbr_ii = None
        for allele_with_score in mhc_ii_alleles_with_best_scores:
            if allele_with_score[-1].gene == MhcTwoGeneName.DRB1.name:
                mhc_ii_alleles_with_best_scores_new.append(allele_with_score)
        if len(mhc_ii_alleles_with_best_scores_new) == 12:
            # 12 genes gene copies should be included into PHBR_II
            best_mhc_ii_scores_per_allele = [epitope[0] for epitope in mhc_ii_alleles_with_best_scores_new]
            phbr_ii = stats.hmean(best_mhc_ii_scores_per_allele)
        return phbr_ii

    def run(self, sequence: str, sequence_reference: str, mhc: List[MhcTwo], available_mhc: Set):
        """predicts MHC epitopes; returns on one hand best binder and on the other hand multiple binder analysis is performed
        """
        # mutation
        self._initialise()
        tmp_prediction = intermediate_files.create_temp_file(prefix="netmhcpanpred_", suffix=".csv")
        netmhc2pan = NetMhcIIPanPredictor(runner=self.runner, configuration=self.configuration)
        tmp_fasta = intermediate_files.create_temp_fasta([sequence], prefix="tmp_singleseq_")
        allele_combinations = netmhc2pan.generate_mhc_ii_alelle_combinations(mhc)
        # TODO: migrate the available alleles into the model for alleles
        patient_mhc_two_molecules = self._get_only_available_combinations(allele_combinations, available_mhc)

        netmhc2pan.mhcII_prediction(patient_mhc_two_molecules, tmp_fasta, tmp_prediction)
        position_mutation = netmhc2pan.mut_position_xmer_seq(sequence_wt=sequence_reference, sequence_mut=sequence)
        if len(sequence) >= 15:
            predicted_epitopes = netmhc2pan.filter_binding_predictions(position_mutation, tmp_prediction)
            # multiple binding
            predicted_epitopes_transformed = MultipleBinding.transform_mhc_two_prediction_output(predicted_epitopes)
            best_predicted_epitopes_per_alelle = MultipleBinding.extract_best_epitope_per_mhc_two_alelle(
                predicted_epitopes_transformed, mhc)
            self.MHCII_score_best_per_alelle = self.calculate_phbr_ii(best_predicted_epitopes_per_alelle)
            # best prediction
            best_predicted_epitope_rank = netmhc2pan.minimal_binding_score(predicted_epitopes)
            self.best_mhcII_pan_score = casting.to_float(netmhc2pan.add_best_epitope_info(best_predicted_epitope_rank, "%Rank"))
            self.best_mhcII_pan_epitope = netmhc2pan.add_best_epitope_info(best_predicted_epitope_rank, "Peptide")
            self.best_mhcII_pan_allele = netmhc2pan.add_best_epitope_info(best_predicted_epitope_rank, "Allele")
            self.best_mhcII_pan_position = netmhc2pan.add_best_epitope_info(best_predicted_epitope_rank, "Seq")
            best_predicted_epitope_affinity = netmhc2pan.minimal_binding_score(predicted_epitopes, rank=False)
            self.best_mhcII_pan_affinity = casting.to_float(netmhc2pan.add_best_epitope_info(best_predicted_epitope_affinity, "Affinity(nM)"))
            self.best_mhcII_pan_affinity_epitope = netmhc2pan.add_best_epitope_info(best_predicted_epitope_affinity, "Peptide")
            self.best_mhcII_pan_affinity_allele = netmhc2pan.add_best_epitope_info(best_predicted_epitope_affinity, "Allele")
            self.best_mhcII_pan_affinity_position = netmhc2pan.add_best_epitope_info(best_predicted_epitope_affinity, "Seq")

        # wt
        tmp_prediction = intermediate_files.create_temp_file(prefix="netmhcpanpred_", suffix=".csv")
        netmhc2pan = NetMhcIIPanPredictor(runner=self.runner, configuration=self.configuration)
        tmp_fasta = intermediate_files.create_temp_fasta([sequence_reference], prefix="tmp_singleseq_")
        netmhc2pan.mhcII_prediction(patient_mhc_two_molecules, tmp_fasta, tmp_prediction)
        if len(sequence_reference) >= 15:
            predicted_epitopes_wt = netmhc2pan.filter_binding_predictions(position_mutation, tmp_prediction)
            # best prediction
            best_predicted_epitope_rank_wt = \
                netmhc2pan.filter_for_wt_epitope_position(predicted_epitopes_wt, self.best_mhcII_pan_epitope,
                                                  position_epitope_in_xmer=self.best_mhcII_pan_position)
            self.best_mhcII_pan_score_WT = casting.to_float(netmhc2pan.add_best_epitope_info(best_predicted_epitope_rank_wt, "%Rank"))
            self.best_mhcII_pan_epitope_WT = netmhc2pan.add_best_epitope_info(best_predicted_epitope_rank_wt, "Peptide")
            self.best_mhcII_pan_allele_WT = netmhc2pan.add_best_epitope_info(best_predicted_epitope_rank_wt, "Allele")
            best_predicted_epitope_affinity_wt = \
                netmhc2pan.filter_for_wt_epitope_position(predicted_epitopes_wt, self.best_mhcII_pan_affinity_epitope,
                                                  position_epitope_in_xmer=self.best_mhcII_pan_affinity_position)
            self.best_mhcII_affinity_WT = casting.to_float(netmhc2pan.add_best_epitope_info(best_predicted_epitope_affinity_wt, "Affinity(nM)"))
            self.best_mhcII_affinity_epitope_WT = netmhc2pan.add_best_epitope_info(best_predicted_epitope_affinity_wt, "Peptide")
            self.best_mhcII_affinity_allele_WT = netmhc2pan.add_best_epitope_info(best_predicted_epitope_affinity_wt, "Allele")

    @staticmethod
    def _get_only_available_combinations(allele_combinations, set_available_mhc):
        patients_available_alleles = list(set(allele_combinations).intersection(set(set_available_mhc)))
        patients_not_available_alleles = list(set(allele_combinations).difference(set(set_available_mhc)))
        if len(patients_not_available_alleles) > 0:
            logger.warning(
                "MHC II alleles {} are not supported by NetMHC2pan and no binding or derived features will "
                "include it".format(",".join(patients_not_available_alleles)))
        return patients_available_alleles

    def get_annotations(self) -> List[Annotation]:
        annotations =  [
            AnnotationFactory.build_annotation(value=self.best_mhcII_pan_score, name="Best_rank_MHCII_score"),
            AnnotationFactory.build_annotation(value=self.best_mhcII_pan_epitope, name="Best_rank_MHCII_score_epitope"),
            AnnotationFactory.build_annotation(value=self.best_mhcII_pan_allele, name="Best_rank_MHCII_score_allele"),
            AnnotationFactory.build_annotation(value=self.best_mhcII_pan_affinity, name="Best_affinity_MHCII_score"),
            AnnotationFactory.build_annotation(value=self.best_mhcII_pan_affinity_epitope,
                                               name="Best_affinity_MHCII_epitope"),
            AnnotationFactory.build_annotation(value=self.best_mhcII_pan_affinity_allele,
                                               name="Best_affinity_MHCII_allele"),
            AnnotationFactory.build_annotation(value=self.best_mhcII_pan_score_WT, name="Best_rank_MHCII_score_WT"),
            AnnotationFactory.build_annotation(value=self.best_mhcII_pan_epitope_WT,
                                               name="Best_rank_MHCII_score_epitope_WT"),
            AnnotationFactory.build_annotation(value=self.best_mhcII_pan_allele_WT,
                                               name="Best_rank_MHCII_score_allele_WT"),
            AnnotationFactory.build_annotation(value=self.best_mhcII_affinity_WT, name="Best_affinity_MHCII_score_WT"),
            AnnotationFactory.build_annotation(value=self.best_mhcII_affinity_epitope_WT,
                                               name="Best_affinity_MHCII_epitope_WT"),
            AnnotationFactory.build_annotation(value=self.best_mhcII_affinity_allele_WT,
                                               name="Best_affinity_MHCII_allele_WT"),
            AnnotationFactory.build_annotation(value=self.phbr_ii,
                                               name="PHBR-II")
            ]
        return annotations
