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
from logzero import logger
from unittest import TestCase

from neofox.model.mhc_parser import MhcParser
from neofox.model.neoantigen import Mutation

from neofox.model.conversion import ModelConverter, ModelValidator
import neofox.tests.integration_tests.integration_test_tools as integration_test_tools
from neofox.helpers.runner import Runner
from neofox.MHC_predictors.netmhcpan.combine_netmhcpan_pred_multiple_binders import (
    BestAndMultipleBinder,
)
from neofox.MHC_predictors.netmhcpan.netmhcpan_prediction import NetMhcPanPredictor
from neofox.MHC_predictors.netmhcpan.combine_netmhcIIpan_pred_multiple_binders import (
    BestAndMultipleBinderMhcII,
)
from neofox.MHC_predictors.netmhcpan.netmhcIIpan_prediction import NetMhcIIPanPredictor
from neofox.annotation_resources.uniprot.uniprot import Uniprot


class TestBestMultipleBinder(TestCase):
    def setUp(self):
        references, self.configuration = integration_test_tools.load_references()
        self.runner = Runner()
        self.available_alleles_mhc1 = (
            references.get_available_alleles().get_available_mhc_i()
        )
        self.available_alleles_mhc2 = (
            references.get_available_alleles().get_available_mhc_ii()
        )
        self.hla_database = references.get_hla_database()
        self.proteome_db = references.proteome_db
        self.mhc_parser = MhcParser(self.hla_database)
        self.test_mhc_one = integration_test_tools.get_mhc_one_test(self.hla_database)
        self.test_mhc_two = integration_test_tools.get_mhc_two_test(self.hla_database)
        self.uniprot = Uniprot(references.uniprot_pickle)

    def test_best_multiple_run(self):
        best_multiple = BestAndMultipleBinder(
            runner=self.runner, configuration=self.configuration, mhc_parser=self.mhc_parser
        )
        # this is some valid example neoantigen candidate sequence
        mutation = ModelValidator._validate_mutation(
            Mutation(
                mutated_xmer="VVKWKFMVSTADPGSFTSRPACSSSAAPLGISQPRSSCTLPEPPLWSVPCPSCRKIYTACPSQEKNLKKPVPKSYLIHAGLEPLTFTNMFPSWEHRDDTAEITEMDMEVSNQITLVEDVLAKLCKTIYLLANLL",
                wild_type_xmer=None,
            )
        )
        best_multiple.run(
            mutation=mutation,
            mhc1_alleles_patient=self.test_mhc_one,
            mhc1_alleles_available=self.available_alleles_mhc1,
            uniprot=self.uniprot,
            hla_database=self.hla_database
        )
        self.assertEqual(18.6, best_multiple.best_epitope_by_affinity.affinity_score)
        self.assertEqual('HLA-A*02:01', best_multiple.best_epitope_by_affinity.hla)
        self.assertEqual(0.2137, best_multiple.best_epitope_by_rank.rank)
        self.assertEqual("HLA-B*15:01", best_multiple.best_epitope_by_rank.hla)
        self.assertEqual("FMVSTADPGSF", best_multiple.best_epitope_by_rank.peptide)
        self.assertEqual("YAVNSADPGVF", best_multiple.best_wt_epitope_by_rank.peptide)
        self.assertEqual(
            best_multiple.best_ninemer_epitope_by_rank.hla,
            best_multiple.best_ninemer_wt_epitope_by_rank.hla,
        )
        self.assertEqual(3, best_multiple.generator_rate_adn)
        self.assertEqual(3, best_multiple.generator_rate_cdn)
        self.assertAlmostEqual(0.38589144451278, best_multiple.phbr_i)



    def test_best_multiple_mhc2_run(self):
        best_multiple = BestAndMultipleBinderMhcII(
            runner=self.runner, configuration=self.configuration, mhc_parser=self.mhc_parser
        )
        # this is some valid example neoantigen candidate sequence
        mutation = ModelValidator._validate_mutation(
            Mutation(
                mutated_xmer="VVKWKFMVSTADPGSFTSRPACSSSAAPLGISQPRSSCTLPEPPLWSVPCPSCRKIYTACPSQEKNLKKPVPKSYLIHAGLEPLTFTNMFPSWEHRDDTAEITEMDMEVSNQITLVEDVLAKLCKTIYLLANLL",
                wild_type_xmer=None,
            )
        )
        best_multiple.run(
            mutation=mutation,
            mhc2_alleles_patient=self.test_mhc_two,
            mhc2_alleles_available=self.available_alleles_mhc2,
            uniprot=self.uniprot,
            hla_database=self.hla_database
        )
        logger.info(best_multiple.best_predicted_epitope_rank.rank)
        logger.info(best_multiple.best_predicted_epitope_affinity.affinity_score)
        logger.info(best_multiple.best_predicted_epitope_rank.peptide)
        logger.info(best_multiple.phbr_ii)
        self.assertEqual(1.1, best_multiple.best_predicted_epitope_rank.rank)
        self.assertEqual(
            135.07, best_multiple.best_predicted_epitope_affinity.affinity_score
        )
        self.assertEqual(
            "PVPKSYLIHAGLEPL", best_multiple.best_predicted_epitope_rank.peptide
        )
        self.assertEqual(
            "PAPKSYLIHAGLEPL", best_multiple.best_predicted_epitope_rank_wt.peptide
        )
        self.assertEqual(2.720820665633116, best_multiple.phbr_ii)
        self.assertEqual(
            best_multiple.best_predicted_epitope_rank.hla,
            best_multiple.best_predicted_epitope_rank_wt.hla,
        )

