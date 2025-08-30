import tkinter as tk
from tkinter import ttk, font, scrolledtext
import pyglet
import os
import csv
import re
import copy
import itertools
import json

# --- Universal Paradigm Template and Placeholders ---
PLACEHOLDER_6 = ['Ø'] * 6
PLACEHOLDER_4 = ['Ø'] * 4
PLACEHOLDER_2 = ['Ø'] * 2
PLACEHOLDER_STR = 'Ø'

PARADIGM_TEMPLATE = {
    'INDICATIVE ACTIVE': {
        'Present': list(PLACEHOLDER_6), 'Imperfect': list(PLACEHOLDER_6), 'Future': list(PLACEHOLDER_6),
        'Perfect': list(PLACEHOLDER_6), 'Pluperfect': list(PLACEHOLDER_6), 'Future Perfect': list(PLACEHOLDER_6)
    },
    'SUBJUNCTIVE ACTIVE': {
        'Present': list(PLACEHOLDER_6), 'Imperfect': list(PLACEHOLDER_6),
        'Perfect': list(PLACEHOLDER_6), 'Pluperfect': list(PLACEHOLDER_6)
    },
    'INDICATIVE PASSIVE': {
        'Present': list(PLACEHOLDER_6), 'Imperfect': list(PLACEHOLDER_6), 'Future': list(PLACEHOLDER_6),
        'Perfect': list(PLACEHOLDER_6), 'Pluperfect': list(PLACEHOLDER_6), 'Future Perfect': list(PLACEHOLDER_6)
    },
    'SUBJUNCTIVE PASSIVE': {
        'Present': list(PLACEHOLDER_6), 'Imperfect': list(PLACEHOLDER_6),
        'Perfect': list(PLACEHOLDER_6), 'Pluperfect': list(PLACEHOLDER_6)
    },
    'IMPERATIVES': {
        'Pres Act': list(PLACEHOLDER_2), 'Pres Pass': list(PLACEHOLDER_2),
        'Fut Act': list(PLACEHOLDER_4), 'Fut Pass': list(PLACEHOLDER_4)
    },
    'NON-FINITE': {
        'INFINITIVES': {
            'Pres Act': PLACEHOLDER_STR, 'Perf Act': PLACEHOLDER_STR, 'Fut Act': PLACEHOLDER_STR,
            'Pres Pass': PLACEHOLDER_STR, 'Perf Pass': PLACEHOLDER_STR, 'Fut Pass': PLACEHOLDER_STR
        },
        'GERUND': {'Gen': PLACEHOLDER_STR, 'Dat': PLACEHOLDER_STR, 'Acc': PLACEHOLDER_STR, 'Abl': PLACEHOLDER_STR},
        'GERUND (-undus form)': {'Gen': PLACEHOLDER_STR, 'Dat': PLACEHOLDER_STR, 'Acc': PLACEHOLDER_STR, 'Abl': PLACEHOLDER_STR},
        'SUPINE': {'Acc': PLACEHOLDER_STR, 'Abl': PLACEHOLDER_STR},
        'PARTICIPLES': {}
    }
}

MASTER_TEMPLATE = {
    'INDICATIVE ACTIVE': {
        'Present': PLACEHOLDER_6, 'Imperfect': PLACEHOLDER_6, 'Future': PLACEHOLDER_6,
        'Perfect': PLACEHOLDER_6, 'Pluperfect': PLACEHOLDER_6, 'Future Perfect': PLACEHOLDER_6,
        'Future Perfect II (Archaic)': PLACEHOLDER_6,
        'Future (Archaic -bō)': PLACEHOLDER_6,
    },
    'SUBJUNCTIVE ACTIVE': {
        'Present': PLACEHOLDER_6, 'Imperfect': PLACEHOLDER_6,
        'Perfect': PLACEHOLDER_6, 'Pluperfect': PLACEHOLDER_6,
        'Aorist Subjunctive (Archaic)': PLACEHOLDER_6,
        'Archaic Optative (Theoretical)': PLACEHOLDER_6,
    },
    'INDICATIVE PASSIVE': {
        'Present': PLACEHOLDER_6, 'Imperfect': PLACEHOLDER_6, 'Future': PLACEHOLDER_6,
        'Perfect': PLACEHOLDER_6, 'Pluperfect': PLACEHOLDER_6, 'Future Perfect': PLACEHOLDER_6,
        'Future (Archaic -bō)': PLACEHOLDER_6,
    },
    'SUBJUNCTIVE PASSIVE': {
        'Present': PLACEHOLDER_6, 'Imperfect': PLACEHOLDER_6,
        'Perfect': PLACEHOLDER_6, 'Pluperfect': PLACEHOLDER_6,
    },
    'IMPERATIVES': {
        'Pres Act': PLACEHOLDER_4, 'Pres Pass': PLACEHOLDER_4,
        'Fut Act': PLACEHOLDER_4, 'Fut Pass': PLACEHOLDER_4
    },
    'NON-FINITE': copy.deepcopy(PARADIGM_TEMPLATE['NON-FINITE']) # Can reuse this part
}

ENDINGS_DATA = {
    'person': {
        'active': ['m', 's', 't', 'mus', 'tis', 'nt'],
        'passive': ['r', ['ris', 're'], 'tur', 'mur', 'minī', 'ntur']
    },
    'perfect_ind': ['ī', 'istī', 'it', 'imus', 'istis', ['ērunt', 'ēre']],
    'pluperfect_ind': ['eram', 'erās', 'erat', 'erāmus', 'erātis', 'erant'],
    'future_perfect_ind': ['erō', 'eris', 'erit', 'erimus', 'eritis', 'erint'],
    'perfect_subj': ['erim', 'erīs', 'erit', 'erīmus', 'erītis', 'erint'],
    'pluperfect_subj': ['issem', 'issēs', 'isset', 'issēmus', 'issētis', 'issent'],
    'future_perfect_2_ind': [['sō', 'sim'], 'sis', 'sit', 'simus', 'sitis', 'sint'],
    'archaic_aorist_subj': ['sim', 'sīs', 'sit', 'sīmus', 'sītis', 'sint'],
    'optative_active': ['m', 's', 't', 'mus', 'tis', 'nt'],
    'sync_perfect_ind': ['ī', 'stī', 't', 'mus', 'stis', ['runt', 're']],
    'sync_pluperfect_ind': ['ram', 'rās', 'rat', 'rāmus', 'rātis', 'rant'],
    'sync_future_perfect_ind': ['rō', 'ris', 'rit', 'rimus', 'ritis', 'rint'],
    'sync_perfect_subj': ['rim', 'rīs', 'rit', 'rīmus', 'rītis', 'rint'],
    'sync_pluperfect_subj': ['ssem', 'ssēs', 'sset', 'ssēmus', 'ssētis', 'ssent'],
    'sync_perfect_inf': 'sse'
}

MACRON_MAP = str.maketrans("āēīōūĀĒĪŌŪ", "aeiouAEIOU")

DEMACRON_MAP = str.maketrans("āēīōūĀĒĪŌŪ", "aeiouAEIOU")

def demacronize(word):
    """Strips all macrons from a Latin word."""
    return word.translate(DEMACRON_MAP)

def macronize(word):
    word = re.sub(r'([āēīōūĀĒĪŌŪ])([aeiouyāēīōūAEIOUY])', lambda m: m.group(1).translate(MACRON_MAP) + m.group(2), word)
    word = re.sub(r'([āēīōūĀĒĪŌŪ])([mrt])$', lambda m: m.group(1).translate(MACRON_MAP) + m.group(2), word)
    word = re.sub(r'([āēīōūĀĒĪŌŪ])(nt|nd)', lambda m: m.group(1).translate(MACRON_MAP) + m.group(2), word)
    return word

class AdjectiveDecliner:

    def __init__(self):
        self.endings_1_2 = {
            'm': {'Nom Sg': 'us', 'Gen Sg': 'ī', 'Dat Sg': 'ō', 'Acc Sg': 'um', 'Abl Sg': 'ō', 'Nom Pl': 'ī',
                  'Gen Pl': 'ōrum', 'Dat Pl': 'īs', 'Acc Pl': 'ōs', 'Abl Pl': 'īs'},
            'f': {'Nom Sg': 'a', 'Gen Sg': 'ae', 'Dat Sg': 'ae', 'Acc Sg': 'am', 'Abl Sg': 'ā', 'Nom Pl': 'ae',
                  'Gen Pl': 'ārum', 'Dat Pl': 'īs', 'Acc Pl': 'ās', 'Abl Pl': 'īs'},
            'n': {'Nom Sg': 'um', 'Gen Sg': 'ī', 'Dat Sg': 'ō', 'Acc Sg': 'um', 'Abl Sg': 'ō', 'Nom Pl': 'a',
                  'Gen Pl': 'ōrum', 'Dat Pl': 'īs', 'Acc Pl': 'a', 'Abl Pl': 'īs'}
        }
        self.endings_3_pap = {
            'Nom Sg': 'ns', 'Gen Sg': 'is', 'Dat Sg': 'ī', 'Acc Sg': 'em', 'Abl Sg': 'e',
            'Nom Pl': 'ēs', 'Gen Pl': 'ium', 'Dat Pl': 'ibus', 'Acc Pl': 'ēs', 'Abl Pl': 'ibus'
        }

    def decline_1_2(self, stem, lemma_nom_sg):
        paradigm = {}
        for gender, endings in self.endings_1_2.items():
            paradigm[gender.upper()] = {case: stem + end for case, end in endings.items()}
            if gender == 'm': paradigm[gender.upper()]['Nom Sg'] = lemma_nom_sg
        return paradigm

    def decline_pap(self, nom_sg, gen_stem):
        paradigm = {}
        mf_forms = {case: gen_stem + end for case, end in self.endings_3_pap.items()}
        mf_forms['Nom Sg'] = nom_sg
        paradigm['M/F'] = mf_forms
        n_forms = mf_forms.copy()
        n_forms['Acc Sg'] = nom_sg
        n_forms['Nom Pl'] = gen_stem + 'ia'
        n_forms['Acc Pl'] = gen_stem + 'ia'
        paradigm['N'] = n_forms
        return paradigm

