"""Focused adversarial tests for the P1 inventory validator."""
from __future__ import annotations

import hashlib
import json
import pathlib
import struct
import tempfile
import unittest

from g2.workflow.tools import validate_inventory_v2 as validator


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class InventoryValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.old_root = validator.ROOT
        validator.ROOT = self.root
        self.addCleanup(setattr, validator, "ROOT", self.old_root)
        self.campaign_id = "synthetic"
        self.version = "fixture"
        self.campaign = self.root / "g2/build/pseudocode-first" / self.campaign_id
        (self.campaign / "inventory").mkdir(parents=True)
        target_dir = self.root / "g2/workflow"
        target_dir.mkdir(parents=True)
        (self.root / "g2/tools").mkdir(parents=True)
        self.write("g2/tools/open_cfw.py", b"inspected parser fixture")
        self.components = []
        self.payloads = {}
        ids = ("codec", "ble_em9305", "touch", "case", "apollo_bootloader", "apollo_main")
        for index, cid in enumerate(ids):
            if cid == "codec":
                data_buffer = bytearray(range(64))
                struct.pack_into("<4I", data_buffer, 0, 0x1010, 0x2000, 4, 0x1020)
                data = bytes(data_buffer)
            else:
                data = bytes([index + 1, index + 11])
            path = f"payloads/{cid}.bin"
            self.write(path, data)
            self.payloads[cid] = data
            self.components.append({"id": cid, "entry_id": index + 1, "type_id": index + 10,
                                    "storage_type": 3, "package_filename": f"firmware/{cid}.bin",
                                    "local_payload_path": path, "sha256": digest(data), "size": len(data)})
        self.bundle, self.entries = self.make_bundle()
        self.write("bundle.bin", self.bundle)
        self.target = {"schema_version": 1, "target_id": "fixture", "format": "EVENOTA",
                       "version": self.version, "bundle": {"size": len(self.bundle), "sha256": digest(self.bundle),
                       "verified_local_path": "bundle.bin"}, "components": self.components}
        manifest_components = []
        for c in self.components:
            manifest_components.append({"name": c["id"], "entry_id": c["entry_id"], "type_id": c["type_id"],
                "storage_type": c["storage_type"], "package_filename": c["package_filename"],
                "provider": {"size": c["size"], "sha256": c["sha256"]}})
        self.manifest = {"schema_version": 1, "package": {"format": "EVENOTA", "version": self.version,
            "build_date": "2026-01-01", "build_time": "00:00:00", "expected_size": len(self.bundle),
            "expected_sha256": digest(self.bundle)}, "components": manifest_components}
        manifest_path = "g2/manifests/g2-2.2.6.10.json"
        self.write_json(manifest_path, self.manifest)
        self.target["identity_sources"] = [{"path": manifest_path, "sha256": digest((self.root / manifest_path).read_bytes())}]
        self.write_json("g2/workflow/target.json", self.target)
        (self.campaign / "inventory" / "outer-container.json").write_text(json.dumps({
            "schema_version": 1, "campaign_id": self.campaign_id, "artifact_sha256": digest(self.bundle),
            "parser_sha256": digest((self.root / "g2/tools/open_cfw.py").read_bytes()),
            "entry_spans": self.entries, "unaccounted_bytes": 0, "unresolved_facts": []}, sort_keys=True))
        registry = {"campaign_id": self.campaign_id, "status": "authenticated",
                    "reviewers": [{"reviewer_id": "reviewer-b", "status": "authenticated"},
                                  {"reviewer_id": "reviewer-c", "status": "authenticated"}], "review_records": {}}
        self.write_json("g2/build/pseudocode-first/synthetic/inventory/review-registry.json", registry)
        registry_path = "g2/build/pseudocode-first/synthetic/inventory/review-registry.json"
        identity = {"campaign_id": self.campaign_id, "target_id": "fixture", "target_sha256": digest(self.bundle),
                    "target_lock_sha256": digest((target_dir / "target.json").read_bytes()),
                    "bundle": {"path": "bundle.bin", "size": len(self.bundle), "sha256": digest(self.bundle)},
                    "components": {c["id"]: {"size": c["size"], "sha256": c["sha256"]} for c in self.components},
                    "container_validation": {"status": "passed", "receipt_sha256": digest((self.campaign / "inventory/outer-container.json").read_bytes())},
                    "review_registry": {"path": registry_path, "sha256": digest((self.root / registry_path).read_bytes())}}
        self.write_json("g2/build/pseudocode-first/synthetic/identity.json", identity)
        self.evidence = b"reviewed fixture evidence"
        self.evidence_hash = digest(self.evidence)
        self.write("evidence.txt", self.evidence)
        self.images = []
        self.coverage = []
        self.reviews = []
        for c in self.components:
            cid = c["id"]
            self.images.append({"schema_version": 2, "campaign_id": self.campaign_id, "id": f"img-{cid}",
                "payload_id": cid, "parent_image_id": None, "source_span": [0, c["size"]],
                "source_size": c["size"], "source_sha256": c["sha256"], "size": c["size"], "content_sha256": c["sha256"],
                "content_path": c["local_payload_path"], "transform": {"kind": "identity"},
                "mapping_status": "resolved", "container_status": "resolved",
                "architecture": {"name": "fixture-isa", "endianness": "little", "isa_mode": "default"},
                "address_spaces": [{"id": "ram", "mappings": [{"image_start": 0, "image_end": c["size"],
                 "loaded_start": 4096, "loaded_end": 4096 + c["size"]}]}],
                "evidence": [{"path": "evidence.txt", "sha256": self.evidence_hash, "input_sha256": c["sha256"]}],
                "accounting_review_id": f"review-img-{cid}"})
            self._coverage("payload", cid, c["size"], c["sha256"])
            self._coverage("image", f"img-{cid}", c["size"], c["sha256"])
        self._coverage("package", "package", len(self.bundle), digest(self.bundle))
        self.discovery = [{"schema_version": 2, "campaign_id": self.campaign_id, "id": f"disc-{c['id']}",
                           "payload_id": c["id"], "image_ids": [f"img-{c['id']}"], "unresolved": [],
                           "evidence": [{"path": "evidence.txt", "sha256": self.evidence_hash,
                                         "input_sha256": c["sha256"]}], "review_id": f"review-disc-{c['id']}"}
                          for c in self.components]
        plans = [{"payload_id": c["id"], "mapping_status": "resolved", "container_status": "resolved",
                  "architecture": "fixture-isa", "endianness": "little", "isa_mode": "default",
                  "address_spaces": ["ram"], "decoder_support": "planned_with_local_decoder",
                  "evidence": [{"path": "evidence.txt", "sha256": self.evidence_hash,
                                "input_sha256": c["sha256"]}]} for c in self.components]
        self.plan = {"schema_version": 2, "campaign_id": self.campaign_id, "id": "analysis-plan",
                     "target_sha256": digest(self.bundle), "review_id": "review-analysis-plan",
                     "architecture_plans": plans}
        self.decoded = False
        self.write_records()

    def make_bundle(self):
        header_size, toc_at = 128, 64
        toc_end = toc_at + len(self.components) * 16
        pos = toc_end + len(validator.EVENOTA_TRAILER)
        toc = bytearray()
        bodies = []
        entries = []
        for c in self.components:
            payload = self.payloads[c["id"]]
            checksum = validator.crc32c_msb(payload)
            hdr = bytearray(header_size)
            struct.pack_into("<I", hdr, 8, len(payload))
            struct.pack_into("<I", hdr, 12, checksum)
            struct.pack_into("<I", hdr, 0x14, validator.EVENOTA_COMPONENT_MAGIC)
            struct.pack_into("<I", hdr, 0x24, c["type_id"])
            struct.pack_into("<I", hdr, 0x28, c["storage_type"])
            struct.pack_into("<II", hdr, 0x18, 0xFFFFFFFF, 0xFFFFFFFF)
            struct.pack_into("<I", hdr, 0x2C, 0xFFFFFFFF)
            hdr[0x30:0x30 + len(c["package_filename"])] = c["package_filename"].encode()
            size = len(hdr) + len(payload)
            toc.extend(struct.pack("<IIII", c["entry_id"], pos, size, checksum))
            entries.append({"payload_id": c["id"], "package_offset": [pos, pos + size],
                            "package_payload_span": [pos + header_size, pos + size],
                            "payload_local_span": [0, len(payload)], "checksum": checksum})
            bodies.append(bytes(hdr) + payload)
            pos += size
        h = bytearray(toc_at)
        h[:8] = b"EVENOTA\0"
        struct.pack_into("<I", h, 8, len(self.components))
        h[0x10:0x10 + len(b"2026-01-01")] = b"2026-01-01"
        h[0x20:0x20 + len(b"00:00:00")] = b"00:00:00"
        h[0x30:0x30 + len(self.version)] = self.version.encode()
        return bytes(h) + bytes(toc) + validator.EVENOTA_TRAILER + b"".join(bodies), entries

    def write(self, relpath, data):
        path = self.root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def write_json(self, relpath, obj):
        self.write(relpath, json.dumps(obj, sort_keys=True).encode())

    def _coverage(self, scope, ident, size, input_hash):
        row_id = f"cov-{scope}-{ident}"
        self.coverage.append({"schema_version": 2, "campaign_id": self.campaign_id, "id": row_id,
            "scope": {"kind": scope, "id": ident}, "start": 0, "end": size, "kind": "unknown",
            "evidence": [{"path": "evidence.txt", "sha256": self.evidence_hash, "input_sha256": input_hash}],
            "review_id": f"review-{row_id}"})

    def write_records(self):
        inv = self.campaign / "inventory"
        def write_jsonl(name, rows):
            (inv / name).write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
        write_jsonl("images.jsonl", self.images)
        write_jsonl("coverage.jsonl", self.coverage)
        write_jsonl("discovery-reconciliation.jsonl", self.discovery)
        self.write_json("g2/build/pseudocode-first/synthetic/inventory/analysis-plan.json", self.plan)
        self.reviews = []
        def add(review_id, kind, record_id, file_name, record, evidence_refs, source_ref=None,
                reviewed_value=None, extra_refs=None):
            roles = [{"role": "record", "path": f"g2/build/pseudocode-first/synthetic/inventory/{file_name}",
                      "sha256": digest((inv / file_name).read_bytes())}]
            if source_ref:
                roles.append({"role": "source", "path": source_ref[0], "sha256": source_ref[1]})
            for ev in evidence_refs:
                roles.append({"role": "evidence", "path": ev["path"], "sha256": ev["sha256"]})
            roles.extend(extra_refs or [])
            if kind == "image":
                roles.append({"role": "content", "path": record["content_path"], "sha256": record["content_sha256"]})
                if record.get("transform", {}).get("kind") == "decoded":
                    ref = record["transform"]["receipt"]
                    roles.append({"role": "transform_receipt", "path": ref["path"], "sha256": ref["sha256"]})
            self.reviews.append({"schema_version": 2, "campaign_id": self.campaign_id, "id": review_id,
                "record_type": kind, "record_id": record_id,
                "record_sha256": validator.canonical_hash(record if reviewed_value is None else reviewed_value,
                    {"review_id", "accounting_review_id"} if reviewed_value is None else set()),
                "author": "worker-a", "reviewer": "reviewer-b",
                "decision": "pass", "input_hashes": roles})
        for image in self.images:
            cid = image["payload_id"]
            add(image["accounting_review_id"], "image", image["id"], "images.jsonl", image, image["evidence"],
                (self.components[[c["id"] for c in self.components].index(cid)]["local_payload_path"], image["source_sha256"]))
            if image.get("mapping_status") == "execution_contract":
                model = image["mapping_model"]
                source_path = (self.components[[c["id"] for c in self.components].index(cid)]["local_payload_path"]
                               if image.get("parent_image_id") is None
                               else next(r["content_path"] for r in self.images if r["id"] == image["parent_image_id"]))
                extra_refs = [
                    {"role": "source", "path": source_path, "sha256": image["source_sha256"]},
                    {"role": "content", "path": image["content_path"], "sha256": image["content_sha256"]},
                ]
                extra_refs.extend({"role": f"execution_contract:{ref['role']}",
                                   "path": ref["path"], "sha256": ref["sha256"]}
                                  for ref in model["evidence"])
                add(model["review_id"], "execution_contract", image["id"], "images.jsonl", image, [],
                    reviewed_value=model, extra_refs=extra_refs)
                self.reviews[-1]["review_scope"] = ["conditional_mapping", "known_route_set",
                                                     "external_premises_scoped"]
            if image.get("transform", {}).get("kind") == "decoded":
                ref = image["transform"]["receipt"]
                receipt = json.loads((self.root / ref["path"]).read_text())
                parent = next(i for i in self.images if i["id"] == image["parent_image_id"])
                handler = next(i for i in self.images if i["id"] == receipt["handler"]["image_id"])
                py_tool, script = receipt["toolchain"]["python"], receipt["toolchain"]["script"]
                execution = receipt["execution"]
                refs = [
                    {"role": "transform_receipt", "path": ref["path"], "sha256": ref["sha256"]},
                    {"role": "source", "path": parent["content_path"], "sha256": parent["content_sha256"]},
                    {"role": "output", "path": image["content_path"], "sha256": image["content_sha256"]},
                    {"role": "descriptor", "path": parent["content_path"], "sha256": parent["content_sha256"]},
                    {"role": "handler", "path": handler["content_path"], "sha256": handler["content_sha256"]},
                    {"role": "tool", "path": py_tool["path"], "sha256": py_tool["sha256"]},
                    {"role": "script", "path": script["path"], "sha256": script["sha256"]},
                    {"role": "stdout", "path": execution["stdout"]["path"], "sha256": execution["stdout"]["sha256"]},
                    {"role": "stderr", "path": execution["stderr"]["path"], "sha256": execution["stderr"]["sha256"]},
                ]
                refs.extend({"role": "library", "path": lib["path"], "sha256": lib["sha256"]}
                            for lib in receipt["toolchain"]["libraries"])
                add(image["transform"]["review_id"], "transform", image["id"], "images.jsonl", image, [],
                    reviewed_value=image["transform"], extra_refs=refs)
        for row in self.coverage:
            scope = row["scope"]
            path = "bundle.bin" if scope["kind"] == "package" else next(c["local_payload_path"] for c in self.components if c["id"] == scope["id"]) if scope["kind"] == "payload" else next(i["content_path"] for i in self.images if i["id"] == scope["id"])
            h = digest((self.root / path).read_bytes())
            add(row["review_id"], "coverage", row["id"], "coverage.jsonl", row, row["evidence"], (path, h))
        for row in self.discovery:
            add(row["review_id"], "discovery", row["id"], "discovery-reconciliation.jsonl", row, row["evidence"])
        add(self.plan["review_id"], "analysis_plan", self.plan["id"], "analysis-plan.json", self.plan,
            [e for p in self.plan["architecture_plans"] for e in p["evidence"]])
        write_jsonl("reviews.jsonl", self.reviews)
        self.refresh_registry()

    def refresh_registry(self):
        registry_path = "g2/build/pseudocode-first/synthetic/inventory/review-registry.json"
        registry_file = self.root / registry_path
        registry = json.loads(registry_file.read_text())
        registry["review_records"] = {r["id"]: validator.canonical_hash(r) for r in self.reviews}
        self.write_json(registry_path, registry)
        self.trusted_registry_hash = digest(registry_file.read_bytes())
        identity_path = self.campaign / "identity.json"
        identity = json.loads(identity_path.read_text())
        identity["review_registry"]["sha256"] = self.trusted_registry_hash
        identity_path.write_text(json.dumps(identity, sort_keys=True))

    def verify(self):
        validator.verify(self.campaign, self.trusted_registry_hash)

    def add_decoded_child(self):
        if self.decoded:
            return
        parent = next(i for i in self.images if i["id"] == "img-codec")
        payload = self.payloads["codec"]
        output = b"abcd"
        self.write("outputs/decoded-codec.bin", output)
        self.write("tools/python", b"python fixture executable")
        self.write("tools/transform.py", b"fixed stock-handler transform fixture")
        self.write("tools/unicorn.py", b"unicorn fixture library")
        self.write("logs/transform.stdout", b"emulation complete\n")
        self.write("logs/transform.stderr", b"")
        child = {"schema_version": 2, "campaign_id": self.campaign_id, "id": "img-decoded-codec",
            "payload_id": "codec", "parent_image_id": "img-codec", "source_span": [16, 24],
            "source_size": 8, "source_sha256": parent["content_sha256"], "size": len(output),
            "content_sha256": digest(output), "content_path": "outputs/decoded-codec.bin",
            "transform": {"kind": "decoded", "recipe_id": "thumb-stock-handler-unicorn-v1",
                "receipt": {"path": "g2/build/pseudocode-first/synthetic/inventory/transform-receipt.json", "sha256": "0" * 64},
                "review_id": "review-transform-img-decoded-codec"},
            "mapping_status": "resolved", "container_status": "resolved",
            "architecture": {"name": "ARM Cortex-M0+", "endianness": "little", "isa_mode": "Thumb"},
            "address_spaces": [{"id": "ram", "mappings": [{"image_start": 0, "image_end": len(output),
                "loaded_start": 0x2000, "loaded_end": 0x2000 + len(output)}]}],
            "evidence": [{"path": "evidence.txt", "sha256": self.evidence_hash,
                "input_sha256": parent["content_sha256"]}], "accounting_review_id": "review-img-decoded-codec"}
        parent["architecture"] = {"name": "ARM Cortex-M0+", "endianness": "little", "isa_mode": "Thumb"}
        self.images.append(child)
        self._coverage("image", child["id"], child["size"], child["content_sha256"])
        next(d for d in self.discovery if d["payload_id"] == "codec")["image_ids"].append(child["id"])
        receipt = {"schema_version": 1, "campaign_id": self.campaign_id,
            "recipe_id": "thumb-stock-handler-unicorn-v1",
            "source": {"parent_image_id": "img-codec", "parent_content_path": parent["content_path"],
                "parent_content_sha256": parent["content_sha256"], "source_span": [16, 24], "source_size": 8,
                "source_span_sha256": digest(payload[16:24])},
            "descriptor": {"image_id": "img-codec", "image_span": [0, 16], "runtime_span": [4096, 4112],
                "bytes_sha256": digest(payload[:16]), "words": [0x1010, 0x2000, 4, 0x1020]},
            "handler": {"image_id": "img-codec", "image_span": [32, 40], "runtime_entry": 0x1020,
                "bytes_sha256": digest(payload[32:40])},
            "output": {"path": child["content_path"], "size": len(output), "sha256": digest(output)},
            "toolchain": {"python": {"path": "tools/python", "sha256": digest(b"python fixture executable"), "version": "3.fixture"},
                "script": {"path": "tools/transform.py", "sha256": digest(b"fixed stock-handler transform fixture")},
                "libraries": [{"name": "unicorn", "version": "fixture", "path": "tools/unicorn.py",
                    "sha256": digest(b"unicorn fixture library")}]},
            "execution": {"argv": ["tools/python", "tools/transform.py", "--recipe", "thumb-stock-handler-unicorn-v1",
                "--parent-image", "img-codec", "--source-span", "16:24", "--output", child["content_path"]],
                "exit_code": 0, "stdout": {"path": "logs/transform.stdout", "sha256": digest(b"emulation complete\n")},
                "stderr": {"path": "logs/transform.stderr", "sha256": digest(b"")}}}
        receipt_path = self.root / child["transform"]["receipt"]["path"]
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(receipt, sort_keys=True))
        child["transform"]["receipt"]["sha256"] = digest(receipt_path.read_bytes())
        self.decoded = True
        self.write_records()

    def mutate_transform_receipt(self, mutation):
        child = next(i for i in self.images if i["id"] == "img-decoded-codec")
        ref = child["transform"]["receipt"]
        path = self.root / ref["path"]
        receipt = json.loads(path.read_text())
        mutation(receipt)
        path.write_text(json.dumps(receipt, sort_keys=True))
        ref["sha256"] = digest(path.read_bytes())
        self.write_records()

    def test_valid_inventory_passes(self):
        self.verify()

    def test_initial_plan_accepts_pending_or_omitted_mapping_status_fields(self):
        original = json.loads(json.dumps(self.plan))
        self.plan = json.loads(json.dumps(original))
        for row in self.plan["architecture_plans"]:
            row["mapping_status"] = "pending_recursive_reconciliation"
            row["container_status"] = "bounds_verified_pending_inventory_review"
        self.write_records()
        self.verify()

        self.plan = json.loads(json.dumps(original))
        for row in self.plan["architecture_plans"]:
            row.pop("mapping_status")
            row.pop("container_status")
        self.write_records()
        self.verify()

    def test_initial_plan_statuses_do_not_override_unresolved_image_mapping(self):
        for row in self.plan["architecture_plans"]:
            row["mapping_status"] = "pending_recursive_reconciliation"
            row["container_status"] = "candidate_unreviewed"
        self.images[0]["mapping_status"] = "fixed_candidate"
        self.images[0]["container_status"] = "candidate_unreviewed"
        self.write_records()
        with self.assertRaisesRegex(ValueError, "unresolved mapping facts: img-codec"):
            self.verify()

    def test_analysis_plan_rejects_missing_or_duplicate_payload_rows(self):
        for mutation in ("missing", "duplicate"):
            self.plan = json.loads(json.dumps(self.plan))
            if mutation == "missing":
                self.plan["architecture_plans"].pop()
            else:
                self.plan["architecture_plans"][-1]["payload_id"] = self.plan["architecture_plans"][0]["payload_id"]
            self.write_records()
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, "exactly six payload"):
                self.verify()
            self.plan = json.loads(json.dumps({
                "schema_version": 2, "campaign_id": self.campaign_id, "id": "analysis-plan",
                "target_sha256": digest(self.bundle), "review_id": "review-analysis-plan",
                "architecture_plans": [{"payload_id": c["id"], "mapping_status": "resolved",
                    "container_status": "resolved", "architecture": "fixture-isa", "endianness": "little",
                    "isa_mode": "default", "address_spaces": ["ram"],
                    "decoder_support": "planned_with_local_decoder",
                    "evidence": [{"path": "evidence.txt", "sha256": self.evidence_hash,
                                  "input_sha256": c["sha256"]}]} for c in self.components]}))

    def test_analysis_plan_rejects_bad_decoder_and_evidence(self):
        original = json.loads(json.dumps(self.plan))
        self.plan["architecture_plans"][0]["decoder_support"] = "complete_pseudocode"
        self.write_records()
        with self.assertRaisesRegex(ValueError, "invalid decoder support"):
            self.verify()

        self.plan = json.loads(json.dumps(original))
        self.plan["architecture_plans"][0]["evidence"][0]["sha256"] = "0" * 64
        self.write_records()
        with self.assertRaisesRegex(ValueError, "evidence file missing or hash mismatch"):
            self.verify()

        self.plan = json.loads(json.dumps(original))
        self.plan["architecture_plans"][0]["evidence"][0]["input_sha256"] = "0" * 64
        self.write_records()
        with self.assertRaisesRegex(ValueError, "architecture evidence is not bound to payload"):
            self.verify()

    def test_versioned_outer_receipt_is_hash_bound(self):
        original = self.campaign / "inventory/outer-container.json"
        versioned = self.campaign / "inventory/outer-container-002.json"
        versioned.write_bytes(original.read_bytes())
        identity_path = self.campaign / "identity.json"
        identity = json.loads(identity_path.read_text())
        identity["container_validation"]["receipt_path"] = str(versioned.relative_to(self.root))
        identity_path.write_text(json.dumps(identity))
        original.write_text("Historical receipt preserved separately in a real campaign")
        self.verify()
        versioned.write_text("tampered")
        with self.assertRaisesRegex(ValueError, "outer-container identity receipt"):
            self.verify()

    def test_iar3_signed_relative_and_separate_compressed_output_sizes(self):
        words = [0x00036F2A, 0x2C, 0x40]
        decoded = validator.verify_iar3_mapping(words, 0x75D3E4, 0x79430E, 22, 24,
            0x40, 0x75D3E0, 0xFFCDCD3F, 0x43A11F)
        self.assertEqual(decoded["source_displacement"], 0x36F2A)
        self.assertEqual(decoded["compressed_size"], 22)
        with self.assertRaisesRegex(ValueError, "compressed length"):
            validator.verify_iar3_mapping(words, 0x75D3E4, 0x79430E, 24, 22,
                0x40, 0x75D3E0, 0xFFCDCD3F, 0x43A11F)

    def test_iar3_negative_signed_source_and_mismatch(self):
        decoded = validator.decode_iar3_descriptor([0xFFFFFFF0, 0x2C, 0x40], 0x1000)
        self.assertEqual(decoded["source_displacement"], -16)
        self.assertEqual(decoded["source_runtime"], 0xFF0)
        with self.assertRaisesRegex(ValueError, "signed source offset"):
            validator.verify_iar3_mapping([0xFFFFFFF0, 0x2C, 0x40], 0x1000, 0x1000,
                22, 24, 0x40, 0x0FFC, 0xFFCDCD3F, 0x43A11F)

    def test_iar3_enclosing_table_handler_binding_is_required(self):
        with self.assertRaisesRegex(ValueError, "initialization table"):
            validator.verify_iar3_mapping([0x36F2A, 0x2C, 0x40], 0x75D3E4, 0x79430E,
                22, 24, 0x40, 0x75D3E0, 0xFFCDCD3F, 0x43A120)

    def test_iar3_relocation_flags_are_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "R9 relocation flag"):
            validator.decode_iar3_descriptor([0x36F2A, 0x2D, 0x40], 0x75D3E4)

    def test_iar3_review004_fixed_payload_descriptor_and_handler(self):
        repo = self.old_root
        payload = (repo / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()
        self.assertEqual(digest(payload), validator.APOLLO_MAIN_SHA256)
        image = payload[32:]
        desc_addr, image_base = 0x75D3E4, 0x438000
        desc_offset = desc_addr - image_base
        words = list(struct.unpack_from("<3I", image, desc_offset))
        self.assertEqual(words, [0x36F2A, 0x2C, 0x40])
        dispatch_addr = desc_addr - 4
        dispatch_word = struct.unpack_from("<I", image, dispatch_addr - image_base)[0]
        handler = dispatch_addr + validator.signed_i32(dispatch_word)
        source_runtime = desc_addr + validator.signed_i32(words[0])
        mapping = validator.verify_iar3_mapping(words, desc_addr, source_runtime, 22, 24,
            0x40, dispatch_addr, dispatch_word, handler)
        source_payload_offset = 32 + source_runtime - image_base
        self.assertEqual(mapping["source_runtime"], 0x79430E)
        self.assertEqual(handler, 0x43A11F)
        self.assertEqual([source_payload_offset, source_payload_offset + mapping["compressed_size"]],
                         [0x35C32E, 0x35C344])
        review_path = repo / validator.APOLLO_REVIEW_004_PATH
        self.assertEqual(digest(review_path.read_bytes()), validator.APOLLO_REVIEW_004_SHA256)
        review = json.loads(review_path.read_text())
        self.assertEqual(review["decision"], "pass")

    def test_iar3_fixed_recipe_matches_all_six_authenticated_descriptor_bytes(self):
        repo = self.old_root
        validator.ROOT = repo
        sources = {
            "apollo_main": ("g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin", 32, 0x438000),
            "apollo_bootloader": ("g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin", 0, 0x410000),
        }
        fresh_outputs = {
            ("apollo_main", 0x75D3E4): "g2/build/pseudocode-first/20260930T190500Z/attempts/P1-apollo-itcm-canonical-replay-011/001/decoded-00000040.bin",
            ("apollo_main", 0x75D3F4): "g2/build/pseudocode-first/20260930T190500Z/attempts/P1-apollo-main-canonical-replay-009/001/decoded-20000000.bin",
            ("apollo_main", 0x75D404): "g2/build/pseudocode-first/20260930T190500Z/attempts/P1-apollo-main-canonical-replay-009/001/decoded-20080000.bin",
            ("apollo_bootloader", 0x4330F4): "g2/build/pseudocode-first/20260930T190500Z/attempts/P1-apollo-initialization-transforms-002/002/decoded-0-itcm.bin",
            ("apollo_bootloader", 0x433104): "g2/build/pseudocode-first/20260930T190500Z/attempts/P1-apollo-initialization-transforms-002/002/decoded-1-dtcm.bin",
            ("apollo_bootloader", 0x433114): "g2/build/pseudocode-first/20260930T190500Z/attempts/P1-apollo-initialization-transforms-002/002/decoded-2-ssram.bin",
        }
        for (payload_id, descriptor_runtime), row in validator.IAR3_FIXED_RECORDS.items():
            with self.subTest(payload=payload_id, descriptor=hex(descriptor_runtime)):
                path, origin, runtime_base = sources[payload_id]
                payload = (repo / path).read_bytes()
                image = payload[origin:]
                descriptor_offset = descriptor_runtime - runtime_base
                words = list(struct.unpack_from("<3I", image, descriptor_offset))
                dispatch_offset = descriptor_offset - 4
                dispatch_word = struct.unpack_from("<I", image, dispatch_offset)[0]
                source_runtime = descriptor_runtime + validator.signed_i32(words[0])
                source_offset = source_runtime - runtime_base
                source_payload_span = [origin + source_offset, origin + source_offset + (words[1] >> 1)]
                handler_entry = dispatch_runtime = descriptor_runtime - 4
                handler_entry += validator.signed_i32(dispatch_word)
                handler_offset = (handler_entry & ~1) - runtime_base
                self.assertEqual(words, list(row["words"]))
                self.assertEqual(dispatch_word, row["dispatch_word"])
                self.assertEqual(source_runtime, row["source_runtime"])
                self.assertEqual(source_payload_span, list(row["source_span"]))
                self.assertEqual(digest(image[source_offset:source_offset + (words[1] >> 1)]), row["source_sha256"])
                self.assertEqual(handler_entry, row["handler"])
                self.assertEqual(digest(image[handler_offset:handler_offset + 126]), row["handler_sha256"])
                output = (repo / fresh_outputs[(payload_id, descriptor_runtime)]).read_bytes()
                self.assertEqual(len(output), row["output_size"])
                self.assertEqual(digest(output), row["output_sha256"])
                validator.verify_iar3_review_basis(
                    {"path": row["review"][0], "sha256": row["review"][1]},
                    "20260930T190500Z", "f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa", row)

    def test_iar3_fixed_recipe_rejects_mutated_tuple_and_review_basis(self):
        row = validator.IAR3_FIXED_RECORDS[("apollo_main", 0x75D3F4)]
        args = ("apollo_main", 0x75D3F4, list(row["words"]), row["source_runtime"],
                list(row["source_span"]), row["source_sha256"], row["output_size"],
                row["output_sha256"], row["destination"], 0x75D3F0, row["dispatch_word"],
                row["handler"], row["handler_sha256"], row["handler"] & ~1, 126)
        validator.verify_iar3_fixed_record(*args)
        bad = list(args)
        bad[7] = "0" * 64
        with self.assertRaisesRegex(ValueError, "pinned reviewed mapping"):
            validator.verify_iar3_fixed_record(*bad)
        bad = list(args)
        bad[2] = [0x344AB, 0x54E0, 0x20000000]
        with self.assertRaisesRegex(ValueError, "pinned reviewed mapping"):
            validator.verify_iar3_fixed_record(*bad)
        with self.assertRaisesRegex(ValueError, "does not support"):
            validator.verify_iar3_fixed_record("apollo_main", 0x75D3FC, *args[2:])
        with self.assertRaisesRegex(ValueError, "exact pinned independent review"):
            validator.verify_iar3_review_basis({"path": row["review"][0], "sha256": "0" * 64},
                "20260930T190500Z", "f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa", row)

    def test_container_only_mapping_needs_verified_container_and_exact_children(self):
        parent = {"id": "container", "payload_id": "codec", "parent_image_id": None,
            "source_span": [0, 10], "source_size": 10, "size": 10,
            "transform": {"kind": "identity"}, "mapping_status": "container_only",
            "container_status": "container_only", "address_spaces": [],
            "evidence": [{"path": "evidence.txt", "sha256": self.evidence_hash,
                "input_sha256": self.evidence_hash}],
            "mapping_model": {"schema_version": 1, "kind": "container_only",
                "component_span": [0, 10], "child_image_ids": ["child"],
                "evidence": [{"path": "evidence.txt", "sha256": self.evidence_hash}]}}
        child = {"id": "child", "payload_id": "codec", "parent_image_id": "container"}
        validator.validate_mapping_model(parent, {"container": parent, "child": child}, 10, self.evidence_hash)
        parent["mapping_model"]["child_image_ids"] = []
        with self.assertRaisesRegex(ValueError, "verified identity parent"):
            validator.validate_mapping_model(parent, {"container": parent, "child": child}, 10, self.evidence_hash)
        parent["mapping_model"]["child_image_ids"] = ["child"]
        parent["address_spaces"] = [{"id": "made-up", "mappings": []}]
        with self.assertRaisesRegex(ValueError, "must not invent fixed runtime"):
            validator.validate_mapping_model(parent, {"container": parent, "child": child}, 10, self.evidence_hash)

    def test_parametric_mapping_requires_external_parameter_and_reviewed_guard(self):
        validator.ROOT = self.old_root
        review_ref = {"path": validator.CODEC_MAPPING_REVIEW_002_PATH,
                      "sha256": validator.CODEC_MAPPING_REVIEW_002_SHA256}
        objdump_path, objdump_hash = validator.CODEC_LOADER_OBJDUMPS["b"]
        type2_hash = "60adadb83f3cc544c4f80729b01c20d5f94dc54dcbca254f7e7ca3f45b1b115f"
        evidence = [dict(review_ref), {"path": objdump_path, "sha256": objdump_hash},
            {"path": validator.CODEC_NESTING_PATH, "sha256": validator.CODEC_NESTING_SHA256},
            {"path": validator.CODEC_SEGMENT_MAP_PATH, "sha256": validator.CODEC_SEGMENT_MAP_SHA256}]
        component_size = (self.old_root / "g2/blobs/official/g2-2.2.6.10/firmware_codec.bin").stat().st_size
        image = {"id": validator.CODEC_PARAMETRIC_IMAGE_ID, "payload_id": "codec", "parent_image_id": "type2",
            "source_span": [205748, 287808], "source_size": 82060, "size": 82060,
            "source_sha256": type2_hash,
            "transform": {"kind": "identity"}, "mapping_status": "parametric",
            "container_status": "resolved", "address_spaces": [],
            "evidence": [dict(item, input_sha256=type2_hash) for item in evidence],
            "mapping_model": {"schema_version": 1, "kind": "parametric", "component_span": [244032, 326092],
                "mapping_role": "flash_source",
                "placement": {"main_segment_component_origin": 38284, "segment_relative_offset": 205748},
                "runtime_parameter": {"name": "codec_nor_base", "source_register": "0xA0010068",
                    "derivation": "register_word & 0xffffff00", "value_status": "external_unmeasured"},
                "runtime_mappings": [{"space": "NOR_SOURCE", "image_span": [0, 82060],
                    "base_parameter": "codec_nor_base", "offset": 205748, "size": 82060}],
                "guard": {"variant": "b", "predicate": "(word_at_0xA0010068 & 0xF) == 2",
                    "review": review_ref, "instruction_evidence": [{"path": objdump_path, "sha256": objdump_hash}]},
                "evidence": evidence}}
        root = {"id": "codec", "payload_id": "codec", "parent_image_id": None,
            "source_span": [0, component_size], "source_size": component_size, "size": component_size,
            "source_sha256": validator.CODEC_PAYLOAD_SHA256, "transform": {"kind": "identity"}}
        type2 = {"id": "type2", "payload_id": "codec", "parent_image_id": "codec",
            "source_span": [38284, component_size], "source_size": 287808, "size": 287808,
            "source_sha256": validator.CODEC_PAYLOAD_SHA256, "transform": {"kind": "identity"},
            "content_sha256": type2_hash}
        image["content_sha256"] = "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941"
        hierarchy = {"codec": root, "type2": type2, image["id"]: image}
        with self.assertRaisesRegex(ValueError, "loader-origin conflation"):
            validator.validate_mapping_model(image, hierarchy, component_size, type2_hash)
        # The candidate assembled from the real 017 inventory is also not
        # accepted as a direct mapping model: its conditional_parametric label
        # is not a supported, independently reviewed mapping schema.
        real_path = (self.old_root / "g2/build/pseudocode-first/20260930T190500Z/attempts/"
                     "P1-inventory-assembly-017/002/images.jsonl")
        real_rows = [json.loads(line) for line in real_path.read_text().splitlines()]
        real_image = next(row for row in real_rows if row["id"] == "binh_b_stage2")
        real_by_id = {row["id"]: row for row in real_rows}
        with self.assertRaisesRegex(ValueError, "unresolved mapping facts"):
            validator.validate_mapping_model(real_image, real_by_id, component_size,
                                             real_image["source_sha256"])

    def test_codec_software_transfer_binds_two_exact_loader_contexts(self):
        validator.ROOT = self.old_root
        component_size = 326092
        parent_hash = "60adadb83f3cc544c4f80729b01c20d5f94dc54dcbca254f7e7ca3f45b1b115f"
        content_hash = "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941"
        refs = [
            (validator.CODEC_SOURCE_ORIGIN_PATH, validator.CODEC_SOURCE_ORIGIN_SHA256),
            (validator.CODEC_ROUTES_028_REVIEW_PATH, validator.CODEC_ROUTES_028_REVIEW_SHA256),
            (validator.CODEC_ROUTES_028_PATH, validator.CODEC_ROUTES_028_SHA256),
            (validator.CODEC_TRANSFER_REVIEW_PATH, validator.CODEC_TRANSFER_REVIEW_SHA256),
            validator.CODEC_LOADER_OBJDUMPS["a"], validator.CODEC_LOADER_OBJDUMPS["b"],
        ]
        evidence = [{"path": path, "sha256": sha, "input_sha256": parent_hash} for path, sha in refs]
        root = {"id": "codec", "payload_id": "codec", "parent_image_id": None,
            "source_span": [0, component_size], "source_size": component_size, "size": component_size,
            "source_sha256": validator.CODEC_PAYLOAD_SHA256, "transform": {"kind": "identity"}}
        type2 = {"id": "main_type2_container", "payload_id": "codec", "parent_image_id": "codec",
            "source_span": [38284, component_size], "source_size": 287808, "size": 287808,
            "source_sha256": validator.CODEC_PAYLOAD_SHA256, "content_sha256": parent_hash,
            "transform": {"kind": "identity"}}
        loader_a = {"id": "binh_a_stage1", "payload_id": "codec", "parent_image_id": "main_type2_container",
            "source_span": [0, 12288], "source_size": 12288, "size": 12288,
            "source_sha256": parent_hash,
            "content_sha256": "9546164f32680de47fa99ba85ba08a3c538822260957de6c1baee772638da464",
            "transform": {"kind": "identity"}}
        loader_b = {"id": "binh_b_stage1", "payload_id": "codec", "parent_image_id": "main_type2_container",
            "source_span": [193456, 205744], "source_size": 12288, "size": 12288,
            "source_sha256": parent_hash,
            "content_sha256": "a80924ccf78205ef1761c4f568d4ce31f909635bf3ad7eecfaed250ad801626c",
            "transform": {"kind": "identity"}}
        source = {"image_span": [0, 82060], "parent_image_id": "main_type2_container",
            "parent_span": [205748, 287808], "parent_sha256": parent_hash,
            "component_span": [244032, 326092], "size": 82060, "sha256": content_hash}
        parameters = [
            {"name": "a_loader_sampled_pmu_base", "loader_image_id": "binh_a_stage1",
             "loader_component_origin": 38284, "source_register": "0xA0010068",
             "derivation": "register_word & 0xffffff00", "value_status": "external_unmeasured", "value": None},
            {"name": "b_loader_sampled_pmu_base", "loader_image_id": "binh_b_stage1",
             "loader_component_origin": 231740, "source_register": "0xA0010068",
             "derivation": "register_word & 0xffffff00", "value_status": "external_unmeasured", "value": None},
        ]
        review_basis = [{"path": path, "sha256": sha} for path, sha in refs[:4]]
        routes = [
            {"route_id": "binh-b-stage2-normal",
             "loader": {"image_id": "binh_b_stage1", "component_origin": 231740,
                        "sampled_base_parameter": "b_loader_sampled_pmu_base"},
             "predicate": "(PMU_CFG_BOOT_MODE & 0xF) == 2 && sentinel[0x20033ffc] != 0xaabbccdd",
             "source": {"image_span": [0, 82060], "parent_span": [205748, 287808],
                        "component_span": [244032, 326092], "base_parameter": "b_loader_sampled_pmu_base",
                        "offset": 12292, "expression": "b_loader_sampled_pmu_base + 0x3004"},
             "write": {"operation": "spi_nor_read_request", "space": "IRAM",
                       "span": [268447744, 268529804], "size": 82060},
             "entry": {"space": "IRAM", "address": 268448000},
             "instruction": {"path": validator.CODEC_LOADER_OBJDUMPS["b"][0],
                             "sha256": validator.CODEC_LOADER_OBJDUMPS["b"][1],
                             "runtime_span": [268438864, 268438932]},
             "review_binding": {"path": validator.CODEC_TRANSFER_REVIEW_PATH,
                                "sha256": validator.CODEC_TRANSFER_REVIEW_SHA256,
                                "route_id": "binh-b-stage2-normal"},
             "external_assumption_refs": ["spi_helper_success"]},
            {"route_id": "binh-b-stage2-via-a-sentinel",
             "loader": {"image_id": "binh_a_stage1", "component_origin": 38284,
                        "sampled_base_parameter": "a_loader_sampled_pmu_base"},
             "predicate": "(PMU_CFG_BOOT_MODE & 0xF) == 2 && sentinel[0x20033ffc] == 0xaabbccdd",
             "source": {"image_span": [0, 82060], "parent_span": [205748, 287808],
                        "component_span": [244032, 326092], "base_parameter": "a_loader_sampled_pmu_base",
                        "offset": 205748, "expression": "a_loader_sampled_pmu_base + 0x323b4"},
             "write": {"operation": "spi_nor_read_request", "space": "DRAM",
                       "span": [536883200, 536965260], "size": 82060},
             "entry": {"space": "IRAM", "address": 268448000},
             "instruction": {"path": validator.CODEC_LOADER_OBJDUMPS["a"][0],
                             "sha256": validator.CODEC_LOADER_OBJDUMPS["a"][1],
                             "runtime_span": [268438092, 268438144]},
             "review_binding": {"path": validator.CODEC_TRANSFER_REVIEW_PATH,
                                "sha256": validator.CODEC_TRANSFER_REVIEW_SHA256,
                                "route_id": "binh-b-stage2-via-a-sentinel"},
             "external_assumption_refs": ["spi_helper_success", "dram_write_visible_to_iram_entry"]},
        ]
        model = {"schema_version": 1, "kind": "software_transfer", "component_span": [244032, 326092],
            "source": source, "runtime_parameters": parameters, "routes": routes,
            "external_assumptions": [{"name": "spi_helper_success", "status": "external_unverified"},
                {"name": "dram_write_visible_to_iram_entry", "status": "external_unverified"}],
            "review_basis": review_basis,
            "evidence": [{"path": path, "sha256": sha} for path, sha in refs]}
        image = {"id": "binh_b_stage2", "payload_id": "codec", "parent_image_id": "main_type2_container",
            "source_span": [205748, 287808], "source_size": 82060, "size": 82060,
            "source_sha256": parent_hash, "content_sha256": content_hash,
            "transform": {"kind": "identity"}, "mapping_status": "software_transfer",
            "container_status": "resolved", "address_spaces": [], "evidence": evidence,
            "mapping_model": model}
        hierarchy = {"codec": root, "main_type2_container": type2,
                     "binh_a_stage1": loader_a, "binh_b_stage1": loader_b,
                     image["id"]: image}
        validator.validate_mapping_model(image, hierarchy, component_size, parent_hash)

        mutations = [
            (lambda m: m["routes"][0]["loader"].update({"sampled_base_parameter": "a_loader_sampled_pmu_base"}),
             "typed loader context"),
            (lambda m: m["routes"][1]["loader"].update({"component_origin": 231740}), "typed loader context"),
            (lambda m: m["routes"][0]["source"].update({"offset": 205748}), "source formula"),
            (lambda m: m["routes"][1].update({"predicate": "sentinel is true"}), "guard or typed loader context"),
            (lambda m: m["routes"][0]["entry"].update({"address": 268447744}), "entry tuple"),
            (lambda m: m["routes"][0]["instruction"].update({"sha256": "0" * 64}), "exact original loader instruction"),
            (lambda m: m["source"].update({"sha256": "0" * 64}), "source identity"),
            (lambda m: m.update({"physical_alias": "confirmed"}), "unsupported fields"),
            (lambda m: m["external_assumptions"][1].update({"status": "resolved"}), "external_unverified"),
            (lambda m: m["routes"].pop(), "exactly the two reviewed"),
        ]
        for mutate, diagnostic in mutations:
            bad = json.loads(json.dumps(image))
            mutate(bad["mapping_model"])
            with self.subTest(diagnostic=diagnostic), self.assertRaisesRegex(ValueError, diagnostic):
                validator.validate_mapping_model(bad, hierarchy, component_size, parent_hash)
        missing_loader = dict(hierarchy)
        missing_loader.pop("binh_a_stage1")
        with self.assertRaisesRegex(ValueError, "loader identity, ancestry"):
            validator.validate_mapping_model(image, missing_loader, component_size, parent_hash)
        swapped_loaders = dict(hierarchy)
        swapped_loaders["binh_a_stage1"], swapped_loaders["binh_b_stage1"] = loader_b, loader_a
        with self.assertRaisesRegex(ValueError, "loader identity, ancestry"):
            validator.validate_mapping_model(image, swapped_loaders, component_size, parent_hash)
        wrong_loader_hash = dict(hierarchy)
        wrong_loader_hash["binh_b_stage1"] = dict(loader_b, content_sha256="0" * 64)
        with self.assertRaisesRegex(ValueError, "loader identity, ancestry"):
            validator.validate_mapping_model(image, wrong_loader_hash, component_size, parent_hash)
        wrong_loader_origin = dict(hierarchy)
        wrong_loader_origin["binh_b_stage1"] = dict(loader_b, source_span=[193457, 205745])
        with self.assertRaisesRegex(ValueError, "loader identity, ancestry"):
            validator.validate_mapping_model(image, wrong_loader_origin, component_size, parent_hash)

    def test_conditional_mapping_rejects_unresolved_alias_even_with_guarded_routes(self):
        validator.ROOT = self.old_root
        review_ref = {"path": validator.CODEC_MAPPING_REVIEW_002_PATH,
                      "sha256": validator.CODEC_MAPPING_REVIEW_002_SHA256}
        objdump_path, objdump_hash = validator.CODEC_LOADER_OBJDUMPS["a"]
        refs = [dict(review_ref), {"path": objdump_path, "sha256": objdump_hash}]
        source_hash = "b" * 64
        image = {"id": "conditional", "payload_id": "codec", "parent_image_id": None,
            "source_span": [0, 16], "source_size": 16, "size": 16,
            "transform": {"kind": "identity"}, "mapping_status": "conditional",
            "container_status": "resolved", "address_spaces": [],
            "evidence": [dict(item, input_sha256=source_hash) for item in refs],
            "mapping_model": {"schema_version": 1, "kind": "conditional", "component_span": [0, 16],
                "alias_status": "unresolved", "unresolved_facts": ["DRAM-to-IRAM visibility"],
                "evidence": refs,
                "alternatives": [
                    {"route_id": "normal", "guard": {"predicate": "normal", "review": review_ref,
                        "instruction_evidence": [{"path": objdump_path, "sha256": objdump_hash}]},
                        "space": "IRAM", "image_span": [0, 16], "loaded_start": 0x10003000, "size": 16},
                    {"route_id": "sentinel", "guard": {"predicate": "sentinel", "review": review_ref,
                        "instruction_evidence": [{"path": objdump_path, "sha256": objdump_hash}]},
                        "space": "DRAM", "image_span": [0, 16], "loaded_start": 0x20003000, "size": 16}]}}
        with self.assertRaisesRegex(ValueError, "unresolved required facts"):
            validator.validate_mapping_model(image, {"conditional": image}, 16, source_hash)
        with self.assertRaisesRegex(ValueError, "lacks its own reviewed evidence"):
            validator.validate_alias_mapping_result({"status": "pass",
                "alias_mapping_result": "unresolved physical alias"})
        model = image["mapping_model"]
        model["unresolved_facts"] = []
        model["alias_status"] = "not_applicable"
        for alternative in model["alternatives"]:
            old_guard = alternative["guard"]
            alternative["guard"] = {"predicate": old_guard["predicate"],
                "guard_review": {"path": review_ref["path"], "sha256": review_ref["sha256"],
                    "finding_id": "boot_mode_flash_base"},
                "instruction_evidence": old_guard["instruction_evidence"]}
        with self.assertRaisesRegex(ValueError, "does not bind the exact route predicate"):
            validator.validate_mapping_model(image, {"conditional": image}, 16, source_hash)

    def test_codec_candidate_mapping_labels_are_not_accepted_without_schema(self):
        validator.ROOT = self.old_root
        path = (self.old_root / "g2/build/pseudocode-first/20260930T190500Z/reviews/"
                "codec-canonical-images-003/images.candidate.jsonl")
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        by_id = {row["id"]: row for row in rows}
        with self.assertRaisesRegex(ValueError, "versioned mapping_model"):
            validator.validate_mapping_model(rows[0], by_id, rows[0]["size"], rows[0]["source_sha256"])
        candidate = next(row for row in rows if row["mapping_status"] == "conditional_parametric")
        with self.assertRaisesRegex(ValueError, "unresolved mapping facts"):
            validator.validate_mapping_model(candidate, by_id, 326092, candidate["source_sha256"])

    def _execution_contract_image(self):
        component = self.components[0]
        evidence = {"role": "source_bytes", "path": component["local_payload_path"],
                    "sha256": component["sha256"]}
        image = {"schema_version": 2, "campaign_id": self.campaign_id,
            "id": "img-codec", "payload_id": "codec", "parent_image_id": None,
            "source_span": [0, component["size"]], "source_size": component["size"],
            "source_sha256": component["sha256"], "size": component["size"],
            "content_sha256": component["sha256"], "content_path": component["local_payload_path"],
            "transform": {"kind": "identity"}, "mapping_status": "execution_contract",
            "container_status": "resolved", "address_spaces": [],
            "architecture": {"name": "fixture-isa", "endianness": "little", "isa_mode": "default"},
            "evidence": [{"path": component["local_payload_path"], "sha256": component["sha256"],
                          "input_sha256": component["sha256"]}]}
        route = {"route_id": "fixture-rom-delivery", "selection": {
                "kind": "external_selected_image", "dependency_id": "rom_selects_codec",
                "selected_image_id": image["id"], "source_origin": {"kind": "locked_payload",
                    "image_id": "codec", "sha256": component["sha256"], "span": [0, component["size"]]},
                "status": "external_unverified"},
            "loader_context": None, "transfer_kind": "external_delivery", "write": None,
            "expected_execution": {"space": "IRAM", "span": [0x1000, 0x1000 + component["size"]],
                "image_span": [0, component["size"]], "entry_offset": 16, "entry_address": 0x1010},
            "device_pointer": None, "external_refs": ["rom_selects_codec", "rom_delivers_codec"], "p2_unresolved": [],
            "evidence": [evidence]}
        model = {"schema_version": 1, "kind": "execution_contract", "review_id": "review-contract-img-codec",
            "execution_class": "cpu_image", "route_set_scope": "known_inventory_transfer_alternatives",
            "source": {"image_id": image["id"], "parent_image_id": None,
                "parent_sha256": component["sha256"], "parent_span": [0, component["size"]],
                "component_span": [0, component["size"]], "image_span": [0, component["size"]],
                "size": component["size"], "content_sha256": component["sha256"]},
            "routes": [route], "external_premises": [{"id": "rom_selects_codec",
                "kind": "external_selected_image", "status": "external_unverified",
                "statement": "Resident ROM selection is outside this fixture artifact."},
                {"id": "rom_delivers_codec", "kind": "external_delivery", "status": "external_unverified",
                 "statement": "Resident ROM delivery is outside this fixture artifact."}],
            "p2_unresolved": [], "evidence": [evidence]}
        image["mapping_model"] = model
        image["accounting_review_id"] = "review-img-codec"
        return image

    def test_execution_contract_requires_registry_trusted_complete_model_review(self):
        image = self._execution_contract_image()
        self.images[0] = image
        self.write_records()
        self.verify()

        registry_path = self.root / "g2/build/pseudocode-first/synthetic/inventory/review-registry.json"
        registry = json.loads(registry_path.read_text())
        registry["review_records"].pop("review-contract-img-codec")
        self.write_json("g2/build/pseudocode-first/synthetic/inventory/review-registry.json", registry)
        identity_path = self.campaign / "identity.json"
        identity = json.loads(identity_path.read_text())
        identity["review_registry"]["sha256"] = digest(registry_path.read_bytes())
        identity_path.write_text(json.dumps(identity, sort_keys=True))
        self.trusted_registry_hash = digest(registry_path.read_bytes())
        with self.assertRaisesRegex(ValueError, "trusted coordinator registry"):
            self.verify()

    def test_execution_contract_review_binds_exact_model_hash(self):
        image = self._execution_contract_image()
        self.images[0] = image
        self.write_records()
        review = next(r for r in self.reviews if r["id"] == image["mapping_model"]["review_id"])
        review["record_sha256"] = "0" * 64
        self.write_records()
        review = next(r for r in self.reviews if r["id"] == image["mapping_model"]["review_id"])
        review["record_sha256"] = "0" * 64
        review_path = self.campaign / "inventory" / "reviews.jsonl"
        review_path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in self.reviews))
        self.refresh_registry()
        with self.assertRaisesRegex(ValueError, "reviewed record hash mismatch"):
            self.verify()

    def test_execution_contract_rejects_malformed_or_unbound_mapping_facts(self):
        image = self._execution_contract_image()
        source = image["source_sha256"]
        size = image["size"]
        ref = lambda im, model: None
        validator.validate_mapping_model(image, {image["id"]: image}, size, source, ref)
        with self.assertRaisesRegex(ValueError, "trusted coordinator review"):
            validator.validate_mapping_model(image, {image["id"]: image}, size, source)
        cases = [
            (lambda m: m["source"].update({"component_span": [0, size + 1]}), "source identity/hash/bounds"),
            (lambda m: m["routes"][0]["selection"].update({"source_origin": {"kind": "locked_payload", "image_id": "codec", "sha256": source, "span": [0, size - 1]}}), "external source origin"),
            (lambda m: m["routes"][0].update({"selection": {"kind": "guard_ast", "ast": {"op": "eval", "code": "true"}, "evidence": m["evidence"]}}), "unsupported operator"),
            (lambda m: m["routes"][0]["expected_execution"].update({"entry_offset": size, "entry_address": 0x1010 + size}), "entry offset mismatch"),
            (lambda m: m["routes"][0]["expected_execution"].update({"span": [0xFFFFFFFF, 0xFFFFFFFF + size], "entry_address": 0xFFFFFFFF + 16}), "expected execution bounds/entry offset"),
            (lambda m: m["routes"][0].update({"write": {"space": "IRAM", "span": [0x1000, 0x1001], "size": size, "image_span": [0, size]}}), "write destination/span/size mismatch"),
            (lambda m: m.update({"execution_class": "opaque_data"}), "cannot reclassify executable bytes"),
            (lambda m: m["external_premises"][0].update({"statement": "physical alias proven"}), "cannot claim a proven physical alias"),
            (lambda m: m["external_premises"][0].update({"status": "resolved"}), "remain explicitly unverified"),
            (lambda m: m["routes"][0].update({"external_refs": []}), "external selected-image premise"),
        ]
        for mutate, error in cases:
            bad = json.loads(json.dumps(image))
            mutate(bad["mapping_model"])
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                validator.validate_mapping_model(bad, {bad["id"]: bad}, size, source, ref)

    def test_execution_contract_binds_nested_payload_and_loader_origins(self):
        payload = self.payloads["codec"]
        payload_hash = digest(payload)
        parent_bytes = payload[8:56]
        parent_hash = digest(parent_bytes)
        child_bytes = parent_bytes[4:12]
        child_hash = digest(child_bytes)
        self.write("nested/parent.bin", parent_bytes)
        self.write("nested/child.bin", child_bytes)
        self.write("nested/instructions.bin", b"loader instruction evidence")
        parent = {"id": "parent", "payload_id": "codec", "parent_image_id": "root",
            "source_span": [8, 56], "source_size": 48, "size": 48,
            "source_sha256": payload_hash, "content_sha256": parent_hash,
            "content_path": "nested/parent.bin", "transform": {"kind": "identity"}}
        root = {"id": "root", "payload_id": "codec", "parent_image_id": None,
            "source_span": [0, 64], "source_size": 64, "size": 64,
            "source_sha256": payload_hash, "content_sha256": payload_hash,
            "content_path": self.components[0]["local_payload_path"], "transform": {"kind": "identity"}}
        inst_hash = digest(b"loader instruction evidence")
        source_ref = {"role": "source_bytes", "path": "nested/child.bin", "sha256": child_hash}
        inst_ref = {"role": "instruction_bytes", "path": "nested/instructions.bin", "sha256": inst_hash}
        image = {"id": "nested-child", "payload_id": "codec", "parent_image_id": "parent",
            "source_span": [4, 12], "source_size": 8, "size": 8,
            "source_sha256": parent_hash, "content_sha256": child_hash,
            "content_path": "nested/child.bin", "transform": {"kind": "identity"},
            "mapping_status": "execution_contract", "container_status": "resolved", "address_spaces": [],
            "evidence": [{"path": source_ref["path"], "sha256": child_hash, "input_sha256": parent_hash},
                         {"path": inst_ref["path"], "sha256": inst_hash, "input_sha256": parent_hash}]}
        premises = [
            {"id": "selected", "kind": "external_selected_image", "status": "external_unverified", "statement": "External selection."},
            {"id": "delivered", "kind": "external_delivery", "status": "external_unverified", "statement": "External delivery."},
            {"id": "base", "kind": "external_parameter", "status": "external_unmeasured", "statement": "Sampled source base."},
            {"id": "visible", "kind": "external_visibility", "status": "external_unverified", "statement": "Destination visibility is external."},
        ]
        route = {"route_id": "nested-copy", "selection": {
                "kind": "external_selected_image", "dependency_id": "selected", "selected_image_id": image["id"],
                "source_origin": {"kind": "locked_payload", "image_id": "codec", "sha256": payload_hash,
                                  "span": [0, len(payload)]}, "status": "external_unverified"},
            "loader_context": {"loader_image_id": "parent", "loader_content_sha256": parent_hash,
                "loader_component_origin": 8, "source_base_parameter": "base", "source_offset": 4},
            "transfer_kind": "software_copy", "write": {"space": "DRAM", "span": [0x2000, 0x2008],
                "size": 8, "image_span": [0, 8]},
            "expected_execution": {"space": "IRAM", "span": [0x1000, 0x1008], "image_span": [0, 8],
                "entry_offset": 2, "entry_address": 0x1002},
            "device_pointer": None, "external_refs": ["selected", "delivered", "base", "visible"],
            "p2_unresolved": ["Full semantics remain P2."], "evidence": [source_ref, inst_ref]}
        image["mapping_model"] = {"schema_version": 1, "kind": "execution_contract", "review_id": "review-nested",
            "execution_class": "cpu_image", "route_set_scope": "known_inventory_transfer_alternatives",
            "source": {"image_id": "nested-child", "parent_image_id": "parent", "parent_sha256": parent_hash,
                "parent_span": [4, 12], "component_span": [12, 20], "image_span": [0, 8], "size": 8,
                "content_sha256": child_hash}, "routes": [route], "external_premises": premises,
            "p2_unresolved": ["Full semantics remain P2."], "evidence": [source_ref, inst_ref]}
        hierarchy = {"root": root, "parent": parent, image["id"]: image}
        self.assertNotEqual(parent_hash, payload_hash)
        validator.validate_mapping_model(image, hierarchy, len(payload), parent_hash, lambda _i, _m: None)
        wrong_origin = json.loads(json.dumps(image))
        wrong_origin["mapping_model"]["routes"][0]["loader_context"]["loader_component_origin"] = 9
        with self.assertRaisesRegex(ValueError, "loader origin/source offset"):
            validator.validate_mapping_model(wrong_origin, hierarchy, len(payload), parent_hash,
                                             lambda _i, _m: None)
        wrong_root = json.loads(json.dumps(image))
        wrong_root["mapping_model"]["routes"][0]["selection"]["source_origin"]["sha256"] = parent_hash
        with self.assertRaisesRegex(ValueError, "locked payload identity"):
            validator.validate_mapping_model(wrong_root, hierarchy, len(payload), parent_hash,
                                             lambda _i, _m: None)

    def test_execution_contract_device_pointer_span_is_not_shiftable(self):
        image = self._execution_contract_image()
        model = image["mapping_model"]
        model["execution_class"] = "device_data"
        route = model["routes"][0]
        route["transfer_kind"] = "device_pointer_translation"
        route["write"] = {"space": "DRAM", "span": [0x2000, 0x2000 + image["size"]],
            "size": image["size"], "image_span": [0, image["size"]]}
        route["expected_execution"] = None
        route["device_pointer"] = {"kind": "masked_address", "input_address": 0x2000,
            "mask": 0x0FFF, "device_address": 0, "span": [0, image["size"]],
            "image_span": [0, image["size"]]}
        model["external_premises"].append({"id": "device", "kind": "device_access",
            "status": "external_unverified", "statement": "Device access is external."})
        route["external_refs"].append("device")
        validator.validate_mapping_model(image, {image["id"]: image}, image["size"],
                                         image["source_sha256"], lambda _i, _m: None)
        route["device_pointer"]["span"] = [1, image["size"] + 1]
        with self.assertRaisesRegex(ValueError, "device pointer/address/span relation"):
            validator.validate_mapping_model(image, {image["id"]: image}, image["size"],
                                             image["source_sha256"], lambda _i, _m: None)
        route["device_pointer"]["span"] = [0, image["size"]]
        route["device_pointer"]["mask"] = -1
        with self.assertRaisesRegex(ValueError, "device pointer/address/span relation"):
            validator.validate_mapping_model(image, {image["id"]: image}, image["size"],
                                             image["source_sha256"], lambda _i, _m: None)

    def test_main_ram_fresh_replay_provenance_is_required_and_matches_outputs(self):
        repo = self.old_root
        validator.ROOT = repo
        base = "g2/build/pseudocode-first/20260930T190500Z/attempts/P1-canonical-main-transforms-012/001/"
        for descriptor, output_path in (
            (0x75D3F4, "g2/build/pseudocode-first/20260930T190500Z/attempts/P1-apollo-main-canonical-replay-009/001/decoded-20000000.bin"),
            (0x75D404, "g2/build/pseudocode-first/20260930T190500Z/attempts/P1-apollo-main-canonical-replay-009/001/decoded-20080000.bin"),
        ):
            receipt = json.loads((repo / f"{base}transform-{0x20000000 if descriptor == 0x75D3F4 else 0x20080000:08x}.json").read_text())
            output = receipt["output"]
            self.assertEqual(output["path"], output_path)
            ref = validator.verify_fresh_main_execution(receipt, output, descriptor)
            self.assertEqual(ref["path"], receipt["fresh_execution_receipt"]["path"])
            forged = dict(receipt)
            forged.pop("fresh_execution_receipt")
            with self.assertRaisesRegex(ValueError, "lacks the fresh canonical replay"):
                validator.verify_fresh_main_execution(forged, output, descriptor)

    def test_valid_decoded_image_requires_bound_independent_review(self):
        self.add_decoded_child()
        self.verify()

    def test_decoded_image_missing_transform_review_fails(self):
        self.add_decoded_child()
        self.reviews = [r for r in self.reviews if r["record_type"] != "transform"]
        (self.campaign / "inventory/reviews.jsonl").write_text(
            "".join(json.dumps(r, sort_keys=True) + "\n" for r in self.reviews))
        self.refresh_registry()
        with self.assertRaisesRegex(ValueError, "missing matching review for transform"):
            self.verify()

    def test_transform_review_without_trusted_registry_binding_fails(self):
        self.add_decoded_child()
        registry_path = self.root / "g2/build/pseudocode-first/synthetic/inventory/review-registry.json"
        registry = json.loads(registry_path.read_text())
        registry["review_records"].pop("review-transform-img-decoded-codec")
        self.write_json("g2/build/pseudocode-first/synthetic/inventory/review-registry.json", registry)
        self.trusted_registry_hash = digest(registry_path.read_bytes())
        identity_path = self.campaign / "identity.json"
        identity = json.loads(identity_path.read_text())
        identity["review_registry"]["sha256"] = self.trusted_registry_hash
        identity_path.write_text(json.dumps(identity, sort_keys=True))
        with self.assertRaisesRegex(ValueError, "trusted coordinator registry"):
            self.verify()

    def test_fabricated_decoded_receipt_argv_fails(self):
        self.add_decoded_child()
        self.mutate_transform_receipt(lambda r: r["execution"].update(argv=["arbitrary-command"]))
        with self.assertRaisesRegex(ValueError, "actual argv/exit receipt mismatch"):
            self.verify()

    def test_decoded_receipt_wrong_source_span_fails(self):
        self.add_decoded_child()
        self.mutate_transform_receipt(lambda r: r["source"].update(source_span=[17, 25]))
        with self.assertRaisesRegex(ValueError, "source identity/span mismatch"):
            self.verify()

    def test_decoded_receipt_wrong_output_hash_fails(self):
        self.add_decoded_child()
        self.mutate_transform_receipt(lambda r: r["output"].update(sha256="0" * 64))
        with self.assertRaisesRegex(ValueError, "output size/hash mismatch"):
            self.verify()

    def test_decoded_receipt_wrong_output_size_fails(self):
        self.add_decoded_child()
        self.mutate_transform_receipt(lambda r: r["output"].update(size=99))
        with self.assertRaisesRegex(ValueError, "output size/hash mismatch"):
            self.verify()

    def test_wrong_out_of_band_registry_pin_fails(self):
        with self.assertRaisesRegex(ValueError, "out-of-band trusted pin"):
            validator.verify(self.campaign, "0" * 64)

    def test_unregistered_review_receipt_fails(self):
        registry_path = self.root / "g2/build/pseudocode-first/synthetic/inventory/review-registry.json"
        registry = json.loads(registry_path.read_text())
        registry["review_records"].pop(self.reviews[0]["id"])
        self.write_json("g2/build/pseudocode-first/synthetic/inventory/review-registry.json", registry)
        self.trusted_registry_hash = digest(registry_path.read_bytes())
        identity_path = self.campaign / "identity.json"
        identity = json.loads(identity_path.read_text())
        identity["review_registry"]["sha256"] = self.trusted_registry_hash
        identity_path.write_text(json.dumps(identity, sort_keys=True))
        with self.assertRaisesRegex(ValueError, "trusted coordinator registry"):
            self.verify()

    def test_parse_pinned_official_bundle_read_only(self):
        repo = self.old_root
        target = json.loads((repo / "g2/workflow/target.json").read_text())
        manifest_ref = next(x for x in target["identity_sources"] if x["path"].endswith("g2-2.2.6.10.json"))
        manifest_path = repo / manifest_ref["path"]
        self.assertEqual(digest(manifest_path.read_bytes()), manifest_ref["sha256"])
        manifest = json.loads(manifest_path.read_text())
        bundle_path = repo / "g2/blobs/official/g2-2.2.6.10/e28738432d7b612d625331b00383149b.bin"
        bundle = bundle_path.read_bytes()
        self.assertEqual(len(bundle), target["bundle"]["size"])
        self.assertEqual(digest(bundle), target["bundle"]["sha256"])
        payloads = {c["id"]: (repo / c["local_payload_path"]).read_bytes() for c in target["components"]}
        entries = validator.parse_evenota(bundle, target, payloads, manifest)
        self.assertEqual([e["payload_id"] for e in entries], [c["id"] for c in target["components"]])
        self.assertEqual(entries[0]["payload_local_span"], [0, target["components"][0]["size"]])

    def test_package_span_equal_length_wrong_bytes_fails(self):
        entry = dict(self.entries[0])
        entry["package_payload_span"] = [entry["package_payload_span"][0] + 1, entry["package_payload_span"][1] + 1]
        entry["package_offset"] = [entry["package_offset"][0], entry["package_offset"][1] + 1]
        path = self.campaign / "inventory/outer-container.json"
        outer = json.loads(path.read_text())
        outer["entry_spans"][0] = entry
        path.write_text(json.dumps(outer, sort_keys=True))
        ident_path = self.campaign / "identity.json"
        ident = json.loads(ident_path.read_text())
        ident["container_validation"]["receipt_sha256"] = digest(path.read_bytes())
        ident_path.write_text(json.dumps(ident, sort_keys=True))
        with self.assertRaisesRegex(ValueError, "receipt|authenticated EVENOTA|source bytes"):
            self.verify()

    def test_invalid_payload_local_span_fails(self):
        path = self.campaign / "inventory/outer-container.json"
        outer = json.loads(path.read_text())
        outer["entry_spans"][0]["payload_local_span"] = [-1, 1]
        path.write_text(json.dumps(outer, sort_keys=True))
        ident_path = self.campaign / "identity.json"
        ident = json.loads(ident_path.read_text())
        ident["container_validation"]["receipt_sha256"] = digest(path.read_bytes())
        ident_path.write_text(json.dumps(ident, sort_keys=True))
        with self.assertRaisesRegex(ValueError, "authenticated EVENOTA|bounds|declarations"):
            self.verify()

    def test_wrong_hash_role_path_fails(self):
        row = next(r for r in self.reviews if r["record_type"] == "image")
        row["input_hashes"] = [x for x in row["input_hashes"] if x["role"] != "source"]
        row["input_hashes"].append({"role": "source", "path": "evidence.txt", "sha256": digest(self.evidence)})
        p = self.campaign / "inventory/reviews.jsonl"
        p.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in self.reviews))
        self.refresh_registry()
        with self.assertRaisesRegex(ValueError, "path/hash roles"):
            self.verify()

    def test_omitted_discovered_image_fails(self):
        self.discovery[0]["image_ids"] = ["img-codec", "image-omitted-from-images"]
        self.write_records()
        with self.assertRaisesRegex(ValueError, "image IDs differ"):
            self.verify()

    def test_fabricated_decoded_transform_fails(self):
        self.add_decoded_child()
        child = next(i for i in self.images if i["id"] == "img-decoded-codec")
        child["transform"]["recipe_id"] = "attacker-selected-command"
        self.write_records()
        with self.assertRaisesRegex(ValueError, "unsupported decoded transform recipe"):
            self.verify()

    def test_discovery_missing_fails(self):
        self.discovery.pop()
        self.write_records()
        with self.assertRaisesRegex(ValueError, "discovery reconciliation"):
            self.verify()


if __name__ == "__main__":
    unittest.main()
