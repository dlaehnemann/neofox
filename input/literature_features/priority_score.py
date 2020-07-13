#!/usr/bin/env python

# import modules
import math


class PriorityScore:

    def number_of_mismatches(self, epitope_wild_type, epitope_mutation):
        """
        This function calculates the number of mismatches between the wt and the mutated epitope
        """
        if len(epitope_wild_type) < len(epitope_mutation):
            epitope_mutation = epitope_mutation[:len(epitope_wild_type)]
        p1 = 0
        try:
            for i, aa in enumerate(epitope_mutation):
                if aa != epitope_wild_type[i]:
                    p1 += 1
        except IndexError:
            p1 = "NA"
        return p1

    def match_not_in_proteome(self, sequence, db):
        """
        This function checks if the mutated epitope has an exact match in a protein database (uniprot)
        Returns 0 if mutation is present in proteome and 1 if it not present
        """
        match = "1"
        try:
            seq_in_db = [sequence in entry for entry in db]
            if any(seq_in_db):
                match = "0"
        except:
            match = "NA"
        return match

    def calc_logistic_function(self, mhc_score):
        """
        Calculates negative logistic function given mhc score
        """
        try:
            log_score = 1.0 / (1.0 + math.exp(5.0 * (float(mhc_score) - 2.0)))
        except (OverflowError, ValueError) as e:
            log_score = "NA"
        return log_score

    def calc_priority_score(self, vaf_tumor, vaf_rna, transcript_expr, no_mismatch, score_mut, score_wt,
                            mut_not_in_prot):
        """
        This function calculates the Priority Score using parameters for mhc I.
        """
        L_mut = self.calc_logistic_function(score_mut)
        L_wt = self.calc_logistic_function(score_wt)
        priority_score = "NA"
        try:
            if vaf_tumor not in ["-1", "NA"]:
                priority_score = (L_mut * float(vaf_tumor) * math.tanh(float(transcript_expr))) * (
                        float(mut_not_in_prot) * (1 - 2 ** (-float(no_mismatch)) * L_wt))
            elif vaf_rna not in ["-1", "NA"]:
                priority_score = (L_mut * float(vaf_rna) * math.tanh(float(transcript_expr))) * (
                        float(mut_not_in_prot) * (1 - 2 ** (-float(no_mismatch)) * L_wt))
        except (TypeError, ValueError) as e:
            pass
        return priority_score




