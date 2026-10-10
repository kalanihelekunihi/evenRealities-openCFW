#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

here = Path(__file__).resolve().parent
root = next(p for p in here.parents if (p / "g2/workflow/state.json").exists())
e = json.loads((here / "evidence.json").read_text())
c = e["counts"]
assert e["inputs"]["stock_sha256"] == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
assert e["inputs"]["elf_sha256"] == "36c9b79de3b961d36ad343a1402a112298603111cbe1d5875e1b471694159d1a"
assert hashlib.sha256((root / e["inputs"]["stock"]).read_bytes()).hexdigest() == e["inputs"]["stock_sha256"]
assert hashlib.sha256((root / e["inputs"]["elf"]).read_bytes()).hexdigest() == e["inputs"]["elf_sha256"]
assert c["missing_body_calls"] == c["missing_from_capped_owners"]
assert c["missing_from_uncapped_owners"] == 0
assert c["extra_calls"] == c["extra_explained_by_native_gap"] + c["extra_unexplained"]
assert c["native_body_calls"] == c["validated_body_calls_present"] + c["missing_body_calls"]
assert json.loads((root / "g2/workflow/state.json").read_text())["phase"] == "P2_EXECUTING"
print("verified", c)