class Verb:
    def __init__(self, verb_data, endings, decliner, irregular_paradigms):
        self.lemma = verb_data.get('lemma', '')
        self.principal_parts = verb_data.get('principal_parts', ['', '', ''])
        self.conjugation_num = verb_data.get('conjugation', '')
        self.properties = verb_data.get('properties', {})
        self.irregular_paradigms = irregular_paradigms
        while len(self.principal_parts) < 3: self.principal_parts.append('')
        self.p1 = self.lemma
        self.p2 = self.principal_parts[0]
        self.p3 = self.principal_parts[1]
        self.p4 = self.principal_parts[2]
        self.endings = endings
        self.decliner = decliner
        semantic_props = self.properties.get('semantic', [])
        self.is_deponent = 'deponent' in semantic_props
        self.is_semi_deponent = 'semi_deponent' in semantic_props
        domain_props = self.properties.get('domain', [])
        self.is_defective_present = 'defective_present' in domain_props
        general_props = self.properties.get('general', [])
        self.is_highly_irregular = 'highly_irregular' in general_props
        derivation_props = self.properties.get('derivation', [])
        self.is_compound = any(p.startswith('compound') for p in derivation_props)
        self.is_inchoative = 'inchoative' in derivation_props
        self.is_desiderative = 'desiderative' in derivation_props
        self.base_verb_lemma = ""
        self.true_prefix = ""
        if self.is_compound:
            for tag in derivation_props:
                if tag.startswith('compound'):
                    match = re.search(r'compound\((.*?)\)', tag)
                    if match:
                        content = match.group(1)
                        # --- THIS IS THE DEFINITIVE FIX ---
                        if '+' in content:
                            parts = content.split('+')
                            self.true_prefix = parts[0]
                            self.base_verb_lemma = parts[1]
                        else:
                            # Handle malformed tags like compound(sum) gracefully
                            self.true_prefix = ""  # No prefix
                            self.base_verb_lemma = content  # The content is the base
                        break  # Found the compound tag, stop looking

        self.irregularities = {tag for tags in self.properties.values() for tag in tags}
        self.suppletive_stems = {}
        for tag in general_props:
            if tag.startswith('suppletive('):
                match = re.search(r'suppletive\((.*?)\)', tag)
                if match:
                    stems = match.group(1).split(',');
                    if len(stems) >= 3:
                        self.suppletive_stems['present'] = stems[0]
                        self.suppletive_stems['perfect'] = stems[1]
                        self.suppletive_stems['supine'] = stems[2]
                break
        self.conjugation = self._get_conjugation()
        self.present_stem = self._get_present_stem()
        self.perfect_stem = self._get_perfect_stem()
        self.supine_stem = self._get_supine_stem()
        self.supine_abl = self.supine_stem + 'ū' if self.supine_stem else ''

    def __repr__(self):
        conj_repr = str(self.conjugation) if self.conjugation != 3.5 else "3-iō"
        type_str = "Deponent" if self.is_deponent else "Semi-Deponent" if self.is_semi_deponent else "Active"
        base_repr = f"Verb: {self.p1} | Conj: {conj_repr} ({type_str}) | Stems: P='{self.present_stem}', Perf='{self.perfect_stem}', Sup='{self.supine_stem}'"
        prop_str_parts = []
        display_order = ['derivation', 'semantic', 'present', 'perfect', 'supine', 'general', 'archaic', 'domain']
        for category in display_order:
            tags = self.properties.get(category)
            if tags:
                prop_str_parts.append(f"{', '.join(tags)}")
        if prop_str_parts:
            return f"{base_repr}\nMarkers: {' | '.join(prop_str_parts)}"
        else:
            return base_repr

    def _combine(self, stem, endings_list):
        forms = []
        for end in endings_list:
            alts_to_process = end if isinstance(end, list) else [end]
            combined_alts = [stem + alt for alt in alts_to_process]
            forms.append(' / '.join(combined_alts))
        return forms

    def _get_conjugation(self):
        is_io_verb = self.p1.endswith('iō') or (self.is_deponent and self.p1.endswith('ior'))
        if is_io_verb and self.conjugation_num == 3:
            return 3.5
        try:
            return int(self.conjugation_num)
        except (ValueError, TypeError):
            if self.p2.endswith('āre') or self.p2.endswith('ārī'): return 1
            if self.p2.endswith('ēre') or self.p2.endswith('ērī'): return 2
            if self.p2.endswith('ere') or self.p2.endswith('ī'): return 3
            if self.p2.endswith('īre') or self.p2.endswith('īrī'): return 4
            return self.conjugation_num

    def _get_present_stem(self):
        infinitive = self.p2
        if not infinitive: return ""
        irregular_infinitives = {'ferre': 'fer', 'esse': 'es', 'posse': 'pos', 'velle': 'vel', 'nōlle': 'nōl',
                                 'mālle': 'māl', 'īre': 'ī', 'fierī': 'fī'}
        if self.is_compound:
            for base_inf, base_stem in irregular_infinitives.items():
                if infinitive.endswith(base_inf):
                    prefix_len = len(infinitive) - len(base_inf)
                    prefix = infinitive[:prefix_len]
                    return prefix + base_stem
        if infinitive in irregular_infinitives:
            return irregular_infinitives[infinitive]
        if self.is_deponent:
            if infinitive.endswith('rī'):
                return infinitive[:-3]
            elif infinitive.endswith('ī'):
                return infinitive[:-1]
        elif infinitive.endswith('re'):
            return infinitive[:-3]
        return ""

    def _get_perfect_stem(self):
        p3 = self.p3.split(' / ')[0]
        if not p3: return ""
        if (self.is_deponent or self.is_semi_deponent):
            return p3.split(' ')[0][:-2]
        elif p3.endswith('ī'):
            return p3[:-1]
        return ""

    def _get_supine_stem(self):
        p4 = self.p4.split(' / ')[0]
        if not p4: return ""
        if p4.endswith('um'):
            return p4[:-2]
        return ""

    def generate_paradigm(self):
        p = copy.deepcopy(PARADIGM_TEMPLATE)

        # --- START OF THE DEFINITIVE FIX ---

        # We only check for 'defective_present'. We REMOVE the check for 'irregular_present'.
        # This ensures that ALL regular parts of an irregular verb (like fero's Present Subjunctive)
        # are always generated. The merge in main() will overwrite the truly irregular parts.
        if 'defective_present' not in self.irregularities:
            # Active Present System
            p['INDICATIVE ACTIVE']['Present'] = self._conjugate_present('ind', 'active')
            p['SUBJUNCTIVE ACTIVE']['Present'] = self._conjugate_present('subj', 'active')
            p['INDICATIVE ACTIVE']['Imperfect'] = self._conjugate_imperfect('ind', 'active')
            p['INDICATIVE ACTIVE']['Future'] = self._conjugate_future('ind', 'active')
            p['SUBJUNCTIVE ACTIVE']['Imperfect'] = self._conjugate_imperfect('subj', 'active')

            # Passive Present System (if applicable)
            if self.p1 != 'sum' and not self.is_semi_deponent:
                p['INDICATIVE PASSIVE']['Present'] = self._conjugate_present('ind', 'passive')
                p['SUBJUNCTIVE PASSIVE']['Present'] = self._conjugate_present('subj', 'passive')
                p['INDICATIVE PASSIVE']['Imperfect'] = self._conjugate_imperfect('ind', 'passive')
                p['INDICATIVE PASSIVE']['Future'] = self._conjugate_future('ind', 'passive')
                p['SUBJUNCTIVE PASSIVE']['Imperfect'] = self._conjugate_imperfect('subj', 'passive')

        # --- END OF THE DEFINITIVE FIX ---

        # --- PERFECT SYSTEM (ACTIVE & PASSIVE) ---
        if self.perfect_stem:
            p['INDICATIVE ACTIVE']['Perfect'] = self._combine(self.perfect_stem, self.endings['perfect_ind'])
            p['INDICATIVE ACTIVE']['Pluperfect'] = self._combine(self.perfect_stem, self.endings['pluperfect_ind'])
            p['INDICATIVE ACTIVE']['Future Perfect'] = self._combine(self.perfect_stem,
                                                                     self.endings['future_perfect_ind'])
            p['SUBJUNCTIVE ACTIVE']['Perfect'] = self._combine(self.perfect_stem, self.endings['perfect_subj'])
            p['SUBJUNCTIVE ACTIVE']['Pluperfect'] = self._combine(self.perfect_stem,
                                                                  self.endings['pluperfect_subj'])

        if self.p1 != 'sum' and self.supine_stem:
            sum_indicative = self.irregular_paradigms.get('sum', {}).get('INDICATIVE ACTIVE', {})
            sum_subjunctive = self.irregular_paradigms.get('sum', {}).get('SUBJUNCTIVE ACTIVE', {})
            ppp_sg, ppp_pl = f"{self.supine_stem}us", f"{self.supine_stem}ī"

            def build_passive_perfect(tense_name, sum_mood_dict):
                forms = []
                order_map = {
                    'Perfect Indicative': ['sum', 'fuī', 'es', 'fuistī', 'est', 'fuit', 'sumus', 'fuimus',
                                           'estis', 'fuistis', 'sunt', 'fuērunt', 'fuēre'],
                    'Pluperfect Indicative': ['eram', 'fueram', 'erās', 'fuerās', 'erat', 'fuerat', 'erāmus',
                                              'fuerāmus', 'erātis', 'fuerātis', 'erant', 'fuerant'],
                    'Future Perfect Indicative': ['erō', 'fuerō', 'eris', 'fueris', 'erit', 'fuerit', 'erimus',
                                                  'fuerimus', 'eritis', 'fueritis', 'erunt', 'fuerint'],
                    'Perfect Subjunctive': ['sim', 'siem', 'fuam', 'fuerim', 'sīs', 'siēs', 'fuās', 'fuerīs',
                                            'sit', 'siet', 'fuat', 'fuerit', 'sīmus', 'siēmus', 'fuāmus',
                                            'fuerīmus', 'sītis', 'siētis', 'fuātis', 'fuerītis', 'sint',
                                            'sient', 'fuant', 'fuerint'],
                    'Pluperfect Subjunctive': ['essem', 'fuissem', 'forem', 'essēs', 'fuissēs', 'forēs',
                                               'esset', 'fuisset', 'foret', 'essēmus', 'fuissēmus', 'forēmus',
                                               'essētis', 'fuissētis', 'forētis', 'essent', 'fuissent',
                                               'forent']
                }
                preferred_order = order_map.get(tense_name, [])

                sum_tenses = []
                if "Future Perfect" in tense_name:
                    sum_tenses = ['Future', 'Future Perfect']
                elif "Pluperfect" in tense_name:
                    sum_tenses = ['Imperfect', 'Pluperfect']
                elif "Perfect" in tense_name:
                    sum_tenses = ['Present', 'Perfect']

                for i in range(6):
                    participle = ppp_sg if i < 3 else ppp_pl
                    helpers_raw = []
                    for tense in sum_tenses:
                        sum_forms = sum_mood_dict.get(tense, [])
                        if isinstance(sum_forms, list) and len(sum_forms) > i:
                            helpers_raw.extend(sum_forms[i].split(' / '))

                    helpers = list(dict.fromkeys([h.strip() for h in helpers_raw if h and h != 'Ø']))
                    sorted_helpers = sorted(helpers,
                                            key=lambda h: preferred_order.index(h) if h in preferred_order else 99)

                    if sorted_helpers:
                        forms.append(f"{participle} {' / '.join(sorted_helpers)}")
                    else:
                        forms.append(PLACEHOLDER_STR)
                return forms

            p['INDICATIVE PASSIVE']['Perfect'] = build_passive_perfect('Perfect Indicative', sum_indicative)
            p['INDICATIVE PASSIVE']['Pluperfect'] = build_passive_perfect('Pluperfect Indicative', sum_indicative)
            p['INDICATIVE PASSIVE']['Future Perfect'] = build_passive_perfect('Future Perfect Indicative',
                                                                              sum_indicative)
            p['SUBJUNCTIVE PASSIVE']['Perfect'] = build_passive_perfect('Perfect Subjunctive', sum_subjunctive)
            p['SUBJUNCTIVE PASSIVE']['Pluperfect'] = build_passive_perfect('Pluperfect Subjunctive', sum_subjunctive)

        # --- VOICE-RELATED SWAPPING (DEPONENT / SEMI-DEPONENT) ---
        if self.is_deponent:
            p['INDICATIVE ACTIVE'] = p.pop('INDICATIVE PASSIVE')
            p['SUBJUNCTIVE ACTIVE'] = p.pop('SUBJUNCTIVE PASSIVE')
            p['IMPERATIVES']['Pres Act'] = p['IMPERATIVES'].pop('Pres Pass', PLACEHOLDER_4)
            p['IMPERATIVES']['Fut Act'] = p['IMPERATIVES'].pop('Fut Pass', PLACEHOLDER_4)
            inf_map = p['NON-FINITE']['INFINITIVES']
            inf_map['Pres Act'] = inf_map.pop('Pres Pass', PLACEHOLDER_STR)
            inf_map['Perf Act'] = inf_map.pop('Perf Pass', PLACEHOLDER_STR)
            inf_map['Fut Act'] = inf_map.pop('Fut Pass', PLACEHOLDER_STR)
            p['INDICATIVE PASSIVE'] = copy.deepcopy(PARADIGM_TEMPLATE['INDICATIVE PASSIVE'])
            p['SUBJUNCTIVE PASSIVE'] = copy.deepcopy(PARADIGM_TEMPLATE['SUBJUNCTIVE PASSIVE'])
        elif self.is_semi_deponent:
            p['INDICATIVE ACTIVE']['Perfect'] = p['INDICATIVE PASSIVE']['Perfect']
            p['INDICATIVE ACTIVE']['Pluperfect'] = p['INDICATIVE PASSIVE']['Pluperfect']
            p['INDICATIVE ACTIVE']['Future Perfect'] = p['INDICATIVE PASSIVE']['Future Perfect']
            p['SUBJUNCTIVE ACTIVE']['Perfect'] = p['SUBJUNCTIVE PASSIVE']['Perfect']
            p['SUBJUNCTIVE ACTIVE']['Pluperfect'] = p['SUBJUNCTIVE PASSIVE']['Pluperfect']
            p['NON-FINITE']['INFINITIVES']['Perf Act'] = p['NON-FINITE']['INFINITIVES']['Perf Pass']
            p['INDICATIVE PASSIVE'] = copy.deepcopy(PARADIGM_TEMPLATE['INDICATIVE PASSIVE'])
            p['SUBJUNCTIVE PASSIVE'] = copy.deepcopy(PARADIGM_TEMPLATE['SUBJUNCTIVE PASSIVE'])

        # --- SYNCOPATION MERGING ---
        if self.perfect_stem:
            sync_forms = self._generate_syncopated_perfects()
            if sync_forms:
                target_indicative = p.get('INDICATIVE ACTIVE', {})
                target_subjunctive = p.get('SUBJUNCTIVE ACTIVE', {})

                def merge_sync(target_dict, tense, sync_key):
                    if tense in target_dict and sync_key in sync_forms and sync_forms[sync_key]:
                        full_forms = target_dict[tense]
                        syncopated = sync_forms[sync_key]
                        merged_list = []
                        for full, sync in zip(full_forms, syncopated):
                            if not sync or sync == 'Ø':
                                merged_list.append(full)
                            else:
                                merged_list.append(f"{full} / {sync}")
                        target_dict[tense] = merged_list

                merge_sync(target_indicative, 'Perfect', 'Perfect')
                merge_sync(target_indicative, 'Pluperfect', 'Pluperfect')
                merge_sync(target_indicative, 'Future Perfect', 'Future Perfect')
                merge_sync(target_subjunctive, 'Perfect', 'Perfect Subjunctive')
                merge_sync(target_subjunctive, 'Pluperfect', 'Pluperfect Subjunctive')

        # --- NON-FINITE AND IMPERATIVES ---
        p['IMPERATIVES'] = self._generate_imperatives()
        p['NON-FINITE'] = self._generate_non_finite()

        # --- FINAL CLEANUP FOR DEPONENTS ---
        if self.is_deponent:
            if 'Present' in p['IMPERATIVES']: p['IMPERATIVES']['Pres Act'] = p['IMPERATIVES'].pop('Present')
            if 'Future' in p['IMPERATIVES']: p['IMPERATIVES']['Fut Act'] = p['IMPERATIVES'].pop('Future')
            if 'INFINITIVES' in p['NON-FINITE']:
                inf_map = p['NON-FINITE']['INFINITIVES']
                if 'Present' in inf_map: inf_map['Pres Act'] = inf_map.pop('Present')
                if 'Perfect' in inf_map: inf_map['Perf Act'] = inf_map.pop('Perfect')
                if 'Future' in inf_map: inf_map['Fut Act'] = inf_map.pop('Future')
        return p

    def _conjugate_present(self, mood, voice):
        if self.conjugation not in [1, 2, 3, 3.5, 4]: return PLACEHOLDER_6
        stem = self.present_stem
        ends = self.endings['person'][voice]
        if mood == 'subj':
            vowel = {'1': 'ē', '2': 'eā', '3': 'ā', '3.5': 'iā', '4': 'iā'}.get(str(self.conjugation))
            if self.conjugation == 2 and voice == 'active': vowel = 'ea'
            full_stem = stem + (vowel or '')
            return [macronize(f) for f in self._combine(full_stem, ends)]
        forms = [self.p1 if voice == 'active' else (self.p1[:-1] + 'or' if self.p1.endswith('ō') else self.p1)]
        for i, end in enumerate(ends[1:]):
            person = i + 2;
            form_base = ""
            if self.conjugation in [1, 2, 4]:
                theme_vowel = {'1': 'ā', '2': 'ē', '4': 'ī'}.get(str(self.conjugation))
                form_base = stem + theme_vowel
            elif self.conjugation in [3, 3.5]:
                vowel_map = {'active': {2: 'i', 3: 'i', 4: 'i', 5: 'i', 6: 'u'},
                             'passive': {2: 'e', 3: 'i', 4: 'i', 5: 'i', 6: 'u'}}
                vowel = vowel_map[voice][person]
                if self.conjugation == 3.5 and not (voice == 'passive' and person == 2): vowel = 'iu' if person == 6 else 'i'
                form_base = stem + vowel
            forms.append(form_base + (end[0] if isinstance(end, list) else end))
        final_forms = []
        for i, form in enumerate(forms):
            ending = ends[i]
            if isinstance(ending, list):
                stem_part = form[:-len(ending[0])]
                final_forms.append(" / ".join([stem_part + alt for alt in ending]))
            else:
                final_forms.append(form)
        return [macronize(f) for f in final_forms]

    def _conjugate_imperfect(self, mood, voice):
        if self.conjugation not in [1, 2, 3, 3.5, 4]: return PLACEHOLDER_6
        stem = self.present_stem
        ends = self.endings['person'][voice]
        if mood == 'ind':
            vowel = {'1': 'ā', '2': 'ē', '3': 'ē', '3.5': 'iē', '4': 'iē'}.get(str(self.conjugation))
            full_stem = stem + (vowel or '') + 'bā'
            return [macronize(f) for f in self._combine(full_stem, ends)]
        elif mood == 'subj':
            infinitive = self.p2
            if self.is_deponent:
                theme = {'1': 'āre', '2': 'ēre', '3': 'ere', '3.5': 'ere', '4': 'īre'}.get(str(self.conjugation))
                infinitive = stem + (theme or '')
            return [macronize(f) for f in self._combine(infinitive, ends)]

    def _conjugate_future(self, mood, voice):
        if self.conjugation not in [1, 2, 3, 3.5, 4]: return PLACEHOLDER_6
        if mood == 'subj': return []
        stem = self.present_stem
        ends = self.endings['person'][voice]
        if self.conjugation in [1, 2]:
            vowel = 'ā' if self.conjugation == 1 else 'ē'
            forms = [stem + vowel + ('bō' if voice == 'active' else 'bor')]
            second_person_base = stem + vowel + 'be'
            forms.append(self._combine(second_person_base, [ends[1]])[0])
            forms.append(stem + vowel + 'bi' + ends[2])
            forms.append(stem + vowel + 'bi' + ends[3])
            forms.append(stem + vowel + 'bi' + ends[4])
            forms.append(stem + vowel + 'bu' + ends[5])
            return [macronize(f) for f in forms]
        else:
            vowel = 'i' if self.conjugation in [3.5, 4] else ''
            forms = [stem + vowel + 'a' + ends[0]]
            forms.extend(self._combine(stem + vowel + 'ē', ends[1:]))
            return [macronize(f) for f in forms]

    def _generate_imperatives(self):
        if self.conjugation not in [1, 2, 3, 3.5, 4]:
            return {'Pres Act': ['Ø'] * 4, 'Pres Pass': ['Ø'] * 4, 'Fut Act': ['Ø'] * 4, 'Fut Pass': ['Ø'] * 4}
        imperatives = {}
        irregulars = {'dīcō': 'dīc', 'dūcō': 'dūc', 'faciō': 'fac', 'ferō': 'fer'}

        # --- PRESENT IMPERATIVES ---
        if self.is_deponent:
            sg_ending = {'1': 'āre', '2': 'ēre', '3': 'ere', '3.5': 'ere', '4': 'īre'}.get(str(self.conjugation))
            deponent_sg = self.present_stem + (sg_ending or '')
            pl_ending = {'1': 'āminī', '2': 'ēminī', '3': 'iminī', '3.5': 'iminī', '4': 'īminī'}.get(
                str(self.conjugation))
            deponent_pl = self.present_stem + (pl_ending or '')
            # FIX: Use the correct final key 'Pres Act'
            imperatives['Pres Act'] = [macronize(deponent_sg), 'Ø', macronize(deponent_pl), 'Ø']
        else:  # Handles both Active and Semi-Deponent
            sg = irregulars.get(self.p1, self.p2[:-2] if self.conjugation in [1, 2, 4] else self.present_stem + 'e')
            pl = sg + 'te'
            imperatives['Pres Act'] = [macronize(sg), 'Ø', macronize(pl), 'Ø']

            # Passive forms are only for non-semi-deponents
            if not self.is_semi_deponent:
                if self.p1 == 'faciō':
                    passive_present_forms = ['fī', 'Ø', 'fīte', 'Ø']
                else:
                    pres_pass_pl_ending = {'1': 'āminī', '2': 'ēminī', '3': 'iminī', '3.5': 'iminī', '4': 'īminī'}.get(
                        str(self.conjugation))
                    pres_pass_pl = self.present_stem + (pres_pass_pl_ending or '')
                    passive_present_forms = [macronize(self.p2), 'Ø', macronize(pres_pass_pl), 'Ø']
                imperatives['Pres Pass'] = passive_present_forms

        if not self.present_stem: return imperatives

        # --- FUTURE IMPERATIVES ---
        vowel = {'1': 'ā', '2': 'ē', '3': 'i', '3.5': 'i', '4': 'ī'}.get(str(self.conjugation))
        future_pl_vowel = {'1': 'ā', '2': 'ē', '3': 'u', '3.5': 'iu', '4': 'iu'}.get(str(self.conjugation))
        if self.is_deponent:
            future_sg = self.present_stem + (vowel or '') + 'tor'
            future_pl = self.present_stem + (future_pl_vowel or '') + 'ntor'
            # FIX: Use the correct final key 'Fut Act'
            imperatives['Fut Act'] = [macronize(future_sg), macronize(future_sg), 'Ø', macronize(future_pl)]
        else:  # Handles both Active and Semi-Deponent
            future_act_sg = self.present_stem + (vowel or '') + 'tō'
            future_act_2p = self.present_stem + (vowel or '') + 'tōte'
            future_act_3p = self.present_stem + (future_pl_vowel or '') + 'ntō'
            imperatives['Fut Act'] = [macronize(future_act_sg), macronize(future_act_sg), macronize(future_act_2p),
                                      macronize(future_act_3p)]

            # Passive forms are only for non-semi-deponents
            if not self.is_semi_deponent:
                if self.p1 == 'faciō':
                    imperatives['Fut Pass'] = ['fītō', 'fītō', 'Ø', 'fīuntō']
                else:
                    future_pass_sg = self.present_stem + (vowel or '') + 'tor'
                    future_pass_3p = self.present_stem + (future_pl_vowel or '') + 'ntor'
                    imperatives['Fut Pass'] = [macronize(future_pass_sg), macronize(future_pass_sg), 'Ø',
                                               macronize(future_pass_3p)]
        return imperatives

    def _generate_non_finite(self):
        parts = copy.deepcopy(PARADIGM_TEMPLATE['NON-FINITE'])
        participles_full = {}
        if self.p1 != 'sum':
            vowel_pap = {'1': 'ā', '2': 'ē', '3': 'ē', '3.5': 'iē', '4': 'iē'}.get(str(self.conjugation))
            if vowel_pap and self.present_stem:
                pap_nom = f"{self.present_stem}{vowel_pap}ns";
                short_vowel_pap = vowel_pap.translate(MACRON_MAP)
                pap_gen_stem = f"{self.present_stem}{short_vowel_pap}nt"
                participles_full['PAP'] = self.decliner.decline_pap(pap_nom, pap_gen_stem)
        if self.supine_stem:
            if self.p1 != 'sum':
                ppp_nom = f"{self.supine_stem}us"
                participles_full['PPP'] = self.decliner.decline_1_2(self.supine_stem, ppp_nom)
            fap_decline_stem = self.supine_stem if self.supine_stem.endswith('ūr') else self.supine_stem + 'ūr'
            fap_nom = f"{fap_decline_stem}us"
            participles_full['FAP'] = self.decliner.decline_1_2(fap_decline_stem, fap_nom)
        if self.p1 != 'sum':
            vowel_fpp = {'1': 'a', '2': 'e', '3': 'e', '3.5': 'ie', '4': 'ie'}.get(str(self.conjugation))
            if vowel_fpp and self.present_stem:
                fpp_stem = f"{self.present_stem}{vowel_fpp}nd"
                participles_full['FPP (Gerundive)'] = self.decliner.decline_1_2(fpp_stem, f"{fpp_stem}us")
                parts['GERUND'] = {'Gen': f"{fpp_stem}ī", 'Dat': f"{fpp_stem}ō", 'Acc': f"{fpp_stem}um",
                                   'Abl': f"{fpp_stem}ō"}
                if self.conjugation in [3.5, 4]:
                    fpp_stem_undus = f"{self.present_stem}und"
                    participles_full['FPP (Gerundive -undus form)'] = self.decliner.decline_1_2(fpp_stem_undus,
                                                                                                f"{fpp_stem_undus}us")
                    parts['GERUND (-undus form)'] = {'Gen': f"{fpp_stem_undus}ī", 'Dat': f"{fpp_stem_undus}ō",
                                                     'Acc': f"{fpp_stem_undus}um", 'Abl': f"{fpp_stem_undus}ō"}
        parts['PARTICIPLES'] = participles_full
        fore_alt = 'fore';
        inf = parts['INFINITIVES']

        # --- START OF RESTRUCTURED INFINITIVE LOGIC ---

        # 1. Present Infinitives
        if self.is_deponent:
            inf['Pres Act'] = self.p2
        else:  # Active and Semi-Deponent have an active present infinitive
            if self.p2:
                inf['Pres Act'] = self.p2
            # Only true active verbs have a present passive infinitive
            if not self.is_semi_deponent and self.p1 != 'sum':
                if self.present_stem and self.p2:
                    classical_pres_pass_inf = f"{self.present_stem}ī" if self.conjugation in [3,
                                                                                              3.5] else f"{self.p2[:-1]}ī"
                    if self.conjugation in [1, 3]:
                        poetic_inf = f"{self.p2[:-1]}ier" if self.conjugation == 1 else f"{self.present_stem}ier"
                        classical_pres_pass_inf += f" / {poetic_inf}"
                    inf['Pres Pass'] = classical_pres_pass_inf

        # 2. Perfect Infinitives
        if self.perfect_stem:
            if self.is_deponent or self.is_semi_deponent:
                ppp_lemma = f"{self.supine_stem}us, -a, -um"
                inf['Perf Act'] = f"{ppp_lemma} esse / {fore_alt}"
            else:  # True Active
                perf_act_inf = f"{self.perfect_stem}isse"
                if 'v_perfect' in self.properties.get('perfect', []):
                    sync_inf = self._generate_syncopated_perfects().get('Perfect Infinitive', '')
                    if sync_inf: perf_act_inf += f" / {sync_inf}"
                inf['Perf Act'] = perf_act_inf

        if self.supine_stem and not self.is_deponent and not self.is_semi_deponent:
            ppp_lemma = f"{self.supine_stem}us, -a, -um"
            inf['Perf Pass'] = f"{ppp_lemma} esse / {fore_alt}"

        # 3. Future Infinitives
        if self.supine_stem:
            fap_decline_stem = self.supine_stem if self.supine_stem.endswith('ūr') else self.supine_stem + 'ūr'
            fap_lemma = f"{fap_decline_stem}us, -a, -um"
            inf['Fut Act'] = f"{fap_lemma} esse / {fore_alt}"
            if not self.is_deponent and not self.is_semi_deponent and self.p4:
                inf['Fut Pass'] = f"{self.p4} īrī"

        # --- END OF RESTRUCTURED LOGIC ---

        if self.p1 != 'sum' and self.p4:
            parts['SUPINE']['Acc'] = self.p4
            parts['SUPINE']['Abl'] = self.supine_abl
        return parts

    def _get_true_root(self):
        stem = self.present_stem
        if 'no_infix_perfect' in self.properties.get('perfect', []) and ('n' in stem[:-1] or 'm' in stem[:-1]):
            last_nasal_pos = max(stem.rfind('n', 0, -1), stem.rfind('m', 0, -1))
            if last_nasal_pos != -1:
                proposed_root = stem[:last_nasal_pos] + stem[last_nasal_pos + 1:]
                vowel_pos = last_nasal_pos - 1
                if vowel_pos >= 0 and proposed_root[vowel_pos] in "aeiou":
                    vowel = proposed_root[vowel_pos]
                    macronized_vowel = {'a': 'ā', 'e': 'ē', 'i': 'ī', 'o': 'ō', 'u': 'ū'}.get(vowel, vowel)
                    proposed_root = proposed_root[:vowel_pos] + macronized_vowel + proposed_root[vowel_pos + 1:]
                return proposed_root
        return stem

    def _get_archaic_sigmatic_stems(self):
        """
        Internal helper method to generate all possible archaic sigmatic stems.
        This is the single source of truth for both the archaic future and aorist subjunctive.
        """
        check_lemma = self.base_verb_lemma if self.is_compound else self.p1

        # Handle `quaerō` and its compounds with apophony separately.
        if check_lemma == 'quaerō':
            # Simple `quaerō` uses 'quaess'
            if not self.is_compound:
                return ['quaess']
            # Compounds like `inquīrō` get `ss` added to the present stem root.
            # This is the FIX: 'inquīr' -> 'inquīss'.
            else:
                return [self.present_stem[:-1] + 'ss']

        special_archaic_stems = {'faciō': ['fax'], 'dīcō': ['dīx'], 'dūcō': ['dūx']}
        if check_lemma in special_archaic_stems:
            prefix = self.true_prefix if self.is_compound else ""
            return [prefix + s for s in special_archaic_stems[check_lemma]]

        final_stems = []
        root = self._get_true_root()

        if self.conjugation in [1, 2, 4]:
            theme_vowel = {'1': 'ā', '2': 'ē', '4': 'ī'}.get(str(self.conjugation))
            final_stems.append(self.present_stem + (theme_vowel or '') + 'ss')
        elif self.conjugation in [3, 3.5]:
            if root.endswith(('rr', 'll')):
                final_stems.append(root[:-1] + 's')
            elif root.endswith('qu'):
                final_stems.extend([root, root[:-2] + 'x'])
            elif root.endswith('r'):
                final_stems.extend([root[:-1] + 'rr', root[:-1] + 'ss'])
            elif root.endswith('mn'):
                final_stems.append(root[:-1] + 'ps')
            elif root.endswith('m'):
                final_stems.append(root + 'ps')
            elif root.endswith('b'):
                final_stems.append(root[:-1] + 'ps')
            elif root.endswith('tt'):
                final_stems.append(root[:-2] + 'ss')
            elif root.endswith(('lv', 'rv')):
                final_stems.append(root[:-1] + 's')
            elif root.endswith('x'):
                final_stems.append(root)
            elif root.endswith(('rt', 'lt')):
                final_stems.append(root[:-1] + 's')
            elif root.endswith(('g', 'c', 'h')):
                final_stems.append(root[:-1] + 'x')
            elif root.endswith(('d', 't')):
                final_stems.append(root[:-1] + 'ss')
            else:
                final_stems.append(root + 's')

        return sorted(list(set(final_stems)))

    def _generate_archaic_future(self):
        if self.is_inchoative or self.is_desiderative or self.p1 == 'eō' or not self.present_stem: return []

        stems = self._get_archaic_sigmatic_stems()
        if not stems: return []

        archaic_endings = [['ō', 'im'], 'is', 'it', 'imus', 'itis', 'int']
        forms = []
        for end in archaic_endings:
            alt_forms = [self._combine(stem, [end])[0] for stem in stems]
            forms.append(' / '.join(alt_forms))
        return forms

    def _generate_aorist_subjunctive(self):
        if self.is_inchoative or self.is_desiderative or self.p1 == 'eō' or not self.present_stem: return []

        stems = self._get_archaic_sigmatic_stems()
        if not stems: return []

        aorist_endings = self.endings['archaic_aorist_subj']
        aorist_paradigm = []

        for end in aorist_endings:
            alt_forms = []
            for stem in stems:
                if stem.endswith(('s', 'x')):
                    alt_forms.append(stem + end[1:])
                else:
                    base_form = stem + end
                    # THE DEFINITIVE FIX: This regex now correctly captures short or long 'i'
                    # and applies the phonological rule to both, fixing linquo and fero.
                    corrected_form = re.sub(r'([rumnqu])s([iī])', r'\1\2', base_form)
                    alt_forms.append(corrected_form)
            aorist_paradigm.append(' / '.join(alt_forms))

        return aorist_paradigm

    def _generate_archaic_optative(self):
        if self.is_inchoative or not self.present_stem: return []
        ends = self.endings['optative_active']
        optative_stem = ""

        # --- START OF FINAL FIX ---

        # For 'eō', the correct theoretical stem is 'eī-' (from the e- stem + ī optative marker).
        # This replaces the previous, less accurate 'ī-' stem.
        special_optative_stems = {
            'sum': 'sī', 'possum': 'possī', 'volō': 'velī', 'nōlō': 'nōlī', 'mālō': 'mālī',
            'dō': 'duī', 'edō': 'edī', 'for': 'ferē', 'eō': 'eī'
        }

        # --- END OF FINAL FIX ---

        if self.p1 in special_optative_stems:
            optative_stem = special_optative_stems[self.p1]
        else:
            if self.conjugation == 1:
                optative_stem = self.present_stem + 'ē'
            elif self.conjugation == 2:
                optative_stem = self.present_stem + 'eī'
            else:
                return []

        if optative_stem: return [macronize(f) for f in self._combine(optative_stem, ends)]
        return []

    def _generate_archaic_bo_future(self, voice):
        if not isinstance(self.conjugation, (int, float)):
            return []
        if self.conjugation < 3: return []
        if self.p1 == 'eō':
            return []
        active_ends = ['bō', 'bis', 'bit', 'bimus', 'bitis', 'bunt']
        passive_ends = ['bor', 'beris', 'bitur', 'bimur', 'biminī', 'buntur']
        ends = active_ends if voice == 'active' else passive_ends
        theme_vowel = {'3': 'ē', '4': 'ī', '3.5': 'iē'}.get(str(self.conjugation))
        base = self.present_stem + (theme_vowel or '')
        forms = [base + end for end in ends]
        if voice == 'passive': forms[1] = f"{base}beris / {base}bere"
        return [macronize(f) for f in forms]

    def _generate_syncopated_perfects(self):
        if not self.perfect_stem or not ('v_perfect' in self.properties.get('perfect', [])): return {}
        sync_paradigm = {}
        sync_stem = self.perfect_stem[:-1]
        tenses_to_process = {
            'Perfect': self.endings['sync_perfect_ind'],
            'Pluperfect': self.endings['sync_pluperfect_ind'],
            'Future Perfect': self.endings['sync_future_perfect_ind'],
            'Perfect Subjunctive': self.endings['sync_perfect_subj'],
            'Pluperfect Subjunctive': self.endings['sync_pluperfect_subj']
        }
        for tense, endings in tenses_to_process.items():
            generated_forms = []
            for end in endings:
                if isinstance(end, list):
                    sub_forms = []
                    for sub_end in end:
                        if sync_stem.endswith(('l', 'r')) and sub_end.startswith('r'):
                            sub_forms.append(sync_stem + 'u' + sub_end)
                        else:
                            sub_forms.append(sync_stem + sub_end)
                    generated_forms.append(' / '.join(sub_forms))
                else:
                    if sync_stem.endswith(('l', 'r')) and end.startswith('r'):
                        generated_forms.append(sync_stem + 'u' + end)
                    else:
                        generated_forms.append(sync_stem + end)
            sync_paradigm[tense] = generated_forms
        sync_paradigm['Perfect Infinitive'] = sync_stem + self.endings['sync_perfect_inf']
        return sync_paradigm

    def _combine_participle_and_helpers(self, participle, helper_forms):
        all_alts = []
        for form_group in helper_forms:
            if form_group == 'Ø': continue
            all_alts.extend([alt.strip() for alt in form_group.split(' / ')])
        if not all_alts: return participle
        standard_form = all_alts[0]
        other_forms = sorted(list(set(all_alts[1:])))
        final_alts = [standard_form] + other_forms
        return f"{participle} {' / '.join(final_alts)}"

    def generate_derived_verbs(self, db):
        derived_paradigms = {}
        if self.is_inchoative or self.is_desiderative or 'iterative' in self.properties.get('derivation', []):
            return {}
        if self.supine_stem and not self.is_highly_irregular and not self.is_deponent:
            iterative_stem = self.supine_stem + 'it'
            p1_iter = iterative_stem + 'ō'
            if db.find_verb(p1_iter):
                derived_paradigms['Iterative Verb'] = {'Info': f"[see '{p1_iter}']", 'Paradigm': {}}
            else:
                iterative_data = {
                    "lemma": p1_iter,
                    "principal_parts": [iterative_stem + 'āre', iterative_stem + 'āvī', iterative_stem + 'ātum'],
                    "conjugation": 1, "properties": {"derivation": ["iterative"]}
                }
                try:
                    iterative_verb = Verb(iterative_data, self.endings, self.decliner, self.irregular_paradigms)
                    iterative_paradigm = iterative_verb.generate_paradigm()
                    derived_paradigms['Iterative Verb'] = {'Info': f"{repr(iterative_verb)}",
                                                           'Paradigm': iterative_paradigm}
                except Exception as e:
                    print(f"DEBUG: Could not generate iterative verb for {self.p1}: {e}")
        if self.conjugation in [1, 2, 4] and not self.is_deponent and not self.is_highly_irregular:
            theme_vowel = {'1': 'ā', '2': 'ē', '4': 'ī'}.get(str(self.conjugation))
            inchoative_base = self.present_stem + (theme_vowel or '')
            p1_incho = inchoative_base + 'scō'
            if db.find_verb(p1_incho):
                derived_paradigms['Inchoative Verb'] = {'Info': f"[see '{p1_incho}']", 'Paradigm': {}}
            else:
                p3_incho = self.p3 if not self.is_deponent and not self.is_semi_deponent else ""
                inchoative_data = {
                    "lemma": p1_incho,
                    "principal_parts": [inchoative_base + 'scere', p3_incho, ""],
                    "conjugation": 3,
                    "properties": {"derivation": ["inchoative"], "semantic": self.properties.get('semantic', [])}
                }
                try:
                    inchoative_verb = Verb(inchoative_data, self.endings, self.decliner, self.irregular_paradigms)
                    inchoative_paradigm = inchoative_verb.generate_paradigm()
                    derived_paradigms['Inchoative Verb'] = {'Info': f"{repr(inchoative_verb)}",
                                                            'Paradigm': inchoative_paradigm}
                except Exception as e:
                    print(f"DEBUG: Could not generate inchoative verb for {self.p1}: {e}")
        if self.supine_stem:
            desiderative_stem = self.supine_stem if self.supine_stem.endswith('ūr') else self.supine_stem + 'ūr'
            p1_desid = desiderative_stem + 'iō'
            if db.find_verb(p1_desid):
                derived_paradigms['Desiderative Verb'] = {'Info': f"[see '{p1_desid}']", 'Paradigm': {}}
            else:
                desiderative_data = {
                    "lemma": p1_desid,
                    "principal_parts": [desiderative_stem + 'īre', "", ""],
                    "conjugation": 4, "properties": {"derivation": ["desiderative"]}
                }
                try:
                    desiderative_verb = Verb(desiderative_data, self.endings, self.decliner, self.irregular_paradigms)
                    desiderative_paradigm = desiderative_verb.generate_paradigm()
                    derived_paradigms['Desiderative Verb'] = {'Info': f"{repr(desiderative_verb)}",
                                                              'Paradigm': desiderative_paradigm}
                except Exception as e:
                    print(f"DEBUG: Could not generate desiderative verb for {self.p1}: {e}")
        return derived_paradigms

