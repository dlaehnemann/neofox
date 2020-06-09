import random
import struct
from unittest import TestCase

from Bio.Data import IUPACData
import numpy as np

from input.model_protobuf.schema_conversion import SchemaConverter
from input.model_protobuf.neoantigen import Neoantigen, Gene, Mutation


class SchemaConverterTest(TestCase):

    def test_model2json(self):
        neoantigens = [_get_random_neoantigen() for _ in range(5)]
        json_data = [n.to_json() for n in neoantigens]
        self.assertIsInstance(json_data, list)
        self.assertEqual(5, len(json_data))
        neoantigens2 = [Neoantigen().from_json(j) for j in json_data]
        self._assert_lists_equal(neoantigens, neoantigens2)

    def test_model2dict(self):
        neoantigens = [_get_random_neoantigen() for _ in range(5)]
        json_data = [n.to_dict() for n in neoantigens]
        self.assertIsInstance(json_data, list)
        self.assertEqual(5, len(json_data))
        neoantigens2 = [Neoantigen().from_dict(j) for j in json_data]
        self._assert_lists_equal(neoantigens, neoantigens2)

    def test_model2csv(self):
        neoantigens = [_get_random_neoantigen() for _ in range(5)]
        csv_data = SchemaConverter.model2csv(neoantigens)
        self.assertIsNotNone(csv_data)
        self.assertEqual(csv_data.shape[0], len(neoantigens))
        for n in neoantigens:
            self.assertEqual(n.variant_allele_frequency,
                             csv_data[
                                 (csv_data['mutation.position'] == n.mutation.position) &
                                 (csv_data['mutation.mutatedAminoacid'] == n.mutation.mutated_aminoacid)
                             ].variantAlleleFrequency.iloc[0])

    def test_csv2model(self):
        neoantigens = [_get_random_neoantigen() for _ in range(5)]
        csv_data = SchemaConverter.model2csv(neoantigens)
        neoantigens2 = SchemaConverter.csv2model(csv_data)
        self._assert_lists_equal(neoantigens, neoantigens2)
        
    def _assert_lists_equal(self, neoantigens, neoantigens2):
        self.assertEqual(len(neoantigens), len(neoantigens2))
        for n1, n2, in zip(neoantigens, neoantigens2):
            self.assertEqual(n1, n2)


class SchemaValidationTest(TestCase):
    
    def test_validation(self):
        neoantigens = [_get_random_neoantigen() for _ in range(5)]
        for n in neoantigens:
            SchemaConverter.validate(n)

    def test_field_invalid_type(self):
        neoantigen = _get_random_neoantigen()
        neoantigen.expression_value = "5.7"  # should be a float
        with self.assertRaises(struct.error):
            SchemaConverter.validate(neoantigen)


def _get_random_neoantigen():
    neoantigen = Neoantigen()
    neoantigen.variant_allele_frequency = np.random.uniform(0, 1)
    neoantigen.expression_value = np.random.uniform(0, 50)
    mutation = Mutation()
    mutation.mutated_aminoacid = random.choices(list(IUPACData.protein_letters), k=1)[0]
    mutation.wild_type_aminoacid = random.choices(list(IUPACData.protein_letters), k=1)[0]
    mutation.position = np.random.randint(0, 1000)
    neoantigen.mutation = mutation
    gene = Gene()
    gene.gene = "BRCA2"
    gene.transcript_identifier = "ENST1234567"
    gene.assembly = "hg19"
    neoantigen.gene = gene
    return neoantigen
