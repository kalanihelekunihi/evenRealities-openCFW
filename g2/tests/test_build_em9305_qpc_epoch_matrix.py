#!/usr/bin/env python3
"""Guard deterministic helpers for the EM9305 QP/C source-epoch builder."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
BUILDER = TOOLS / "build_em9305_qpc_epoch_matrix.py"


def load_builder():
    sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location("build_em9305_qpc_epoch_matrix", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Em9305QpcEpochMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()

    def test_matrix_is_eight_modules_across_ten_epochs(self) -> None:
        self.assertEqual(len(self.builder.MODULE_SOURCES), 8)
        self.assertEqual(len(self.builder.SOURCE_EPOCH_TAG_GROUPS), 10)
        self.assertEqual(self.builder.COMMON_FLAGS[0], "-mcpu=em")
        self.assertEqual(len(self.builder.STOCK_COMPATIBLE_SOURCE_EPOCH_TAG_GROUPS), 6)
        self.assertEqual(len(self.builder.STOCK_COMPATIBLE_SOURCE_TAGS), 7)

    def test_port_configuration_is_rewritten_fail_closed(self) -> None:
        source = """\
#define QF_MAX_ACTIVE 64
#define QF_MAX_EPOOL 3
#define QF_EVENT_SIZ_SIZE 4
#define QF_EQUEUE_CTR_SIZE 2
#define QF_MPOOL_SIZ_SIZE 4
#define QF_MPOOL_CTR_SIZE 4
"""
        observed = self.builder.patch_port_configuration(source)
        for expected in (
            "QF_MAX_ACTIVE 16",
            "QF_MAX_EPOOL 2",
            "QF_EVENT_SIZ_SIZE 2",
            "QF_EQUEUE_CTR_SIZE 1",
            "QF_MPOOL_SIZ_SIZE 2",
            "QF_MPOOL_CTR_SIZE 2",
        ):
            self.assertIn(expected, observed)
        with self.assertRaises(self.builder.BuildError):
            self.builder.patch_port_configuration(source.replace("QF_MAX_ACTIVE", "MISSING"))

    def test_objdump_normalization_removes_addresses_not_semantics(self) -> None:
        source = """\
sample.o: file format elf32-littlearc

00000000 <QF_add_>:
   0: 7104 add_s r0,r0,1
   2: R_ARC_32 qf_act
"""
        observed = self.builder.normalize_objdump(source)
        self.assertNotIn("00000000", observed)
        self.assertNotIn("file format", observed)
        self.assertIn("<FUNCTION>", observed)
        self.assertIn("R_ARC_32 qf_act", observed)


if __name__ == "__main__":
    unittest.main()