class LatinDB:
    def __init__(self, filepath, irregular_paradigms):
        self.verbs = {}
        self.demacronized_index = {}
        self.irregular_paradigms = irregular_paradigms
        # THE FIX: It now uses the global constant.
        self.endings = ENDINGS_DATA
        self.decliner = AdjectiveDecliner()
        self.load_data(filepath)

    def load_data(self, filepath):
        print(f"Loading Master Verb Database from '{filepath}'…")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                verb_data_list = json.load(f)
            for verb_data in verb_data_list:
                verb_obj = Verb(verb_data, self.endings, self.decliner, self.irregular_paradigms)
                self.verbs[verb_obj.lemma] = verb_obj
                demacronized_lemma = demacronize(verb_obj.lemma)
                self.demacronized_index[demacronized_lemma] = verb_obj
            print(f"Successfully loaded {len(self.verbs)} verbs from JSON.")
        except FileNotFoundError:
            print(f"FATAL ERROR: Database file not found at '{filepath}'.")
            self.verbs = None
        except json.JSONDecodeError as e:
            print(f"FATAL ERROR: The file '{filepath}' is not a valid JSON file. Error: {e}")
            self.verbs = None
        except Exception as e:
            import traceback
            print(f"An unexpected error occurred during data loading: {e}")
            traceback.print_exc()
            self.verbs = None

    def find_verb(self, lemma):
        return self.verbs.get(lemma)

