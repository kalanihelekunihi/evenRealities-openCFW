# SPDX-License-Identifier: MIT
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


G2_ROOT = Path(__file__).resolve().parents[1]
TOOL = G2_ROOT / "tools/integrate_g2_pt_protocol_provider.py"
MANIFEST = G2_ROOT / "manifests/g2-2.2.6.10-core-source.json"
CONFIG = G2_ROOT / "components/apollo_main/core_overlay/overlay.json"
SPEC = importlib.util.spec_from_file_location(
    "retired_g2_pt_protocol_integrator_test", TOOL
)
assert SPEC is not None and SPEC.loader is not None
INTEGRATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INTEGRATOR)


class RetiredPTProtocolIntegratorTests(unittest.TestCase):
    def test_historical_logic_preserves_the_mixed_license_contract(self) -> None:
        provider = json.loads(CONFIG.read_text(encoding="utf-8"))[
            "post_link_providers"
        ]["pt_protocol"]
        INTEGRATOR._validate_pt_license_contract(provider)
        self.assertEqual(provider["license"], "MIT AND Apache-2.0")
        source = TOOL.read_text(encoding="utf-8")
        self.assertNotIn("Compiled MIT G2 PT provider section", source)
        self.assertIn(
            "Compiled MIT AND Apache-2.0 aggregate G2 PT provider section",
            source,
        )

        mutations = []
        changed = copy.deepcopy(provider)
        changed["license"] = "MIT"
        mutations.append(changed)
        changed = copy.deepcopy(provider)
        changed["sources"][-1]["license"] = "Apache-2.0"
        mutations.append(changed)
        changed = copy.deepcopy(provider)
        changed["sources"][:2] = reversed(changed["sources"][:2])
        mutations.append(changed)
        for index, changed in enumerate(mutations):
            with self.subTest(mutation=index), self.assertRaises(
                INTEGRATOR.IntegrationError
            ):
                INTEGRATOR._validate_pt_license_contract(changed)

    def test_legacy_apply_and_verify_are_fail_closed_and_non_mutating(self) -> None:
        before = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
        for mode in ("apply", "verify"):
            with self.subTest(mode=mode):
                result = subprocess.run(
                    [sys.executable, str(TOOL), mode],
                    cwd=G2_ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("legacy single-report PT integration is retired", result.stdout)
                self.assertIn("apply_g2_canonical_observations.py", result.stdout)
        self.assertEqual(hashlib.sha256(MANIFEST.read_bytes()).hexdigest(), before)


if __name__ == "__main__":
    unittest.main()
