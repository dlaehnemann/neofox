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
import os
from logzero import logger
from unittest import TestCase
from neofox.model.conversion import ModelConverter
import neofox.tests.integration_tests.integration_test_tools as integration_test_tools
from neofox.helpers import intermediate_files
from neofox.helpers.runner import Runner
from neofox.MHC_predictors.netmhcpan.combine_netmhcpan_pred_multiple_binders import BestAndMultipleBinder
from neofox.MHC_predictors.netmhcpan.netmhcpan_prediction import NetMhcPanPredictor
from neofox.MHC_predictors.netmhcpan.multiple_binders import MultipleBinding
from neofox.MHC_predictors.netmhcpan.combine_netmhcIIpan_pred_multiple_binders import BestAndMultipleBinderMhcII
from neofox.MHC_predictors.netmhcpan.netmhcIIpan_prediction import NetMhcIIPanPredictor
from neofox.tests import TEST_MHC_ONE, TEST_MHC_TWO


class TestBestMultipleBinder(TestCase):

    def setUp(self):
        references, self.configuration = integration_test_tools.load_references()
        self.runner = Runner()
        self.available_alleles_mhc1 = references.get_available_alleles().get_available_mhc_i()
        self.available_alleles_mhc2 = references.get_available_alleles().get_available_mhc_ii()



    def test_best_multiple_run(self):
        best_multiple = BestAndMultipleBinder(runner=self.runner, configuration=self.configuration)
        # this is some valid example neoantigen candidate sequence
        mutated = 'DEVLGEPSQDILVTDQTRLEATISPET'
        non_mutated = 'DEVLGEPSQDILVIDQTRLEATISPET'
        best_multiple.run(sequence_mut=mutated, sequence_wt=non_mutated, mhc1_alleles_patient=TEST_MHC_ONE,
                          mhc1_alleles_available=self.available_alleles_mhc1)
        self.assertEqual(543.9, best_multiple.best4_affinity)
        self.assertEqual(0.4304, best_multiple.best4_mhc_score)
        self.assertEqual("VTDQTRLEA", best_multiple.best4_mhc_epitope)
        logger.info(best_multiple.best4_mhc_epitope)
        logger.info(best_multiple.phbr_i)

    def test_phbr1(self):
        tmp_prediction = intermediate_files.create_temp_file(prefix="netmhcpanpred_", suffix=".csv")
        best_multiple = BestAndMultipleBinder(runner=self.runner, configuration=self.configuration)
        netmhcpan = NetMhcPanPredictor(runner=self.runner, configuration=self.configuration)
        mutated = 'DEVLGEPSQDILVTDQTRLEATISPET'
        non_mutated = 'DEVLGEPSQDILVIDQTRLEATISPET'
        # all alleles = heterozygous
        tmp_fasta = intermediate_files.create_temp_fasta(sequences=[mutated], prefix="tmp_singleseq_")
        netmhcpan.mhc_prediction(TEST_MHC_ONE, self.available_alleles_mhc1, tmp_fasta, tmp_prediction)
        position_of_mutation = netmhcpan.mut_position_xmer_seq(sequence_mut=mutated, sequence_wt=non_mutated)
        predicted_neoepitopes = netmhcpan.filter_binding_predictions(position_of_mutation=position_of_mutation,
                                                                     tmppred=tmp_prediction)
        predicted_neoepitopes_transformed = MultipleBinding.transform_mhc_prediction_output(predicted_neoepitopes)
        best_epitopes_per_allele = MultipleBinding.extract_best_epitope_per_alelle(
            predicted_neoepitopes_transformed, TEST_MHC_ONE)
        best_epitopes_per_allele = [epitope[0] for epitope in best_epitopes_per_allele]
        phbr_i = best_multiple.calculate_phbr_i(best_epitopes_per_allele)
        self.assertIsNotNone(phbr_i)
        self.assertAlmostEqual(1.9449989270, phbr_i)
        # one homozygous allele present
        mhc_alleles = ModelConverter.parse_mhc1_alleles(['HLA-A*24:02', 'HLA-A*02:01', 'HLA-B*15:01', 'HLA-B*44:02',
                                                         'HLA-C*05:01', 'HLA-C*05:01'])
        tmp_fasta = intermediate_files.create_temp_fasta(sequences=[mutated], prefix="tmp_singleseq_")
        netmhcpan.mhc_prediction(TEST_MHC_ONE, self.available_alleles_mhc1, tmp_fasta, tmp_prediction)
        position_of_mutation = netmhcpan.mut_position_xmer_seq(sequence_mut=mutated, sequence_wt=non_mutated)
        predicted_neoepitopes = netmhcpan.filter_binding_predictions(position_of_mutation=position_of_mutation,
                                                                     tmppred=tmp_prediction)
        predicted_neoepitopes_transformed = MultipleBinding.transform_mhc_prediction_output(predicted_neoepitopes)
        best_epitopes_per_allele = MultipleBinding.extract_best_epitope_per_alelle(
            predicted_neoepitopes_transformed, mhc_alleles)
        best_epitopes_per_allele = [epitope[0] for epitope in best_epitopes_per_allele]

        phbr_i = best_multiple.calculate_phbr_i(best_epitopes_per_allele)
        self.assertIsNotNone(phbr_i)
        self.assertAlmostEqual(1.131227969630, phbr_i)
        # mo info for one allele
        mhc_alleles = ModelConverter.parse_mhc1_alleles(['HLA-A*24:02', 'HLA-A*02:01', 'HLA-B*15:01', 'HLA-B*44:02',
                                                         'HLA-C*05:01'])
        tmp_fasta = intermediate_files.create_temp_fasta(sequences=[mutated], prefix="tmp_singleseq_")
        netmhcpan.mhc_prediction(TEST_MHC_ONE, self.available_alleles_mhc1, tmp_fasta, tmp_prediction)
        position_of_mutation = netmhcpan.mut_position_xmer_seq(sequence_mut=mutated, sequence_wt=non_mutated)
        predicted_neoepitopes = netmhcpan.filter_binding_predictions(position_of_mutation=position_of_mutation,
                                                                     tmppred=tmp_prediction)
        predicted_neoepitopes_transformed = MultipleBinding.transform_mhc_prediction_output(predicted_neoepitopes)
        best_epitopes_per_allele = MultipleBinding.extract_best_epitope_per_alelle(
            predicted_neoepitopes_transformed, mhc_alleles)
        best_epitopes_per_allele = [epitope[0] for epitope in best_epitopes_per_allele]
        phbr_i = best_multiple.calculate_phbr_i(best_epitopes_per_allele)
        self.assertIsNone(phbr_i)

    def test_best_multiple_mhc2_run(self):
        best_multiple = BestAndMultipleBinderMhcII(runner=self.runner, configuration=self.configuration)
        # this is some valid example neoantigen candidate sequence
        mutated = 'DEVLGEPSQDILVTDQTRLEATISPET'
        non_mutated = 'DEVLGEPSQDILVIDQTRLEATISPET'
        best_multiple.run(sequence_mut=mutated, sequence_wt=non_mutated, mhc2_alleles_patient=TEST_MHC_TWO,
                          mhc2_alleles_available=self.available_alleles_mhc2)
        logger.info(best_multiple.best_mhcII_pan_score)
        logger.info(best_multiple.best_mhcII_pan_affinity)
        logger.info(best_multiple.best_mhcII_pan_epitope)
        logger.info(best_multiple.phbr_ii)
        self.assertEqual(17.0, best_multiple.best_mhcII_pan_score)
        self.assertEqual(1434.66, best_multiple.best_mhcII_pan_affinity)
        self.assertEqual("VTDQTRLEATISPET", best_multiple.best_mhcII_pan_epitope)

    def test_phbr2(self):
        tmp_prediction = intermediate_files.create_temp_file(prefix="netmhcpanpred_", suffix=".csv")
        best_multiple = BestAndMultipleBinderMhcII(runner=self.runner, configuration=self.configuration)
        netmhc2pan = NetMhcIIPanPredictor(runner=self.runner, configuration=self.configuration)
        mutated = 'DEVLGEPSQDILVTDQTRLEATISPET'
        non_mutated = 'DEVLGEPSQDILVIDQTRLEATISPET'
        # all alleles = heterozygous
        tmp_fasta = intermediate_files.create_temp_fasta(sequences=[mutated], prefix="tmp_singleseq_")
        allele_combinations = netmhc2pan.generate_mhc2_alelle_combinations(TEST_MHC_TWO)
        patient_mhc2_isoforms = best_multiple._get_only_available_combinations(allele_combinations,
                                                                               self.available_alleles_mhc2)
        netmhc2pan.mhcII_prediction(patient_mhc2_isoforms, tmp_fasta, tmp_prediction)
        position_of_mutation = netmhc2pan.mut_position_xmer_seq(sequence_mut=mutated, sequence_wt=non_mutated)
        predicted_neoepitopes = netmhc2pan.filter_binding_predictions(position_of_mutation=position_of_mutation,
                                                                      tmppred=tmp_prediction)
        predicted_neoepitopes_transformed = MultipleBinding.transform_mhc2_prediction_output(predicted_neoepitopes)
        best_predicted_epitopes_per_alelle = MultipleBinding.extract_best_epitope_per_mhc2_alelle(
            predicted_neoepitopes_transformed, TEST_MHC_TWO)
        logger.info(best_predicted_epitopes_per_alelle)
        logger.info(len(best_predicted_epitopes_per_alelle))
        phbr_ii = best_multiple.calculate_phbr_ii(best_predicted_epitopes_per_alelle)
        self.assertIsNotNone(phbr_ii)
        self.assertAlmostEqual(37.09795868, phbr_ii)
        # mo info for one allele
        mhc2_alleles = ModelConverter.parse_mhc2_alleles(['HLA-DRB1*04:02', 'HLA-DRB1*08:01', 'HLA-DQA1*03:01',
                                                          'HLA-DQA1*04:01', 'HLA-DQB1*03:02', 'HLA-DQB1*04:02',
                                                          'HLA-DPA1*01:03', 'HLA-DPA1*02:01', 'HLA-DPB1*13:01',
                                                          'HLA-DPB1*13:01'])
        tmp_fasta = intermediate_files.create_temp_fasta(sequences=[mutated], prefix="tmp_singleseq_")
        allele_combinations = netmhc2pan.generate_mhc2_alelle_combinations(mhc2_alleles)
        patient_mhc2_isoforms = best_multiple._get_only_available_combinations(allele_combinations,
                                                                               self.available_alleles_mhc2)
        netmhc2pan.mhcII_prediction(patient_mhc2_isoforms, tmp_fasta, tmp_prediction)
        position_of_mutation = netmhc2pan.mut_position_xmer_seq(sequence_mut=mutated, sequence_wt=non_mutated)
        predicted_neoepitopes = netmhc2pan.filter_binding_predictions(position_of_mutation=position_of_mutation,
                                                                      tmppred=tmp_prediction)
        predicted_neoepitopes_transformed = MultipleBinding.transform_mhc2_prediction_output(predicted_neoepitopes)
        best_predicted_epitopes_per_alelle = MultipleBinding.extract_best_epitope_per_mhc2_alelle(
            predicted_neoepitopes_transformed, mhc2_alleles)
        logger.info(best_predicted_epitopes_per_alelle)
        logger.info(len(best_predicted_epitopes_per_alelle))
        phbr_ii = best_multiple.calculate_phbr_ii(best_predicted_epitopes_per_alelle)
        self.assertIsNotNone(phbr_ii)
        self.assertAlmostEqual(37.7107933753, phbr_ii)
        # one allele present
        mhc2_alleles = ModelConverter.parse_mhc2_alleles(['HLA-DRB1*04:02', 'HLA-DRB1*08:01', 'HLA-DQA1*03:01',
                                                          'HLA-DQA1*04:01', 'HLA-DQB1*03:02', 'HLA-DQB1*04:02',
                                                          'HLA-DPA1*01:03', 'HLA-DPA1*02:01', 'HLA-DPB1*13:01'])
        tmp_fasta = intermediate_files.create_temp_fasta(sequences=[mutated], prefix="tmp_singleseq_")
        allele_combinations = netmhc2pan.generate_mhc2_alelle_combinations(mhc2_alleles)
        patient_mhc2_isoforms = best_multiple._get_only_available_combinations(allele_combinations,
                                                                               self.available_alleles_mhc2)
        netmhc2pan.mhcII_prediction(patient_mhc2_isoforms, tmp_fasta, tmp_prediction)
        position_of_mutation = netmhc2pan.mut_position_xmer_seq(sequence_mut=mutated, sequence_wt=non_mutated)
        predicted_neoepitopes = netmhc2pan.filter_binding_predictions(position_of_mutation=position_of_mutation,
                                                                      tmppred=tmp_prediction)
        predicted_neoepitopes_transformed = MultipleBinding.transform_mhc2_prediction_output(predicted_neoepitopes)
        best_predicted_epitopes_per_alelle = MultipleBinding.extract_best_epitope_per_mhc2_alelle(
            predicted_neoepitopes_transformed, mhc2_alleles)
        logger.info(best_predicted_epitopes_per_alelle)
        logger.info(len(best_predicted_epitopes_per_alelle))
        phbr_ii = best_multiple.calculate_phbr_ii(best_predicted_epitopes_per_alelle)
        self.assertIsNone(phbr_ii)