def generate_compound_paradigm(compound_lemma, compound_map, base_paradigms):

    if compound_lemma not in compound_map:
        return None

    base_verb, prefix_normal, prefix_vowel = compound_map[compound_lemma]

    if base_verb not in base_paradigms:
        print(f"Warning: Base verb '{base_verb}' for '{compound_lemma}' not found in lookup.")
        return None

    base_paradigm = copy.deepcopy(base_paradigms[base_verb])
    base_paradigm.pop('Verb Info', None)

    def apply_prefix(data):
        if isinstance(data, str):
            if data.strip() == '-':
                return data
            if ' / ' in data:
                parts = data.split(' / ')
                return ' / '.join([apply_prefix(part) for part in parts])
            if ' ' in data:
                parts = data.split(' ')
                return ' '.join([apply_prefix(parts[0])] + parts[1:])

            if data in ['fers', 'fert', 'fer', 'ferte']:

                if prefix_vowel.endswith('f'):
                    return prefix_vowel + data
                return prefix_normal + data

            first_char = data[0] if data else ''

            if first_char in 'aeiouāēīōū':
                return prefix_vowel + data

            elif prefix_vowel.endswith(first_char):
                return prefix_vowel + data

            else:
                return prefix_normal + data

        elif isinstance(data, list):
            return [apply_prefix(item) for item in data]
        elif isinstance(data, dict):
            return {key: apply_prefix(value) for key, value in data.items()}
        else:
            return data

    new_paradigm = apply_prefix(base_paradigm)
    new_paradigm['Verb Info'] = f"{compound_lemma} (Compound of {base_verb})"
    return new_paradigm


