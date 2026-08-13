import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools" / "run_ghidra_shard_batch.sh"
SCRIPTS = (
    "DisassembleArcompactRange.java",
    "DumpInstructionsAround.java",
    "CreateAndDumpFunctions.java",
)


class GhidraShardBatchTests(unittest.TestCase):
    def make_fixture(self, root: Path):
        firmware = root / "firmware.bin"
        firmware.write_bytes(b"stock")
        manifest = root / "manifest.tsv"
        manifest.write_text(
            "# shard_id\tentry\tstart\tend-exclusive\n"
            "one\t0x1000\t0x1000\t0x1010\n"
            "two\t0x1020\t0x1020\t0x1030\n"
        )
        scripts = root / "scripts"
        scripts.mkdir()
        for name in SCRIPTS:
            (scripts / name).write_text(f"// {name}\n")
        headless = root / "analyzeHeadless"
        headless.write_text("#!/bin/sh\nexit 0\n")
        headless.chmod(0o755)
        return firmware, manifest, scripts, headless

    def runner_env(self, root: Path):
        firmware, manifest, scripts, headless = self.make_fixture(root)
        env = dict(os.environ)
        env.update(
            GHIDRA_HEADLESS=str(headless),
            JAVA_HOME=str(root / "jdk"),
            FIRMWARE=str(firmware),
            MANIFEST=str(manifest),
            GHIDRA_SCRIPT_DIR=str(scripts),
            OUTPUT_DIR=str(root / "output"),
            JOBS="2",
        )
        return env

    def test_targeted_run_records_runner_and_configuration(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            env = self.runner_env(root)
            subprocess.run([str(RUNNER)], env=env, check=True, capture_output=True)

            output = root / "output"
            config = dict(
                line.split("\t", 1)
                for line in (output / "CONFIG.tsv").read_text().splitlines()
            )
            self.assertEqual(config["jobs"], "2")
            self.assertEqual(config["full_analysis"], "0")

            identities = {
                label: digest
                for digest, label in (
                    line.split("\t", 1)
                    for line in (output / "INPUTS.tsv").read_text().splitlines()
                )
            }
            self.assertEqual(
                identities["runner"], hashlib.sha256(RUNNER.read_bytes()).hexdigest()
            )
            self.assertEqual(
                identities["configuration"],
                hashlib.sha256((output / "CONFIG.tsv").read_bytes()).hexdigest(),
            )
            self.assertEqual(
                set(identities),
                {"runner", "firmware", "manifest", "configuration", *SCRIPTS},
            )

            results = (output / "results.tsv").read_text().splitlines()
            self.assertEqual(len(results), 3)
            self.assertTrue(all(line.split("\t")[4] == "0" for line in results[1:]))
            checksums = (output / "SHA256SUMS").read_text()
            self.assertIn("  CONFIG.tsv\n", checksums)
            self.assertIn("  INPUTS.tsv\n", checksums)
            self.assertIn("  results.tsv\n", checksums)

    def test_rejects_unknown_analysis_mode(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            env = self.runner_env(root)
            env["FULL_ANALYSIS"] = "sometimes"
            result = subprocess.run([str(RUNNER)], env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("FULL_ANALYSIS must be", result.stderr)


if __name__ == "__main__":
    unittest.main()
