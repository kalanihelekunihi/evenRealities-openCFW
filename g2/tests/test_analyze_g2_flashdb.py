#!/usr/bin/env python3
"""Guard the read-only FlashDB 2.1.1 identity/configuration audit."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_flashdb.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_flashdb", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FlashDbAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.data = cls.analyzer._load()

    def test_identity_and_config_are_pinned(self) -> None:
        f = self.analyzer.audit(self.data)
        self.assertEqual(f["version"], "2.1.1")
        self.assertTrue(f["retained_kvdb_only"])
        self.assertEqual(
            f["feature_evidence"],
            {
                "retained_tsdb_subsystem": False,
                "tsdb_macro_state": "not statically proven",
                "minimal_recovered_config_uses_tsdb": False,
            },
        )
        self.assertTrue(f["stock_init_path"])
        self.assertEqual(f["databases"], ["sysenv", "factory"])
        self.assertEqual(
            f["database_bindings"],
            [
                {"index": 0, "database_name": "sysenv", "partition_name": "kvdb"},
                {"index": 1, "database_name": "factory", "partition_name": "NVdb"},
            ],
        )
        self.assertEqual(f["partition_table_anchor"], "01PEkvdb")
        self.assertEqual(
            f["binding_literal_pointers"],
            [
                {
                    "index": 0,
                    "role": "database",
                    "pool": 0x004D9AD4,
                    "target": 0x0078E594,
                    "value": "sysenv",
                },
                {
                    "index": 0,
                    "role": "partition",
                    "pool": 0x004D9AB8,
                    "target": 0x0078E58C,
                    "value": "kvdb",
                },
                {
                    "index": 1,
                    "role": "database",
                    "pool": 0x005109D0,
                    "target": 0x0078E60C,
                    "value": "factory",
                },
                {
                    "index": 1,
                    "role": "partition",
                    "pool": 0x005109D4,
                    "target": 0x0078E614,
                    "value": "NVdb",
                },
            ],
        )
        self.assertEqual(
            f["partitions"],
            [
                {
                    "name": "kvdb",
                    "flash_name": "norflash",
                    "offset": 0x01FC0000,
                    "length": 0x38000,
                },
                {
                    "name": "NVdb",
                    "flash_name": "norflash",
                    "offset": 0x01FF8000,
                    "length": 0x8000,
                },
            ],
        )
        self.assertEqual(f["fal_device_callback_offsets"], {"read": 0x28, "write": 0x2C, "erase": 0x30})
        self.assertEqual(f["fal_partition_offset_offset"], 0x34)
        self.assertEqual(f["fal_partition_length_offset"], 0x38)
        self.assertEqual(
            f["configuration"],
            {
                "FDB_USING_KVDB": True,
                "FDB_USING_FAL_MODE": True,
                "FDB_USING_FILE_MODE": False,
                "FDB_WRITE_GRAN": 1,
                "sec_size": 0x1000,
                "FDB_KV_CACHE_TABLE_SIZE": 64,
                "FDB_SECTOR_CACHE_TABLE_SIZE": 64,
                "FDB_KV_AUTO_UPDATE": False,
                "FDB_DEBUG_ENABLE": False,
                "compiler_short_enums": True,
            },
        )
        self.assertEqual(f["kv_header_size"], 0x18)
        self.assertEqual(f["db_object_abi"]["base"], 0x2005DFFC)
        self.assertEqual(f["db_object_abi"]["count"], 2)
        self.assertEqual(f["db_object_abi"]["stride"], 0x8AC)
        self.assertEqual(f["db_object_abi"]["kv_cache_table"], 0xA8)
        self.assertEqual(f["db_object_abi"]["sector_cache_table"], 0x2A8)
        self.assertEqual(f["open_config"], [])

    def test_default_tables_and_initialized_values_are_pinned(self) -> None:
        f = self.analyzer.audit(self.data)
        tables = f["default_kv_tables"]
        self.assertEqual([(t["database"], t["address"], t["count"]) for t in tables], [
            ("sysenv", 0x2000372C, 12),
            ("factory", 0x20003868, 9),
        ])
        self.assertEqual(
            [node["key"] for node in tables[0]["nodes"]],
            [
                "kvString", "kvMagic", "kvbooCount", "kvTime", "kvTimeFormat",
                "kvTemperatureUnit", "kvUniversalSetting", "kvSetting",
                "kvOnboardingConfig", "kvRing", "kvTerminalMode", "kvAlsScale",
            ],
        )
        self.assertEqual(
            [node["key"] for node in tables[1]["nodes"]],
            [
                "nvString", "nvMagic", "nvProdMode", "nvSysDt", "nvAdvMagic",
                "nvMAC", "nvSCald", "nvSCaldAG", "nvBuzzer",
            ],
        )
        boot = tables[0]["nodes"][2]
        self.assertEqual(boot["value_address"], 0x20074988)
        self.assertEqual(boot["value_len"], 4)
        self.assertEqual(boot["default_hex"], "00000000")
        self.assertEqual(
            boot["value_provenance"],
            "authenticated reset-called IAR zero scatter over [0x20004558,0x20075048)",
        )
        self.assertEqual(tables[0]["nodes"][1]["default_hex"], "2000005a")
        self.assertEqual(tables[1]["nodes"][1]["default_hex"], "22005555")
        self.assertTrue(all(
            node["storage_kind"] == "explicit-length blob"
            for table in tables for node in table["nodes"]
        ))

    def test_callbacks_port_and_reset_policy_are_pinned(self) -> None:
        f = self.analyzer.audit(self.data)
        self.assertEqual(
            f["database_callbacks"],
            {
                "mutex_object": 0x20074944,
                "lock": 0x005410DB,
                "unlock": 0x00541127,
                "lock_wait": "forever",
                "per_node_callbacks": "none in FlashDB fdb_default_kv_node ABI",
            },
        )
        port = f["norflash_port"]
        self.assertEqual(port["read"]["driver"], 0x004709C8)
        self.assertEqual(port["write"]["driver"], 0x004708A8)
        self.assertEqual(port["erase"]["driver"], 0x0047075C)
        self.assertEqual(port["erase"]["success"], "4096 after all requested sectors")
        lifecycle = f["first_party_policy"]["boot_count_lifecycle"]
        self.assertEqual(
            lifecycle,
            {
                "key": "kvbooCount",
                "value_address": 0x20074988,
                "startup_default": 0,
                "startup_zero_range": [0x20004558, 0x20075048],
                "runtime": "read persisted word, increment, write persisted word",
            },
        )
        self.assertEqual(len(f["first_party_policy"]["migration_targets"]), 11)
        self.assertFalse(any("kvbooCount" in item for item in f["promotion_blockers"]))
        self.assertIn("checks only negative FAL returns", port["flashdb_error_mapping"])
        self.assertEqual(
            f["first_party_policy"]["set_default_callers"],
            [0x004D990E, 0x0051093C, 0x005452CC],
        )
        self.assertEqual(f["first_party_policy"]["sysenv_magic"]["value"], 0x5A000020)
        self.assertEqual(f["first_party_policy"]["factory_magic"]["value"], 0x55550022)

    def test_mutated_image_is_rejected(self) -> None:
        mutated = bytearray(self.data)
        run = 0x0078D60C  # FDB_SW_VERSION "2.1.1"
        off = run - self.analyzer.LOAD_BASE
        mutated[off] = ord("9")
        with self.assertRaises(self.analyzer.AuditError):
            self.analyzer.audit(bytes(mutated))

    def test_tsdb_marker_would_be_rejected(self) -> None:
        injected = bytes(self.data) + b"[FlashDB][tsdb]\x00"
        with self.assertRaises(self.analyzer.AuditError):
            self.analyzer.audit(injected)

    def test_mutated_configuration_and_fal_records_are_rejected(self) -> None:
        for run in (
            self.analyzer.KVDB_INIT_CACHE_LOOP_RUN,
            self.analyzer.FAL_PARTITION_TABLE + 0x38,
            self.analyzer.FAL_DEVICE + 0x20,
        ):
            with self.subTest(run=f"0x{run:08x}"):
                mutated = bytearray(self.data)
                mutated[run - self.analyzer.LOAD_BASE] ^= 1
                with self.assertRaises(self.analyzer.AuditError):
                    self.analyzer.audit(bytes(mutated))

    def test_mutated_binding_pointers_and_complete_wrappers_are_rejected(self) -> None:
        runs = [
            item[key]
            for item in self.analyzer.DB_BINDING_LITERAL_POINTERS
            for key in ("database_literal_pool", "partition_literal_pool")
        ]
        runs.extend(
            self.analyzer.PINNED_BODIES[name][0]
            for name in (
                "sysenv_init_wrapper",
                "factory_init_wrapper",
                "fal_partition_read_wrapper",
                "fal_partition_write_wrapper",
                "fal_partition_erase_wrapper",
            )
        )
        for run in runs:
            with self.subTest(run=f"0x{run:08x}"):
                mutated = bytearray(self.data)
                mutated[run - self.analyzer.LOAD_BASE] ^= 1
                with self.assertRaises(self.analyzer.AuditError):
                    self.analyzer.audit(bytes(mutated))

    def test_mutated_scatter_port_and_policy_evidence_is_rejected(self) -> None:
        runs = [
            self.analyzer.IAR_SCATTER_RECORD,
            self.analyzer.IAR_SCATTER_STREAM,
            self.analyzer.PINNED_BODIES["sysenv_default_descriptor"][0],
            self.analyzer.PINNED_BODIES["sysenv_default_validator"][0],
            self.analyzer.PINNED_BODIES["factory_default_descriptor"][0],
            self.analyzer.PINNED_BODIES["factory_default_validator"][0],
            self.analyzer.PINNED_BODIES["norflash_read"][0],
            self.analyzer.PINNED_BODIES["norflash_write"][0],
            self.analyzer.PINNED_BODIES["norflash_erase"][0],
            self.analyzer.PINNED_BODIES["flashdb_mutex_init"][0],
            self.analyzer.PINNED_BODIES["flashdb_mutex_lock"][0],
            self.analyzer.PINNED_BODIES["flashdb_mutex_unlock"][0],
            self.analyzer.PINNED_BODIES["flashdb_low_level_read"][0],
            self.analyzer.PINNED_BODIES["flashdb_low_level_erase"][0],
            self.analyzer.PINNED_BODIES["flashdb_low_level_write"][0],
            0x004D9AF4,
            0x005109F0,
        ]
        for run in runs:
            with self.subTest(run=f"0x{run:08x}"):
                mutated = bytearray(self.data)
                mutated[run - self.analyzer.LOAD_BASE] ^= 1
                with self.assertRaises(self.analyzer.AuditError):
                    self.analyzer.audit(bytes(mutated))

    def test_cli_json_is_read_only_and_machine_readable(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["version"], "2.1.1")
        self.assertTrue(payload["retained_kvdb_only"])
        self.assertFalse(payload["feature_evidence"]["retained_tsdb_subsystem"])
        self.assertEqual(
            payload["feature_evidence"]["tsdb_macro_state"],
            "not statically proven",
        )
        self.assertEqual(payload["configuration"]["FDB_WRITE_GRAN"], 1)
        self.assertEqual(payload["configuration"]["sec_size"], 0x1000)


if __name__ == "__main__":
    unittest.main()