def display_paradigm_gui(app, text_widget, paradigm_data):
    """
    This function takes a Tkinter Text widget and a paradigm dictionary,
    and inserts beautifully formatted text into it.
    """
    # --- FONT & COLOR SETUP ---
    # Get fonts and colors from the app instance directly
    font_bold = app.font_bold_medium
    font_bold_large = app.font_bold_large
    font_italic = app.font_italic_medium
    accent_color = app.ACCENT_COLOR

    # --- TAG CONFIGURATION ---
    # Define styles for different parts of the text
    text_widget.tag_configure("header", font=font_bold_large, foreground=accent_color, spacing1=15, spacing3=10)
    text_widget.tag_configure("subheader", font=font_bold, foreground=accent_color, spacing1=10, spacing3=5)
    text_widget.tag_configure("tense", font=font_bold, lmargin1=10, spacing1=5)
    text_widget.tag_configure("form_label", lmargin1=25, rmargin=10)
    text_widget.tag_configure("form_value", font=font_italic)
    text_widget.tag_configure("participle_header", font=font_bold, lmargin1=10, spacing1=5)
    text_widget.tag_configure("participle_gender", font=font_italic, lmargin1=25, spacing1=2)
    text_widget.tag_configure("participle_case", lmargin1=40, rmargin=10)
    text_widget.tag_configure("derived_header", font=font_bold_large, foreground=accent_color, spacing1=25, spacing3=10)
    text_widget.tag_configure("derived_info", font=font_italic, lmargin1=10)

    # --- HELPER FUNCTIONS ---
    def insert(text, tags=()):
        text_widget.insert(tk.END, text, tags)

    def is_empty(data):
        """Check if a list or dictionary contains only placeholders."""
        if isinstance(data, list):
            return all(item == 'Ø' for item in data)
        if isinstance(data, dict):
            return all(value == 'Ø' for value in data.values())
        return data == 'Ø'

    # --- DISPLAY LOGIC ---
    paradigm = paradigm_data.copy()
    derived_verbs_data = paradigm.pop('DERIVED VERBS', None)

    print_order = ['INDICATIVE ACTIVE', 'SUBJUNCTIVE ACTIVE', 'INDICATIVE PASSIVE', 'SUBJUNCTIVE PASSIVE',
                   'IMPERATIVES', 'NON-FINITE']

    for category in print_order:
        items = paradigm.get(category)
        if not items or is_empty(items):
            continue

        insert(f"--- {category.replace('_', ' ')} ---\n", "header")

        if category in ['INDICATIVE ACTIVE', 'SUBJUNCTIVE ACTIVE', 'INDICATIVE PASSIVE', 'SUBJUNCTIVE PASSIVE']:
            person_labels = ['1st Sg: ', '2nd Sg: ', '3rd Sg: ', '1st Pl: ', '2nd Pl: ', '3rd Pl: ']
            for tense, forms in items.items():
                if not forms or is_empty(forms):
                    continue
                insert(f"{tense}\n", "tense")
                for i, form in enumerate(forms):
                    if form != 'Ø':
                        insert(f"{person_labels[i]}", "form_label")
                        insert(f"{form}\n", "form_value")

        elif category == 'IMPERATIVES':
            labels = {'Pres Act': ['2nd Sg: ', '3rd Sg: ', '2nd Pl: ', '3rd Pl: '],
                      'Pres Pass': ['2nd Sg: ', '3rd Sg: ', '2nd Pl: ', '3rd Pl: '],
                      'Fut Act': ['2nd Sg: ', '3rd Sg: ', '2nd Pl: ', '3rd Pl: '],
                      'Fut Pass': ['2nd Sg: ', '3rd Sg: ', '2nd Pl: ', '3rd Pl: ']}
            for tense, forms in items.items():
                if not forms or is_empty(forms):
                    continue
                insert(f"{tense}\n", "tense")
                for i, form in enumerate(forms):
                    if form != 'Ø' and i < len(labels.get(tense, [])):
                        insert(f"{labels[tense][i]}", "form_label")
                        insert(f"{form}\n", "form_value")

        elif category == 'NON-FINITE':
            for sub_category, sub_items in items.items():
                if not sub_items or is_empty(sub_items):
                    continue

                insert(f"-- {sub_category} --\n", "subheader")

                if sub_category == 'PARTICIPLES':
                    for part_name, paradigm_data in sub_items.items():
                        insert(f"{part_name}:\n", "participle_header")
                        for gender, cases in paradigm_data.items():
                            insert(f"{gender}\n", "participle_gender")
                            for case, form in cases.items():
                                if form != 'Ø':
                                    insert(f"{case + ':':<10}", "participle_case")
                                    insert(f"{form}\n", "form_value")
                else:
                    for label, form in sub_items.items():
                        if form != 'Ø':
                            insert(f"{label}: ", "form_label")
                            insert(f"{form}\n", "form_value")

    if derived_verbs_data:
        insert("\n--- DERIVED VERBS ---\n", "derived_header")
        for derived_name, derived_info in derived_verbs_data.items():
            insert(f"\n--- {derived_name.upper()} ---\n", "header")
            insert(f"{derived_info['Info']}\n", "derived_info")
            if derived_info.get('Paradigm'):
                display_paradigm_gui(app, text_widget, derived_info['Paradigm'])

