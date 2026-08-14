#!/usr/bin/env python3
"""Fail-closed bounded audit of the IAR DLIB formatted-I/O cluster.

Scope: the twelve ``iar-dlib`` bucket members of the Apollo unanchored
provenance census (``tools/manifests/g2-apollo-unanchored-census-functions.tsv``)
in the official G2 ``s200_v2.2.6.10`` Apollo-main image:

- the 3,256-byte ``printf`` formatter core at ``0x00481836``,
- the 2,778-byte ``scanf`` scanner core at ``0x004D1638``,
- the 420-byte Annex-K string-conversion helper at ``0x004D2158``,
- the 28-byte constraint-handler dispatcher at ``0x004D40A0``,
- the 466-byte hex-float scanner at ``0x00585410``,
- the 236-byte ``strtod`` engine at ``0x00542C20``,
- the 70-byte scanset membership matcher at ``0x004D2112``, and
- five small wrappers (three bounded/unbounded ``printf``-family output
  wrappers, one default-output wrapper, one string-input ``scanf`` wrapper).

For every unit the analyzer re-derives, from the authenticated image alone,
the exact body span and SHA-256, the linear-decode coverage (the ``scanf``
core carries a 22-byte inline literal/jump-table window), the external
BL/B.W call census, the DLIB diagnostic-string materialization sites
(``addw``/``adr`` PC-relative forms plus the IAR self-relative PIC
``ldr``/``add pc`` idiom), the remaining PC-relative literal loads, the
image-wide BL/B.W ingress census with caller-address digests, a
stored-pointer scan (no image word may name a unit entry), and the unit
boundary context.  Any drift raises :class:`AuditError`.

With ``--ghidra-corpus`` the audit additionally authenticates the 64-shard
corpus ``SHA256SUMS``, re-checks each unit's corpus envelope span, and
splits every raw ingress site into corpus-token-verified callers and
unverifiable sites (raw bytes that decode as BL/B.W to a unit entry but lie
inside Ghidra's rejected oversized envelopes, where decompilation tokens
cannot corroborate them).  Both halves are pinned by count and digest.

The analyzer is read-only and deterministic; no hardware operation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any, Sequence

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
DEFAULT_CENSUS_TSV = ROOT / "tools/manifests/g2-apollo-unanchored-census-functions.tsv"
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
LOAD_BASE = 0x0043_7FE0

# Corpus authentication mirrors analyze_apollo_embedded_source_paths.py.
ACCEPTED_CORPUS_SHA256SUMS_SHA256 = frozenset(
    {
        "3ff8aa908e5841823df9384cfbffca91d657816274797f332a45ff93a8aa832f",
        "87d0befa001f042918bd6af83b0f50e13dd95aab160b0e520f2cb0bc55c6404e",
    }
)
EXPECTED_LOG_COUNT = 64

# The ten IAR DLIB formatted-I/O diagnostic strings.  No other provider in
# the image emits the Annex-K ``_s`` spellings or the constraint-handler
# message; the hex digit table is the DLIB float scanner's signature.  Each
# string must occur exactly once, at the pinned address.  Addresses are
# re-derived from the image on every run; only the pin is hardcoded.
SIGNATURE_STRINGS = (
    ("printf_bad_n_argument", "printf: bad %n argument", 0x004826CC,
     "5a82ce27e149ec57b35115c21b0e7e411ce2371ede6c94441aa7abdc0b951030"),
    ("printf_s_bad_s_argument", "printf_s: bad %s argument", 0x004824FC,
     "3b7b5a940d4213b698d6cd39c9105c5b4fd386a173655c229aaf2963e93cef1d"),
    ("printf_s_n_disallowed", "printf_s: %n disallowed", 0x004826B4,
     "de3bb66359192ae004733750117858e45fed2c59768b62a6ec03c74e6f969fca"),
    ("scanf_s_bad_n_argument", "scanf_s: bad %n argument", 0x004D2308,
     "2230510d33de4415774f3be24ead070604c2b6f2bbccb55b706bd0b53edc09e2"),
    ("scanf_s_bad_integer_argument", "scanf_s: bad integer argument", 0x004D2344,
     "456f5ddb79db253c9577195a57a4f598d99ddfe3181458047b554b8b68c35e73"),
    ("scanf_s_bad_size_argument", "scanf_s: bad %c, %s, or %[ size", 0x004D2324,
     "39a550e8c443f189e2f4ee244b06639943060ed5033c140be9bca26e7acbe4f5"),
    ("scanf_s_bad_float_argument", "scanf_s: bad floating-point argument", 0x007514CC,
     "a310cfdbd4ad8bd76fd609ff2f1216e7dfe005f0746d9a83186de647d6542e21"),
    ("scanf_s_bad_argument", "scanf_s: bad %c, %s, or %[ argument", 0x0075D3A4,
     "afec4b0e079b54a2b79a803bf6edfe730cf6fff139bdb00106c1a26da9e4f003"),
    ("constraint_bad_message", " constraint handler: bad message", 0x004D40BF,
     "8a34984f320d51da63a487ebc7f418a01f9216041b262b0e5a59eb0efc7a9688"),
    ("hex_digit_table", "0123456789abcdefABCDEF", 0x005855E8,
     "40351e03506ee12cedadf6a813fd8d8531e7fd10e951f5fc6610ac58bbfed33b"),
)

# Adjacent data spans that form the cluster's physical identity: literal
# pools, the constraint message overlapping its pool word's top byte, the
# scanf_s string island, the hex-float cap/nibble tables, the strtod double
# constants, and the errno island shared with the bounded runtime census.
EVIDENCE_SPANS = (
    ("constraint_pool_and_message", 0x004D40BC, 0x004D40E0,
     "b94d82494428a7e57fd3aa339d09520f49b96b3c88e97217bf5ea3bbd1f4d6d5"),
    ("scanf_s_island", 0x004D22FC, 0x004D2362,
     "270e47da9150ccc7c16a556c9b95ff13186a4f1e5db563f849c683d15118a68e"),
    ("hexfloat_cap_word", 0x005855E4, 0x005855E8,
     "a2a347ae5162fe3b22728e7280793e39c7de33da1a63724cc3fcfa766174f7e5"),
    ("hexfloat_nibble_map", 0x00585600, 0x00585616,
     "eb9929efa04887df32466c5d74bc02f63cf7fb7c4f9dc994a2e53e9ca15dc579"),
    ("strtod_double_constants", 0x00542D0C, 0x00542D44,
     "13be171b021b11c993c6dd9d185288d489f8c1893bd3ba94229f529c48d19d11"),
    ("errno_island", 0x00439CD0, 0x00439CE0,
     "0d441527b2ae7b59077c4bf26520f57704ef2c60c91719c900279c3f3fcfc222"),
)

# Per-unit pins.  ``calls`` are external BL/B.W sites as (site, kind,
# target); ``strings`` are DLIB diagnostic-string materializations as (site,
# mnemonic, target); ``pics`` are IAR self-relative PIC ``ldr [pc]`` +
# ``add pc`` pairs as (ldr site, literal cell, resolved target) where the
# resolved target is cell + signed contents; ``lits`` are the remaining
# PC-relative literal loads as (site, cell, value).  ``before``/``after``
# pin 8/16 bytes of boundary context.  ``ingress_*`` pin the raw
# image-wide BL/B.W caller census (count per kind and SHA-256 of the sorted
# little-endian site addresses).
EXPECTED_UNITS = (
    {
        'name': 'bounded_printf_wrapper_a', 'start': 0x0044B728, 'end': 0x0044B766,
        'sha256': '0b3f0ee4463f8a2560eb9a1ac68060b39fb797c0c44f5a85daa923fe5bcf14fd',
        'code_end': 0x0044B766, 'instructions': 29, 'blx_sites': 0,
        'calls': ((4503374, 'bl', 4724790),),
        'strings': (),
        'pics': ((4503368, 4503400, 4430987),),
        'lits': (),
        'before': '34d26d001cd57800', 'after': '00bf23e5feff08b584b0002303930029',
        'ingress_bl': 156, 'ingress_bw': 0, 'ingress_sha256': 'ab1139cffffffff657054f83b4db6756acbda99a68845119055dc5168a6c1676',
    },
    {
        'name': 'bounded_printf_wrapper_b', 'start': 0x0044B76C, 'end': 0x0044B7A2,
        'sha256': '6370164665446b0f6232e3883ca06fe954ee4aa335dc433328232bbf5e90ee12',
        'code_end': 0x0044B7A2, 'instructions': 26, 'blx_sites': 0,
        'calls': ((4503436, 'bl', 4724790),),
        'strings': (),
        'pics': ((4503430, 4503460, 4430987),),
        'lits': (),
        'before': '08fb00bf23e5feff', 'after': '00bfe7e4feff80b50a00002108f0caff',
        'ingress_bl': 3, 'ingress_bw': 0, 'ingress_sha256': 'a24a266bcd2d7e1127033e2a8f1ee88eeecd342ddadf7a93757f38af977ce9ac',
    },
    {
        'name': 'string_scanf_wrapper', 'start': 0x00475FC0, 'end': 0x00475FE2,
        'sha256': '6b77d50c936d0f4f33f769721b862cdbb3522883c9904dcc5673b0a2f7b1f81a',
        'code_end': 0x00475FE2, 'instructions': 15, 'blx_sites': 0,
        'calls': ((4677592, 'bl', 5051960),),
        'strings': (),
        'pics': ((4677586, 4677604, 4430791),),
        'lits': (),
        'before': 'f435770034547400', 'after': '00bfe33bfcff2de9f84195b004a8dff8',
        'ingress_bl': 7, 'ingress_bw': 0, 'ingress_sha256': '2ef5fe1939e344d3cf8be8ce4e0935c4952a333b3b39217b533cb124f0e93b73',
    },
    {
        'name': 'printf_core', 'start': 0x00481836, 'end': 0x004824EE,
        'sha256': '0ace800002b34fa464fd3a816691e77df43a7919b2747ef608d0b89213786fb0',
        'code_end': 0x004824EE, 'instructions': 1270, 'blx_sites': 4,
        'calls': ((4725118, 'bl', 4724760), (4725326, 'bl', 5062816), (4725348, 'bl', 4728452), (4725422, 'bl', 4728452), (4725496, 'bl', 4728452), (4725574, 'bl', 4728452), (4725622, 'bl', 4728452), (4725658, 'bl', 4498492), (4725670, 'bl', 5062880), (4726236, 'bl', 4430820), (4726254, 'bl', 5062992), (4726372, 'bl', 5063104), (4726408, 'bl', 4440240), (4726416, 'bl', 5063156), (4726424, 'bl', 5063416), (4726436, 'bl', 5063430), (4726448, 'bl', 5063444), (4726672, 'bl', 4728364), (4726686, 'bl', 4728364), (4726698, 'bl', 5063462), (4726746, 'bl', 5063480), (4726816, 'bl', 5063494), (4726828, 'bl', 5063444), (4726838, 'bl', 5063508), (4726976, 'bl', 5063592), (4727146, 'bl', 4430820), (4727284, 'bl', 4430820), (4727448, 'bl', 4430820), (4727506, 'bl', 4430820), (4727560, 'bl', 4430820), (4727928, 'bl', 4728088)),
        'strings': ((4725322, 'addw', 4728060), (4725734, 'addw', 4728500), (4725794, 'addw', 4728524), (4725818, 'addw', 4728524), (4725852, 'addw', 4728524), (4725878, 'addw', 4728524), (4725902, 'addw', 4728524), (4725926, 'addw', 4728524), (4725960, 'addw', 4728524), (4725990, 'addw', 4728524)),
        'pics': (),
        'lits': ((4724966, 4728048, 214748363), (4725064, 4728048, 214748363), (4726636, 4728436, 100000), (4726682, 4728440, 1072693248), (4726834, 4728444, 1100470148)),
        'before': '000040f020007047', 'after': '0000cbcccc0c686a6c747a4c00007072',
        'ingress_bl': 4, 'ingress_bw': 0, 'ingress_sha256': '5c4d0623883e5b1aa07f186af492a362080dc229d0556e25b3bd1e70c982bf31',
    },
    {
        'name': 'unbounded_printf_wrapper', 'start': 0x004B4728, 'end': 0x004B4762,
        'sha256': 'bb81bae4ec7909074b049262b5da647de77fda198db92fca072b1fb3383cd8a6',
        'code_end': 0x004B4762, 'instructions': 27, 'blx_sites': 0,
        'calls': ((4933446, 'bl', 4724790),),
        'strings': (),
        'pics': ((4933440, 4933476, 4429767),),
        'lits': (),
        'before': '80b5c6f7d7fe01bd', 'after': '00bf6350f8ff010009b2002909d40122',
        'ingress_bl': 75, 'ingress_bw': 0, 'ingress_sha256': 'd414f74f35b83ddc4efac33c70b720b3fa151da7ce0518ba6a9ca6be055cf066',
    },
    {
        'name': 'scanf_core', 'start': 0x004D1638, 'end': 0x004D2112,
        'sha256': '54dcd834ea6fcf74db400e38df7635f5b0686f4253db1a9fe6b05af7c2a3a120',
        'code_end': 0x004D20FC, 'instructions': 1154, 'blx_sites': 16,
        'calls': ((5052016, 'bl', 5068974), (5052030, 'bl', 5051932), (5052044, 'bl', 5068974), (5052120, 'bl', 5051932), (5052184, 'bl', 4724760), (5052254, 'bl', 4724760), (5052276, 'bl', 5068974), (5052290, 'bl', 5051932), (5052474, 'bl', 5051932), (5052642, 'bl', 5051898), (5052666, 'bl', 5051898), (5052688, 'bl', 5051898), (5052718, 'bl', 5051898), (5052750, 'bl', 5051898), (5052780, 'bl', 5051898), (5052802, 'bl', 5051898), (5052816, 'bl', 5051932), (5052846, 'bl', 5051880), (5052858, 'bl', 5512104), (5052912, 'bl', 5051898), (5052942, 'bl', 5051898), (5052964, 'bl', 5051898), (5052984, 'bl', 5051932), (5053176, 'bl', 5051880), (5053226, 'bl', 5051880), (5053318, 'bl', 5063592), (5053378, 'bl', 5051880), (5053440, 'bl', 5051880), (5053558, 'bl', 5051932), (5053590, 'bl', 5512130), (5053730, 'bl', 5051880), (5053776, 'bl', 5051880), (5053824, 'bl', 5512130), (5053830, 'bl', 5063156), (5053888, 'bl', 5512138), (5054136, 'bl', 5051880), (5054282, 'bl', 5051932), (5054322, 'bl', 5512580), (5054534, 'bl', 5512748), (5054670, 'bl', 5062816), (5054684, 'bl', 5054808)),
        'strings': ((5052536, 'addw', 5055240), (5052560, 'addw', 5055240), (5052584, 'addw', 5055240), (5052612, 'addw', 5055240), (5054668, 'adr', 5055300)),
        'pics': ((5053620, 5054716, 7673036), (5053856, 5054716, 7673036), (5053876, 5054716, 7673036)),
        'lits': ((5052136, 5054720, 214748363), (5053904, 5055228, 2147483646)),
        'data_window_sha256': '2ba1554e5791186a8f55c2fb0f72d20fcfaaa4489d9bf106a295d0bfb2344b4f',
        'before': '0022184770470000', 'after': 'c9b208e003789942a4bf90f802c08c45',
        'ingress_bl': 1, 'ingress_bw': 0, 'ingress_sha256': '0fa20932fec5a04c1a5ee9b32ca5c745911600bb59558bf5ee8733b119b2816e',
    },
    {
        'name': 'scanset_matcher', 'start': 0x004D2112, 'end': 0x004D2158,
        'sha256': '154d24d2cf8f15fed12b16d091a734a70d216ceda6fabb0978cadb522139a2c2',
        'code_end': 0x004D2158, 'instructions': 32, 'blx_sites': 0,
        'calls': (),
        'strings': (),
        'pics': (),
        'lits': (),
        'before': '00001bb0bde8f08f', 'after': '2de9f04f92460027baf1000f83b08046',
        'ingress_bl': 2, 'ingress_bw': 0, 'ingress_sha256': '4bc62cc68aaeb4d058e18d464045e2cf7a537ad04392e8aacf961bbd1f69320b',
    },
    {
        'name': 'scanf_string_helper', 'start': 0x004D2158, 'end': 0x004D22FC,
        'sha256': '0e089f2af1c9e9d36403cea97bef7aba808a2cddd67a8da9678cf33d632051b1',
        'code_end': 0x004D22FC, 'instructions': 176, 'blx_sites': 1,
        'calls': ((5054870, 'bl', 4724760), (5054898, 'bl', 5062880), (5054994, 'bl', 5062816), (5055092, 'bl', 5054738), (5055098, 'bl', 5068974), (5055114, 'bl', 5062880), (5055122, 'bl', 5062880), (5055130, 'bl', 5054738), (5055170, 'bl', 5051932)),
        'strings': ((5054992, 'adr', 5055268),),
        'pics': ((5054950, 5054960, 7721892),),
        'lits': (),
        'before': '0120704700207047', 'after': 'feffff7f63436e5b000000007363616e',
        'ingress_bl': 1, 'ingress_bw': 0, 'ingress_sha256': '9d1bd2883ec668326de0d779c50c76721ee86f46488302d99c04eb0d9871024a',
    },
    {
        'name': 'constraint_dispatcher', 'start': 0x004D40A0, 'end': 0x004D40BC,
        'sha256': '9e0e60f5fcfdbba0e2b7efde09ad1bee23ce431af97f99806a21f2634baca18a',
        'code_end': 0x004D40BC, 'instructions': 13, 'blx_sites': 1,
        'calls': ((5062836, 'bl', 5512052),),
        'strings': ((5062820, 'adr', 5062848),),
        'pics': (),
        'lits': ((5062822, 5062844, 537349904),),
        'before': '5e4f0720fced00e0', 'after': '104f0720636f6e73747261696e742068',
        'ingress_bl': 3, 'ingress_bw': 0, 'ingress_sha256': '941d53f77fec97d5e68ba672ec0e0ba460f4fecc75499f2f50c84cb0f7377b45',
    },
    {
        'name': 'strtod_engine', 'start': 0x00542C20, 'end': 0x00542D0C,
        'sha256': '4b72a352e4440bba5c1c96f26e7cfe43b0504577116ae7b7d9b242f10ac865d9',
        'code_end': 0x00542D0C, 'instructions': 87, 'blx_sites': 0,
        'calls': ((5516342, 'bl', 5787956), (5516372, 'bl', 5788248), (5516450, 'bl', 5788688), (5516508, 'bl', 5063176), (5516516, 'bl', 5515904)),
        'strings': (),
        'pics': (),
        'lits': (),
        'before': '31bd00bfbccb1b00', 'after': '436fac642806c80a3cbf737fdd4f1575',
        'ingress_bl': 1, 'ingress_bw': 0, 'ingress_sha256': '277ec4201bd1d0ebfee4ef0108a4b904898a906e3a7578a503c8a13b06720207',
    },
    {
        'name': 'hexfloat_scanner', 'start': 0x00585410, 'end': 0x005855E2,
        'sha256': '4a25c7b2418cbb186d7f30a2a2971fd2bfd49b1fea0bd485e089561dccc8aa5a',
        'code_end': 0x005855E2, 'instructions': 186, 'blx_sites': 0,
        'calls': ((5788800, 'bl', 5062880), (5788808, 'bl', 5063592), (5788878, 'bl', 5062880)),
        'strings': ((5788740, 'adr', 5789160), (5788796, 'adr', 5789160), (5788876, 'adr', 5789160)),
        'pics': (),
        'lits': ((5789080, 5789156, 100000000),),
        'before': 'f08f00bf00e1f505', 'after': '000000e1f50530313233343536373839',
        'ingress_bl': 2, 'ingress_bw': 0, 'ingress_sha256': '0a26e5b23d1dd2ba621a9af63ddc9873b7fa45581a5fe724fcafd14bc183dcfa',
    },
    {
        'name': 'default_output_printf_wrapper', 'start': 0x00595A34, 'end': 0x00595A56,
        'sha256': '73780de586940ab94f4af62a556a91c9ae0c74550afbd756f5c1bba53dc2fad0',
        'code_end': 0x00595A56, 'instructions': 15, 'blx_sites': 0,
        'calls': ((5855820, 'bl', 4724790),),
        'strings': (),
        'pics': ((5855814, 5855832, 6266889),),
        'lits': (),
        'before': 'f2830023b7e70000', 'after': '00bfb145060038b50c001500002810d0',
        'ingress_bl': 2, 'ingress_bw': 0, 'ingress_sha256': '669078334e308968d041c2c40fc6411cff951a1696dd32e7b515418a6bb008a8',
    },
)

# Raw-scan BL/B.W sites that target a strict unit interior from outside the
# owning unit.  The single entry is a mid-instruction artifact: the bytes at
# 0x005C87E0 are the second half of a 32-bit ``mul`` at 0x005C87DE inside
# corpus function FUN_005c877a, not a real call.  Pinned so the raw scan
# stays fail-closed; documented as an artifact, not semantic ingress.
INTERIOR_ARTIFACTS = ((6064096, 'bl', 5052404),)

# Corpus cross-check pins: per unit (verified count, verified digest,
# unverified count, unverified digest).  Verified sites sit inside a corpus
# function whose decompilation tokens name the unit entry; unverified sites
# lie inside Ghidra's rejected oversized envelopes.
CORPUS_INGRESS_PINS = {
    'bounded_printf_wrapper_a': (115, '0d607b1350c0d8b801c51833209b3c8c9add18d873d2fae0ff498b44392cb25d', 41, '42cf020aa6d3410b5e5469ae2ba05bef99dc3eb6dfc3f3719caed02f6c583c56'),
    'bounded_printf_wrapper_b': (3, 'a24a266bcd2d7e1127033e2a8f1ee88eeecd342ddadf7a93757f38af977ce9ac', 0, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),
    'string_scanf_wrapper': (3, 'e3119ab604299d144f7c9ee74353f482c827b20d339ce8d2bb3148d76ded2667', 4, 'f9a278f25581774ae23b6447970e7b1fbfe85e058aa2a23547127f8fe796bca6'),
    'printf_core': (4, '5c4d0623883e5b1aa07f186af492a362080dc229d0556e25b3bd1e70c982bf31', 0, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),
    'unbounded_printf_wrapper': (65, '1b849b5b11c05d1694abf5a618c6017d85264e4431c04258daab4ed9547a5c66', 10, 'ee8e73367b7fc870d1c48c9b1805c2571bd07b74e8bc91f3f00b28d117bab12e'),
    'scanf_core': (1, '0fa20932fec5a04c1a5ee9b32ca5c745911600bb59558bf5ee8733b119b2816e', 0, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),
    'scanset_matcher': (2, '4bc62cc68aaeb4d058e18d464045e2cf7a537ad04392e8aacf961bbd1f69320b', 0, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),
    'scanf_string_helper': (1, '9d1bd2883ec668326de0d779c50c76721ee86f46488302d99c04eb0d9871024a', 0, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),
    'constraint_dispatcher': (3, '941d53f77fec97d5e68ba672ec0e0ba460f4fecc75499f2f50c84cb0f7377b45', 0, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),
    'strtod_engine': (1, '277ec4201bd1d0ebfee4ef0108a4b904898a906e3a7578a503c8a13b06720207', 0, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),
    'hexfloat_scanner': (1, 'e9ebff15a48de9645dcfb5fe14014edfb26807a64986a8915b0e0b2521be17d0', 1, '6ce90fb5e2db70b571cccc3a413fa357c06b46c438042e6c09631238313d1019'),
    'default_output_printf_wrapper': (2, '669078334e308968d041c2c40fc6411cff951a1696dd32e7b515418a6bb008a8', 0, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),
}

# Audit conclusions per unit: role within the cluster, provider decision,
# and the condition a clean-room candidate must satisfy before production
# admission.  Decisions follow the bounded IAR runtime precedent (all 13
# previously censused runtime units were clean-room recreated and
# production-redirected) and the in-cluster scan_string.c adapter.
UNIT_DISPOSITIONS = {
    'bounded_printf_wrapper_a': {
        'role': 'vsnprintf-family bounded output wrapper (four-word state)',
        'decision': 'clean-room-recreate',
        'condition': 'candidate must ship the bounded writer callback at '
            '0x00439C8A (state {cursor, remaining, would_be_count}), return '
            'the would-be count on success and the negative core status on '
            'constraint, and pass Unicorn differential qualification against '
            'the stock 62-byte body per the memory/math precedent',
    },
    'bounded_printf_wrapper_b': {
        'role': 'vsnprintf-family bounded output wrapper (three-word state)',
        'decision': 'clean-room-recreate',
        'condition': 'same writer callback and contract as wrapper A; only '
            'the va_list hand-off stack layout differs',
    },
    'string_scanf_wrapper': {
        'role': 'vsscanf-family string-input wrapper',
        'decision': 'recreated-production',
        'condition': 'already clean-room recreated and production-redirected '
            'by components/apollo_main/core_overlay/scan_string.c (patch site '
            'replace_scan_string); stock body carries zero official opaque '
            'bytes in the census',
    },
    'printf_core': {
        'role': 'DLIB printf formatter core (callback + state engine)',
        'decision': 'licensed-retention',
        'condition': 'recreation is gated on bounding the DLIB helper sea it '
            'calls inside the rejected oversized envelopes (0x0048262C/'
            '0x00482684/0x00482518 and the 0x004D41xx/0x004D43xx float and '
            'locale helpers); ingress is fully enumerated (the four '
            'wrappers) so retention is a bounded boundary',
    },
    'unbounded_printf_wrapper': {
        'role': 'vsprintf-family unbounded output wrapper',
        'decision': 'clean-room-recreate',
        'condition': 'candidate must ship the unbounded writer callback at '
            '0x004397C6 (write byte, advance cursor) and return cursor minus '
            'base on success',
    },
    'scanf_core': {
        'role': 'DLIB scanf scanner core (reader callback + state engine)',
        'decision': 'licensed-retention',
        'condition': 'sole stock caller is the already-redirected string '
            'wrapper; production reaches it only through the first-party '
            'open_cfw_scan_string adapter; recreation is gated on the same '
            'helper-sea bounding as the printf core',
    },
    'scanset_matcher': {
        'role': '%[...] scanset membership matcher with a-b range support',
        'decision': 'clean-room-recreate',
        'condition': 'pure leaf (no calls, no literals); candidate must '
            'reproduce the range-triple walk and both exit codes',
    },
    'scanf_string_helper': {
        'role': 'Annex-K aware %s/%c/%[ string-conversion helper',
        'decision': 'clean-room-recreate',
        'condition': 'conditional on clean-room strchr (0x00481818), memchr '
            '(0x004D40E0) and ctype (0x004D58AE) leaves, which currently sit '
            'inside rejected oversized envelopes',
    },
    'constraint_dispatcher': {
        'role': 'Annex-K constraint-handler dispatcher',
        'decision': 'clean-room-recreate',
        'condition': 'dispatch through the SRAM handler cell 0x20074F10 '
            '(four bytes below the bounded-census errno word 0x20074F14), '
            'fall back to the retained default handler at 0x00541B74, '
            'return 34',
    },
    'strtod_engine': {
        'role': 'strtod-family binary64 parse engine',
        'decision': 'licensed-retention',
        'condition': 'decimal/hex classification and combination helpers '
            '(0x00585134/0x00585258/0x00542A80/0x004D4208) sit inside '
            'rejected oversized envelopes; exact binary64 rounding makes '
            'the qualification burden match the format cores',
    },
    'hexfloat_scanner': {
        'role': 'hexadecimal mantissa/exponent scanner (%a, strtod hex path)',
        'decision': 'clean-room-recreate',
        'condition': 'conditional on clean-room memchr and locale '
            'decimal-point (0x004D43A8) leaves; candidate must reproduce the '
            '7-hexit grouping, rounding nibble, and 100000000 exponent cap',
    },
    'default_output_printf_wrapper': {
        'role': 'vprintf-family default-output wrapper',
        'decision': 'clean-room-recreate',
        'condition': 'conditional on the retained stream-writer boundary '
            '(callback at 0x005FA008 forwarding to 0x005F9FA4 in the '
            'low-level I/O sea); the wrapper itself is a 15-instruction shim',
    },
}

FUNCTION_BEGIN_RE = re.compile(
    r"OPENCFW_FUNCTION_BEGIN entry=([0-9a-f]+) "
    r"body_start=([0-9a-f]+) body_end=([0-9a-f]+) name=(\S+)",
    re.IGNORECASE,
)
FUNCTION_END_RE = re.compile(r"OPENCFW_FUNCTION_END entry=([0-9a-f]+)", re.IGNORECASE)
ADDRESS_TOKEN_RE = re.compile(r"(?<![0-9a-fA-F])([0-9a-f]{8})(?![0-9a-fA-F])")
IMM_RE = r"#(-?(?:0x[0-9a-f]+|\d+))"


class AuditError(RuntimeError):
    """Raised when an authenticated formatted-I/O cluster invariant changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def wide_branch_target(address: int, first: int, second: int, *, link: bool) -> int | None:
    expected = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    immediate = (
        sign << 24
        | (1 ^ (j1 ^ sign)) << 23
        | (1 ^ (j2 ^ sign)) << 22
        | (first & 0x03FF) << 12
        | (second & 0x07FF) << 1
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def scan_wide_branches(blob: bytes) -> list[tuple[int, str, int]]:
    """Every (site, kind, target) BL/B.W-shaped word pair in the image."""

    hits = []
    for offset in range(0, len(blob) - 3, 2):
        address = LOAD_BASE + offset
        first, second = struct.unpack_from("<HH", blob, offset)
        for kind, link in (("bl", True), ("bw", False)):
            target = wide_branch_target(address, first, second, link=link)
            if target is not None:
                hits.append((address, kind, target))
    return hits


def _decode_unit(blob: bytes, md: Cs, unit: dict[str, Any]) -> dict[str, Any]:
    """Re-derive a unit's decode census; compared against the pins."""

    start, end, code_end = unit["start"], unit["end"], unit["code_end"]
    instructions = list(md.disasm(image_slice(blob, start, code_end), start))
    if sum(i.size for i in instructions) != code_end - start:
        raise AuditError(f"{unit['name']}: code prefix does not decode cleanly")
    string_addresses = {row[2] for row in SIGNATURE_STRINGS}
    calls: list[tuple[int, str, int]] = []
    strings: list[tuple[int, str, int]] = []
    pics: list[tuple[int, int, int]] = []
    lits: list[tuple[int, int, int]] = []
    blx = 0
    for index, ins in enumerate(instructions):
        if ins.mnemonic == "bl":
            target = wide_branch_target(
                ins.address, *struct.unpack_from("<HH", blob, ins.address - LOAD_BASE), link=True
            )
            if not (start <= target < end):
                calls.append((ins.address, "bl", target))
        elif ins.mnemonic == "b.w":
            target = wide_branch_target(
                ins.address, *struct.unpack_from("<HH", blob, ins.address - LOAD_BASE), link=False
            )
            if not (start <= target < end):
                calls.append((ins.address, "b.w", target))
        elif ins.mnemonic.startswith("blx"):
            blx += 1
        elif ins.mnemonic == "adr" or (
            ins.mnemonic in ("addw", "subw") and "pc" in ins.op_str
        ):
            match = re.search(IMM_RE + r"$", ins.op_str)
            if match is None:
                raise AuditError(f"{unit['name']}: unparseable PC materialization at 0x{ins.address:08X}")
            immediate = int(match.group(1), 0)
            base = (ins.address + 4) & ~3
            target = base - immediate if ins.mnemonic == "subw" else base + immediate
            if target in string_addresses or (target - 1) in string_addresses:
                strings.append((ins.address, ins.mnemonic, target))
        elif ins.mnemonic.startswith("ldr") and "[pc" in ins.op_str:
            match = re.search(IMM_RE + r"\]", ins.op_str)
            if match is None:
                raise AuditError(f"{unit['name']}: unparseable literal load at 0x{ins.address:08X}")
            cell = ((ins.address + 4) & ~3) + int(match.group(1), 0)
            value = struct.unpack_from("<I", blob, cell - LOAD_BASE)[0]
            following = instructions[index + 1] if index + 1 < len(instructions) else None
            if (
                following is not None
                and following.mnemonic in ("add", "add.w", "adds")
                and following.op_str.endswith("pc")
            ):
                resolved = (cell + struct.unpack_from("<i", blob, cell - LOAD_BASE)[0]) & 0xFFFF_FFFF
                pics.append((ins.address, cell, resolved))
            else:
                lits.append((ins.address, cell, value))
    return {
        "instructions": len(instructions),
        "blx_sites": blx,
        "calls": tuple(calls),
        "strings": tuple(strings),
        "pics": tuple(pics),
        "lits": tuple(lits),
    }


def _check_corpus(corpus_root: Path, ingress: dict[str, list[int]]) -> dict[str, Any]:
    sums = corpus_root / "SHA256SUMS"
    if not sums.is_file():
        raise AuditError(f"corpus SHA256SUMS missing: {corpus_root}")
    if sha256(sums.read_bytes()) not in ACCEPTED_CORPUS_SHA256SUMS_SHA256:
        raise AuditError("Ghidra corpus SHA256SUMS identity changed")
    logs = sorted(corpus_root.glob("logs/apollo-*.log"))
    if len(logs) != EXPECTED_LOG_COUNT:
        raise AuditError(f"expected {EXPECTED_LOG_COUNT} corpus logs, found {len(logs)}")

    functions = []
    current = None
    for log in logs:
        for line in log.read_text(encoding="utf-8", errors="strict").splitlines():
            begin = FUNCTION_BEGIN_RE.search(line)
            if begin:
                entry, body_start, body_end = (int(value, 16) for value in begin.groups()[:3])
                current = {
                    "entry": entry,
                    "body_start": body_start,
                    "body_end": body_end,
                    "name": begin.group(4),
                    "tokens": set(),
                }
                functions.append(current)
                continue
            if FUNCTION_END_RE.search(line):
                current = None
                continue
            if current is not None:
                current["tokens"].update(
                    int(token, 16) for token in ADDRESS_TOKEN_RE.findall(line)
                )

    per_unit = {}
    for unit in EXPECTED_UNITS:
        name, start, end = unit["name"], unit["start"], unit["end"]
        envelopes = [f for f in functions if f["entry"] == start]
        if len(envelopes) != 1:
            raise AuditError(f"{name}: corpus envelope census changed")
        envelope = envelopes[0]
        if (envelope["body_start"], envelope["body_end"]) != (start, end - 1):
            raise AuditError(f"{name}: corpus envelope span changed")
        if not envelope["name"].startswith("FUN_"):
            raise AuditError(f"{name}: corpus name changed: {envelope['name']}")
        verified = sorted(
            site
            for site in ingress[name]
            if any(
                f["body_start"] <= site <= f["body_end"] and start in f["tokens"]
                for f in functions
            )
        )
        unverified = sorted(set(ingress[name]) - set(verified))
        observed = (
            len(verified),
            sha256(b"".join(site.to_bytes(4, "little") for site in verified)),
            len(unverified),
            sha256(b"".join(site.to_bytes(4, "little") for site in unverified)),
        )
        if observed != CORPUS_INGRESS_PINS[name]:
            raise AuditError(f"{name}: corpus ingress verification changed: {observed!r}")
        per_unit[name] = {
            "corpus_envelope": f"0x{start:08X}-0x{end:08X}",
            "verified_callers": observed[0],
            "unverified_sites": observed[2],
        }
    return per_unit


def analyze(
    image: Path = DEFAULT_IMAGE,
    corpus_root: Path | None = None,
    census_tsv: Path = DEFAULT_CENSUS_TSV,
) -> dict[str, Any]:
    blob = image.read_bytes()
    if len(blob) != IMAGE_SIZE or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official Apollo-main image identity mismatch")

    # Signature strings: exactly one occurrence each, at the pinned address.
    string_records = []
    for key, text, address, digest in SIGNATURE_STRINGS:
        needle = text.encode("ascii") + b"\x00"
        if sha256(needle) != digest:
            raise AuditError(f"signature string pin corrupt: {key}")
        occurrences = []
        cursor = 0
        while True:
            offset = blob.find(needle, cursor)
            if offset < 0:
                break
            occurrences.append(LOAD_BASE + offset)
            cursor = offset + 1
        if occurrences != [address]:
            raise AuditError(
                f"signature string {key} location changed: "
                + ", ".join(f"0x{item:08X}" for item in occurrences)
            )
        string_records.append({"key": key, "address": address, "text": text})

    # Adjacent evidence spans.
    evidence_records = []
    for name, start, end, digest in EVIDENCE_SPANS:
        body = image_slice(blob, start, end)
        if sha256(body) != digest:
            raise AuditError(f"evidence span changed: {name}")
        evidence_records.append(
            {"name": name, "start": start, "end": end, "size": len(body), "sha256": digest}
        )

    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    branches = scan_wide_branches(blob)
    entries = {unit["start"] for unit in EXPECTED_UNITS}
    interiors = set()
    for unit in EXPECTED_UNITS:
        interiors.update(range(unit["start"] + 2, unit["end"], 2))

    ingress_sites: dict[str, list[int]] = {unit["name"]: [] for unit in EXPECTED_UNITS}
    interior_artifacts = []
    for site, kind, target in branches:
        if target in entries:
            name = next(u["name"] for u in EXPECTED_UNITS if u["start"] == target)
            ingress_sites[name].append(site)
        elif target in interiors:
            owner = next(u for u in EXPECTED_UNITS if u["start"] < target < u["end"])
            if not (owner["start"] <= site < owner["end"]):
                interior_artifacts.append((site, kind, target))
    if tuple(sorted(interior_artifacts)) != INTERIOR_ARTIFACTS:
        raise AuditError(f"interior branch census changed: {sorted(interior_artifacts)!r}")

    # Stored-pointer scan: no image word may name a unit entry or its Thumb
    # function-pointer form.
    for unit in EXPECTED_UNITS:
        for probe in (unit["start"], unit["start"] | 1):
            needle = struct.pack("<I", probe)
            if blob.find(needle) >= 0:
                raise AuditError(
                    f"stored pointer to {unit['name']} at "
                    f"0x{LOAD_BASE + blob.find(needle):08X}"
                )

    # Census cross-pin: the twelve iar-dlib rows of the unanchored census
    # must keep their exact spans, bucket, and evidence class.
    census_lines = [
        line
        for line in census_tsv.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    census_rows = {
        int(row["entry"], 16): row
        for row in csv.DictReader(census_lines, delimiter="\t")
        if row.get("bucket") == "iar-dlib"
    }
    if sorted(census_rows) != sorted(entries):
        raise AuditError("unanchored census iar-dlib bucket membership changed")

    unit_records = []
    for unit in EXPECTED_UNITS:
        name, start, end = unit["name"], unit["start"], unit["end"]
        body = image_slice(blob, start, end)
        if sha256(body) != unit["sha256"]:
            raise AuditError(f"{name}: body changed")
        observed = _decode_unit(blob, md, unit)
        for field in ("instructions", "blx_sites", "calls", "strings", "pics", "lits"):
            if observed[field] != unit[field]:
                raise AuditError(f"{name}: {field} census changed")
        if unit["code_end"] != end:
            window = image_slice(blob, unit["code_end"], end)
            if sha256(window) != unit["data_window_sha256"]:
                raise AuditError(f"{name}: inline data window changed")
        if image_slice(blob, start - 8, start).hex() != unit["before"]:
            raise AuditError(f"{name}: leading boundary context changed")
        if image_slice(blob, end, end + 16).hex() != unit["after"]:
            raise AuditError(f"{name}: trailing boundary context changed")

        sites = sorted(ingress_sites[name])
        bl = [site for site, kind, _ in branches if kind == "bl" and target == start]
        bw = [site for site, kind, _ in branches if kind == "bw" and target == start]
        ingress_digest = sha256(b"".join(site.to_bytes(4, "little") for site in sites))
        if (len(bl), len(bw)) != (unit["ingress_bl"], unit["ingress_bw"]):
            raise AuditError(f"{name}: ingress count changed")
        if ingress_digest != unit["ingress_sha256"]:
            raise AuditError(f"{name}: ingress topology changed")

        row = census_rows[start]
        if (
            int(row["body_start"], 16),
            int(row["body_end_exclusive"], 16),
            row["evidence"],
        ) != (start, end, row["evidence"]) or (start, end) != (
            int(row["body_start"], 16),
            int(row["body_end_exclusive"], 16),
        ):
            raise AuditError(f"{name}: census span changed")

        disposition = UNIT_DISPOSITIONS[name]
        unit_records.append(
            {
                "name": name,
                "start": start,
                "end_exclusive": end,
                "bytes": end - start,
                "sha256": unit["sha256"],
                "code_bytes": unit["code_end"] - start,
                "data_bytes": end - unit["code_end"],
                "instructions": unit["instructions"],
                "blx_sites": unit["blx_sites"],
                "external_calls": [
                    {"site": site, "kind": kind, "target": target}
                    for site, kind, target in unit["calls"]
                ],
                "string_materializations": [
                    {"site": site, "mnemonic": mnemonic, "target": target}
                    for site, mnemonic, target in unit["strings"]
                ],
                "pic_references": [
                    {"ldr_site": site, "cell": cell, "target": target}
                    for site, cell, target in unit["pics"]
                ],
                "ingress_bl": unit["ingress_bl"],
                "ingress_bw": unit["ingress_bw"],
                "ingress_sha256": unit["ingress_sha256"],
                "census_evidence": row["evidence"],
                "census_confidence": row["confidence"],
                "role": disposition["role"],
                "provider_decision": disposition["decision"],
                "candidate_condition": disposition["condition"],
            }
        )

    corpus_report = None
    if corpus_root is not None:
        corpus_report = _check_corpus(corpus_root, ingress_sites)

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; no signing, flashing, erase, or hardware operation",
        "target": "official G2 s200_v2.2.6.10 Apollo main",
        "identity": {
            "image_sha256": IMAGE_SHA256,
            "provider": "IAR DLIB formatted-I/O runtime (EWARM 9.20+ candidate)",
            "evidence": "Annex-K printf_s/scanf_s/constraint-handler diagnostic "
            "strings plus the IAR self-relative PIC ldr/add-pc idiom",
        },
        "signature_strings": string_records,
        "evidence_spans": evidence_records,
        "interior_branch_artifacts": [
            {"site": site, "kind": kind, "target": target}
            for site, kind, target in INTERIOR_ARTIFACTS
        ],
        "units": unit_records,
        "corpus": corpus_report,
        "reconciliation": {
            "units": len(unit_records),
            "envelope_bytes": sum(record["bytes"] for record in unit_records),
            "ingress_sites": sum(
                record["ingress_bl"] + record["ingress_bw"] for record in unit_records
            ),
            "provider_decisions": {
                decision: sum(
                    1 for record in unit_records if record["provider_decision"] == decision
                )
                for decision in sorted(
                    {record["provider_decision"] for record in unit_records}
                )
            },
        },
    }


MAP_TSV_HEADER = (
    "unit\trole\tstock_start\tstock_end_exclusive\tstock_bytes\tcode_bytes\t"
    "data_bytes\tstock_sha256\tinstructions\tblx_sites\tingress_bl\tingress_bw\t"
    "ingress_sha256\tstring_refs\tprovider_decision"
)


def map_tsv(report: dict[str, Any]) -> str:
    key_by_address = {row[2]: key for key, _text, address, _digest in (
        (k, t, a, d) for k, t, a, d in SIGNATURE_STRINGS
    )}
    lines = [
        "# G2 IAR DLIB formatted-I/O bounded audit; regenerated by "
        "tools/analyze_g2_iar_dlib_format_io.py",
        MAP_TSV_HEADER,
    ]
    for record in report["units"]:
        counts: dict[str, int] = {}
        for item in record["string_materializations"]:
            target = item["target"]
            key = key_by_address.get(target) or key_by_address.get(target - 1)
            if key is None:
                raise AuditError(
                    f"{record['name']}: unmapped string target 0x{target:08X}"
                )
            counts[key] = counts.get(key, 0) + 1
        for item in record["pic_references"]:
            key = key_by_address.get(item["target"])
            if key is not None:
                counts[key] = counts.get(key, 0) + 1
        refs = "|".join(f"{key}={counts[key]}" for key in sorted(counts)) or "-"
        lines.append(
            "\t".join(
                (
                    record["name"],
                    record["role"],
                    f"0x{record['start']:08X}",
                    f"0x{record['end_exclusive']:08X}",
                    str(record["bytes"]),
                    str(record["code_bytes"]),
                    str(record["data_bytes"]),
                    record["sha256"],
                    str(record["instructions"]),
                    str(record["blx_sites"]),
                    str(record["ingress_bl"]),
                    str(record["ingress_bw"]),
                    record["ingress_sha256"],
                    refs,
                    record["provider_decision"],
                )
            )
        )
    return "\n".join(lines) + "\n"


def _text(report: dict[str, Any]) -> str:
    lines = ["G2 IAR DLIB formatted-I/O bounded audit: PASS"]
    for record in report["units"]:
        lines.append(
            f"  {record['name']}: [0x{record['start']:08X},0x{record['end_exclusive']:08X}) "
            f"{record['bytes']}B ingress bl={record['ingress_bl']} bw={record['ingress_bw']} "
            f"-> {record['provider_decision']}"
        )
    recon = report["reconciliation"]
    lines.append(
        f"  units={recon['units']} envelope_bytes={recon['envelope_bytes']} "
        f"ingress_sites={recon['ingress_sites']} decisions={recon['provider_decisions']}"
    )
    lines.append("hardware/flash operations: none")
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--ghidra-corpus", type=Path, default=None)
    parser.add_argument("--census-tsv", type=Path, default=DEFAULT_CENSUS_TSV)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--write-manifest",
        type=Path,
        metavar="DIRECTORY",
        help="write g2-iar-dlib-format-io-map.tsv into DIRECTORY",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = analyze(args.image, corpus_root=args.ghidra_corpus, census_tsv=args.census_tsv)
    if args.write_manifest is not None:
        args.write_manifest.mkdir(parents=True, exist_ok=True)
        (args.write_manifest / "g2-iar-dlib-format-io-map.tsv").write_text(
            map_tsv(report), encoding="utf-8"
        )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_text(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
