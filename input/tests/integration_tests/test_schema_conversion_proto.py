from unittest import TestCase

from input.model.schema_conversion import SchemaConverter
from input.model.neoantigen import Neoantigen, Gene, Mutation, Patient


class SchemaConverterTest(TestCase):

    def test_icam2model(self):
        # self.icam_file = '/projects/SUMMIT/WP1.2/input/development/Pt29.sequences4testing.txt'
        self.icam_file = '\\\\192.168.171.199\\projects$\\SUMMIT\\WP1.2\\input\\development\\Pt29.sequences4testing.txt'
        with open(self.icam_file) as f:
            self.count_lines = len(f.readlines())
        neoantigens = SchemaConverter().icam2model(self.icam_file)
        self.assertIsNotNone(neoantigens)
        self.assertEqual(self.count_lines - 1, len(neoantigens))
        for n in neoantigens:
            self.assertIsInstance(n, Neoantigen)
            self.assertIsInstance(n.gene, Gene)
            self.assertIsInstance(n.mutation, Mutation)
            self.assertTrue(n.gene.transcript_identifier is not None and len(n.gene.transcript_identifier) > 0)
            self.assertTrue(n.mutation.mutated_aminoacid is not None and len(n.mutation.mutated_aminoacid) == 1)

    def test_overriding_patient_id(self):
        # self.icam_file = '/projects/SUMMIT/WP1.2/input/development/Pt29.sequences4testing.txt'
        self.icam_file = '\\\\192.168.171.199\\projects$\\SUMMIT\\WP1.2\\input\\development\\Pt29.sequences4testing.txt'
        with open(self.icam_file) as f:
            self.count_lines = len(f.readlines())
        neoantigens = SchemaConverter().icam2model(self.icam_file, patient_id='patientX')
        for n in neoantigens:
            self.assertEqual(n.patient_identifier, 'patientX')
        neoantigens = SchemaConverter().icam2model(self.icam_file)
        for n in neoantigens:
            self.assertEqual(n.patient_identifier, None)

    def test_patient_metadata2model(self):
        # alleles_file = '/projects/SUMMIT/WP1.2/Literature_Cohorts/data_analysis/cohorts/vanallen/output_tables/20200106_alleles_extended.csv'
        # tumor_content_file = '/projects/SUMMIT/WP1.2/Literature_Cohorts/data_analysis/cohorts/vanallen/output_tables/vanallen_patient_overview.csv'
        alleles_file = "\\\\192.168.171.199\\projects$\\SUMMIT\\WP1.2\\Literature_Cohorts\\data_analysis\\cohorts\\vanallen\\output_tables\\20200106_alleles_extended.csv"
        tumor_content_file = '\\\\192.168.171.199\\projects$\\SUMMIT\\WP1.2\\Literature_Cohorts\\data_analysis\\cohorts\\vanallen\\output_tables\\vanallen_patient_overview.csv'
        with open(alleles_file) as f:
            count_lines = len(f.readlines())
        patients = SchemaConverter().patient_metadata2model(hla_file=alleles_file, tumor_content_file=tumor_content_file)
        self.assertIsNotNone(patients)
        self.assertIsInstance(patients, list)
        self.assertEqual(count_lines / 2, len(patients))
        for n in patients:
            self.assertIsInstance(n, Patient)
            self.assertIsInstance(n.is_rna_available, bool)
            self.assertIsInstance(n.estimated_tumor_content, float)
            self.assertIsInstance(n.mhc_i_alleles, list)
            self.assertIsInstance(n.mhc_i_i_alleles, list)