def apply_prefix_with_assimilation(prefix, root_word):

    if not root_word or root_word.strip() == '-': return root_word
    first_char = root_word.strip()[0]

    if prefix == 'ad':
        if first_char in 'cqv': return 'ac' + root_word
        if first_char == 'f': return 'af' + root_word
        if first_char == 'g': return 'ag' + root_word
        if first_char == 'l': return 'al' + root_word
        if first_char == 'n': return 'an' + root_word
        if first_char == 'p': return 'ap' + root_word
        if first_char == 'r': return 'ar' + root_word
        if first_char == 's': return 'as' + root_word
        if first_char == 't': return 'at' + root_word
    elif prefix == 'sub':
        if first_char == 'c': return 'suc' + root_word
        if first_char == 'f': return 'suf' + root_word
        if first_char == 'g': return 'sug' + root_word
        if first_char == 'p': return 'sup' + root_word
        if first_char == 'm': return 'sum' + root_word
    elif prefix == 'in':
        if first_char in 'lr': return 'i' + first_char + root_word
        if first_char in 'bmp': return 'im' + root_word
    elif prefix == 'ob':
        if first_char == 'c': return 'oc' + root_word
        if first_char == 'f': return 'of' + root_word
        if first_char == 'p': return 'op' + root_word
    elif prefix == 'con':
        if first_char in 'lr': return 'co' + first_char + root_word
        if first_char in 'bmp': return 'com' + root_word
    elif prefix == 'dis':
        if first_char == 'f': return 'dif' + root_word
    elif prefix == 'ex':
        if first_char == 'f': return 'ef' + root_word
    elif prefix == 'ab' and first_char == 'f':
        return 'au' + root_word  # aufero

    if prefix == 're' and first_char in 'aeiouāēīōū': return 'red' + root_word
    if prefix == 'prō' and first_char in 'aeiouāēīōū': return 'prōd' + root_word

    return prefix + root_word

def generate_compound_paradigm(compound_verb, base_paradigms):

    base_paradigm = copy.deepcopy(base_paradigms.get(compound_verb.base_verb_lemma))
    if not base_paradigm:
        print(f"Warning: Base verb '{compound_verb.base_verb_lemma}' for '{compound_verb.p1}' not found in lookup.")
        return {}

    base_paradigm.pop('Verb Info', None)

    def prefix_all_forms(data):
        if isinstance(data, str):
            if ' / ' in data: return ' / '.join([prefix_all_forms(part) for part in data.split(' / ')])
            if ' ' in data:
                parts = data.split(' ');
                return ' '.join([prefix_all_forms(parts[0])] + parts[1:])
            return apply_prefix_with_assimilation(compound_verb.true_prefix, data)
        elif isinstance(data, list):
            return [prefix_all_forms(item) for item in data]
        elif isinstance(data, dict):
            return {key: prefix_all_forms(value) for key, value in data.items()}
        else:
            return data

    new_paradigm = prefix_all_forms(base_paradigm)
    return new_paradigm


class App(tk.Tk):
    def __init__(self, db_instance):
        super().__init__()
        self.db = db_instance
        if not self.db.verbs:
            # Handle the case where the database failed to load
            self.title("Error")
            tk.Label(self, text="FATAL ERROR: Could not load the verb database.\nPlease check the console for details.",
                     font=("Helvetica", 12), fg="red", padx=20, pady=20).pack()
            return

        # --- FONT & COLOR CONFIGURATION ---
        self.load_custom_fonts()
        self.BG_COLOR = "#2E4600"  # Dark Green
        self.ACCENT_COLOR = "#FFD700"  # Gold/Yellow
        self.TEXT_COLOR = "#FFFFFF"  # White
        self.configure(bg=self.BG_COLOR)

        self.title("ECCE LOGOS")
        self.geometry("1000x800")

        # --- STYLING ---
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TFrame", background=self.BG_COLOR)
        style.configure("TLabel", background=self.BG_COLOR, foreground=self.TEXT_COLOR, font=self.font_regular)
        style.configure("Header.TLabel", font=self.font_bold_large)
        style.configure("Subheader.TLabel", font=self.font_italic)
        style.configure("Treeview", background="#203000", foreground=self.TEXT_COLOR, fieldbackground="#203000",
                        font=self.font_regular, rowheight=25)
        style.map("Treeview", background=[('selected', self.ACCENT_COLOR)], foreground=[('selected', self.BG_COLOR)])
        style.configure("Vertical.TScrollbar", background=self.BG_COLOR, troughcolor="#203000",
                        bordercolor=self.BG_COLOR)
        style.configure("TCheckbutton", background=self.BG_COLOR, foreground=self.TEXT_COLOR, font=self.font_regular)
        style.map("TCheckbutton",
                  background=[('active', self.BG_COLOR)],
                  indicatorcolor=[('selected', self.ACCENT_COLOR), ('!selected', self.TEXT_COLOR)],
                  indicatorbackground=[('selected', '#FFFFFF')])

        # --- LAYOUT ---
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_header()
        self.create_search_and_filter()
        self.create_results_display()

        # Initial population of the list
        self.update_verb_list()

    def load_custom_fonts(self):
        try:
            # Assumes font files are in the same directory as the script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            pyglet.font.add_file(os.path.join(script_dir, "Gentium-Regular.ttf"))
            pyglet.font.add_file(os.path.join(script_dir, "Gentium-Bold.ttf"))
            pyglet.font.add_file(os.path.join(script_dir, "Gentium-Italic.ttf"))
            pyglet.font.add_file(os.path.join(script_dir, "Gentium-Medium.ttf"))
            pyglet.font.add_file(os.path.join(script_dir, "Gentium-MediumItalic.ttf"))

            self.font_regular = font.Font(family="Gentium", size=12)
            self.font_bold = font.Font(family="Gentium", size=12, weight="bold")
            self.font_bold_medium = font.Font(family="Gentium", size=13, weight="bold") # For tenses
            self.font_italic = font.Font(family="Gentium", size=12, slant="italic")
            self.font_italic_medium = font.Font(family="Gentium", size=13, slant="italic") # For forms
            self.font_bold_large = font.Font(family="Gentium", size=20, weight="bold") # For main headers
            # --- THIS IS THE MISSING LINE ---
            self.font_monospace = font.Font(family="Courier New", size=11)
            # --- END OF FIX ---
        except Exception as e:
            print(f"Font loading failed: {e}. Falling back to default fonts.")
            # Fallback fonts
            self.font_regular = font.Font(family="Times New Roman", size=12)
            self.font_bold = font.Font(family="Times New Roman", size=12, weight="bold")
            self.font_bold_medium = font.Font(family="Times New Roman", size=13, weight="bold")
            self.font_italic = font.Font(family="Times New Roman", size=12, slant="italic")
            self.font_italic_medium = font.Font(family="Times New Roman", size=13, slant="italic")
            self.font_bold_large = font.Font(family="Times New Roman", size=20, weight="bold")
            # --- THIS IS THE MISSING LINE (FOR THE FALLBACK) ---
            self.font_monospace = font.Font(family="Courier New", size=11)
            # --- END OF FIX ---

    def create_header(self):
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        title = ttk.Label(header_frame, text="ECCE LOGOS", style="Header.TLabel",
                          foreground=self.ACCENT_COLOR)
        title.pack(side=tk.LEFT)

        author = ttk.Label(header_frame, text="by Anton Vladimir", style="TLabel")
        author.pack(side=tk.LEFT)

    def create_search_and_filter(self):
        search_frame = ttk.Frame(self.main_frame)
        search_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="Search:", font=self.font_bold).pack(side=tk.LEFT, padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.update_verb_list)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=self.font_regular, width=40)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        filter_button = ttk.Button(search_frame, text="Filter by Tags", command=self.open_filter_window)
        filter_button.pack(side=tk.LEFT, padx=(10, 0))

        self.active_filters = set()

    def create_results_display(self):
        display_frame = ttk.Frame(self.main_frame)
        display_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        display_frame.grid_rowconfigure(0, weight=1)
        display_frame.grid_columnconfigure(0, weight=1, minsize=300)
        display_frame.grid_columnconfigure(1, weight=3)

        # Verb List
        list_frame = ttk.Frame(display_frame)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.verb_tree = ttk.Treeview(list_frame, columns=("lemma",), show="headings", selectmode="browse")
        self.verb_tree.heading("lemma", text="Verb Lemma")
        self.verb_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.verb_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.verb_tree.configure(yscrollcommand=scrollbar.set)

        self.verb_tree.bind("<<TreeviewSelect>>", self.on_verb_select)

        # Paradigm Display
        self.paradigm_text = scrolledtext.ScrolledText(display_frame, wrap=tk.WORD,
                                                       font=self.font_monospace,
                                                       bg="#1c2b00", fg=self.TEXT_COLOR,
                                                       bd=0, relief="flat",
                                                       padx=10, pady=10)
        self.paradigm_text.grid(row=0, column=1, sticky="nsew")
        self.paradigm_text.insert(tk.END, "Select a verb from the list to view its paradigm.")
        self.paradigm_text.config(state=tk.DISABLED)

    def on_verb_select(self, event=None):
        selection = self.verb_tree.selection()
        if not selection:
            return

        selected_item = self.verb_tree.item(selection[0])
        verb_lemma = selected_item['values'][0]

        # This function now does all the work of clearing and inserting text.
        self.generate_paradigm_string(verb_lemma)

    def update_verb_list(self, *args):
        self.verb_tree.delete(*self.verb_tree.get_children())
        search_term = self.search_var.get().lower()

        for lemma, verb_obj in sorted(self.db.verbs.items()):
            # Filter by search term
            if search_term and search_term not in lemma.lower():
                continue

            # Filter by tags
            if self.active_filters:
                verb_tags = {tag for tags_list in verb_obj.properties.values() for tag in tags_list}
                if not self.active_filters.issubset(verb_tags):
                    continue

            self.verb_tree.insert("", tk.END, values=(lemma,))

    def open_filter_window(self):
        filter_win = tk.Toplevel(self)
        filter_win.title("Filter by Tags")
        filter_win.configure(bg=self.BG_COLOR)
        filter_win.transient(self)
        filter_win.grab_set()

        all_tags = sorted(list(
            {tag for verb in self.db.verbs.values() for tags in verb.properties.values() for tag in tags if
             not tag.startswith('compound')}))

        ttk.Label(filter_win, text="Select tags to filter by:", font=self.font_bold).pack(pady=10)

        self.filter_vars = {}
        checkbox_frame = ttk.Frame(filter_win)
        checkbox_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        num_columns = 4
        for i, tag in enumerate(all_tags):
            var = tk.BooleanVar(value=(tag in self.active_filters))
            cb = ttk.Checkbutton(checkbox_frame, text=tag, variable=var, style="TCheckbutton")
            cb.grid(row=i // num_columns, column=i % num_columns, sticky="w", padx=5, pady=2)
            self.filter_vars[tag] = var

        button_frame = ttk.Frame(filter_win)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Apply", command=lambda: self.apply_filters(filter_win)).pack(side=tk.LEFT,
                                                                                                    padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_filters).pack(side=tk.LEFT, padx=5)

    def apply_filters(self, window):
        self.active_filters = {tag for tag, var in self.filter_vars.items() if var.get()}
        self.update_verb_list()
        window.destroy()

    def clear_filters(self):
        for var in self.filter_vars.values():
            var.set(False)

    def generate_paradigm_string(self, lemma):
        found_verb = self.db.find_verb(lemma)
        if not found_verb:
            self.paradigm_text.config(state=tk.NORMAL)
            self.paradigm_text.delete('1.0', tk.END)
            self.paradigm_text.insert(tk.END, f"Error: Verb '{lemma}' not found.")
            self.paradigm_text.config(state=tk.DISABLED)
            return

        # --- Replicate the logic from your original main loop to build the final dictionary ---
        header_text = f"--- {repr(found_verb)} ---\n"
        final_paradigm = found_verb.generate_paradigm()

        if found_verb.p1 in self.db.irregular_paradigms:
            def deep_merge_dicts(base, override):
                for key, val in override.items():
                    if key in base and isinstance(base.get(key), dict) and isinstance(val, dict):
                        deep_merge_dicts(base[key], val)
                    else:
                        base[key] = val

            deep_merge_dicts(final_paradigm, self.db.irregular_paradigms[found_verb.p1])

        scaffold = copy.deepcopy(MASTER_TEMPLATE)

        def merge_into_scaffold(base, generated):
            for key, gen_val in generated.items():
                if key in base and isinstance(base.get(key), dict) and isinstance(gen_val, dict):
                    merge_into_scaffold(base[key], gen_val)
                else:
                    base[key] = gen_val

        merge_into_scaffold(scaffold, final_paradigm)

        target_dict_act = scaffold['INDICATIVE ACTIVE']
        target_dict_act['Future Perfect II (Archaic)'] = found_verb._generate_archaic_future()
        target_dict_act['Future (Archaic -bō)'] = found_verb._generate_archaic_bo_future('active')
        target_dict_subj_act = scaffold['SUBJUNCTIVE ACTIVE']
        target_dict_subj_act['Aorist Subjunctive (Archaic)'] = found_verb._generate_aorist_subjunctive()
        target_dict_subj_act['Archaic Optative (Theoretical)'] = found_verb._generate_archaic_optative()
        target_dict_pass = scaffold['INDICATIVE PASSIVE']
        if not found_verb.is_deponent:
            target_dict_pass['Future (Archaic -bō)'] = found_verb._generate_archaic_bo_future('passive')

        derived_verbs = found_verb.generate_derived_verbs(self.db)
        if derived_verbs:
            scaffold['DERIVED VERBS'] = derived_verbs

        # --- NEW DISPLAY LOGIC ---
        self.paradigm_text.config(state=tk.NORMAL)
        self.paradigm_text.delete('1.0', tk.END)

        self.paradigm_text.insert(tk.END, header_text, "subheader")

        # Call the new beautiful display function, passing the App instance (self)
        display_paradigm_gui(self, self.paradigm_text, scaffold)

        self.paradigm_text.config(state=tk.DISABLED)


def main():
    # --- SETUP STEP 1: Load irregular paradigms first ---
    try:
        with open('irregular_paradigms.json', 'r', encoding='utf-8') as f:
            IRREGULAR_PARADIGMS = json.load(f)
        print("Successfully loaded irregular paradigms.")
    except FileNotFoundError:
        print("Warning: 'irregular_paradigms.json' not found. Irregular verbs may not conjugate correctly.")
        IRREGULAR_PARADIGMS = {}
    except json.JSONDecodeError as e:
        print(f"FATAL ERROR: 'irregular_paradigms.json' is invalid. Error: {e}")
        return

    # --- SETUP STEP 2: Perfect the 'sum' paradigm BEFORE loading the main DB ---
    try:
        with open('verbs_Cicero.json', 'r', encoding='utf-8') as f:
            verb_list = json.load(f)
            sum_data = next((v for v in verb_list if v.get('lemma') == 'sum'), None)

            if sum_data and 'sum' in IRREGULAR_PARADIGMS:
                endings_dict = ENDINGS_DATA
                decliner_obj = AdjectiveDecliner()
                temp_sum_obj = Verb(sum_data, endings_dict, decliner_obj, IRREGULAR_PARADIGMS)
                sum_generated_paradigm = temp_sum_obj.generate_paradigm()

                def merge_dicts(base, override):
                    for key, val in override.items():
                        if key in base and isinstance(base.get(key), dict) and isinstance(val, dict):
                            merge_dicts(base[key], val)
                        elif key in base and isinstance(base.get(key), list) and isinstance(val, list):
                            len_base = len(base[key])
                            len_val = len(val)
                            max_len = max(len_base, len_val)
                            combined_list = []
                            for i in range(max_len):
                                form1_parts = (base[key][i] if i < len_base else "").split(' / ')
                                form2_parts = (val[i] if i < len_val else "").split(' / ')
                                all_forms = sorted(list(dict.fromkeys(
                                    [f.strip() for f in form1_parts + form2_parts if f and f.strip() != 'Ø'])))
                                combined_list.append(" / ".join(all_forms))
                            base[key] = combined_list
                        else:
                            base[key] = val

                complete_sum_paradigm = copy.deepcopy(IRREGULAR_PARADIGMS['sum'])
                merge_dicts(complete_sum_paradigm, sum_generated_paradigm)
                IRREGULAR_PARADIGMS['sum'] = complete_sum_paradigm
    except Exception as e:
        print(f"Critical error during pre-setup of 'sum': {e}")
        import traceback
        traceback.print_exc()
        return

    # --- SETUP STEP 3: Load the main database properly ---
    db = LatinDB('verbs_Cicero.json', IRREGULAR_PARADIGMS)

    # --- LAUNCH THE GUI ---
    app = App(db)
    app.mainloop()


if __name__ == "__main__":
    main()