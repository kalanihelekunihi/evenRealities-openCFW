#!/usr/bin/env python3
"""Fail-closed P1 inventory validator (schema v2).

JSONL schemas (all rows carry schema_version=2, campaign_id, id):

* images.jsonl: payload_id, parent_image_id (null for a root image; parents precede
  children), source_span [parent_start,parent_end), source_size, source_sha256
  (SHA-256 of the full parent image), size (decoded content length),
  content_sha256, content_path, transform {kind:"identity"} or the reviewed
  decoded transform described below, mapping_status="resolved",
  architecture {name,endianness,isa_mode}, address_spaces [{id, mappings:[{
  image_start,image_end,loaded_start,loaded_end}]}], accounting_review_id.
  Every image has its own exact image-byte coverage partition. Root images must
  be bound to their payload hash; children must be bounded by a parent image.
  Numeric mappings remain mandatory for `mapping_status="resolved"`. A
  versioned `mapping_model` can instead describe an identity-only container
  with enumerated children, the narrowly reviewed BINH-B software-transfer
  routes, instruction-guarded conditional alternatives, or a coordinator-
  reviewed conditional `execution_contract` whose record binds the complete
  route model and raw-byte evidence. External selection/delivery/visibility
  premises may remain explicitly unverified; missing artifact-derived source,
  write, expected-entry, or device-address facts still fail. Decoded
  transforms continue to require unique numeric mappings. The payload-level
  analysis plan and independent accounting/coverage gates remain separate.
* coverage.jsonl: scope {kind:"package"|"payload"|"image",id}, start, end,
  kind {code,data,container,padding,unknown}, evidence [{path,sha256,
  input_sha256}], review_id. Package and each payload partition their complete
  byte ranges; each image also has a shadow ledger partition of its own bytes.
  Image ledgers do not add bytes to the package/payload denominators. Unknown
  code/data is allowed at G1, but every interval still needs evidence/review.
* reviews.jsonl: id, record_type, record_id, record_sha256 (canonical record
  hash, omitting review_id/accounting_review_id), author, reviewer, decision,
  input_hashes [{role,path,sha256}]. Each path is checked against its actual file.
* analysis-plan.json: schema_version=2, campaign_id, id="analysis-plan",
  target_sha256, review_id,
  architecture_plans with exactly one initial architecture plan per payload, including
  architecture, endianness, isa_mode, address_spaces, decoder_support, and
  hash-bound evidence. Its independent review uses record_type="analysis_plan",
  record_id="analysis-plan", and hashes the canonical document omitting
  review_id. This validates that a plan exists; it does not prove decoder
  correctness or nested-image completeness by itself.

Decoded images use fixed recipes only. `thumb-stock-handler-unicorn-v1` checks a
four-word descriptor. `apollo-iar3-itcm-stock-handler-unicorn-v1` is restricted
to the pinned Apollo main 22-byte to 24-byte ITCM transform reviewed in
review004. `apollo-iar3-fixed-reviewed-stock-handler-unicorn-v2` admits only
the six fixed Apollo main/bootloader initialization tuples pinned to reviews
004, 005, and bootloader review002. Both decode signed relative pointers,
encoded source lengths, destinations, and the enclosing-table handler selector.
The two Apollo-main RAM tuples also require the separately captured canonical
replay execution receipt and bind it into the external transform review. This
keeps the stale worker script receipt out of the trust chain. IAR3 R9-relocated
inputs and all other tuples remain unsupported.
Source span/size and decoded output size are separate; the receipt pins the
hash of the exact source slice while `source_sha256` pins the full parent. A
receipt must bind authenticated parent bytes, descriptor words, original
handler bytes, output, tool/script/library hashes, exact argv and exit status.
A separate `transform` review must pass and bind those files through the
trusted coordinator registry. The validator verifies evidence; it does not
execute commands or prove that a recorded command ran. The independent
reviewer and out-of-band registry are therefore part of the trust boundary.
Unsupported or unreviewed transforms remain fail-closed.

Review labels are not cryptographic identities. This validator checks reviewer
IDs against a coordinator-provided authenticated registry receipt whose hash
must also be supplied through the trusted CLI argument; authenticity of that
out-of-band hash is an external trust boundary. Discovery completeness is a separately reviewed claim, not an
algorithmically provable fact. This validator requires a per-payload
discovery-reconciliation receipt, but cannot independently prove exhaustive
firmware discovery and makes no P2/G2 completeness claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import struct
import sys
from typing import Any, Callable

ROOT = pathlib.Path(__file__).resolve().parents[3]
SCHEMA = 2
KINDS = {"code", "data", "container", "padding", "unknown"}
EVENOTA_HEADER_SIZE = 128
EVENOTA_TOC_OFFSET = 64
EVENOTA_TOC_ENTRY_SIZE = 16
EVENOTA_TRAILER = b"evenota\0" + b"\0" * 8
EVENOTA_COMPONENT_MAGIC = 0x4E455645
DECODED_RECIPES = {"thumb-stock-handler-unicorn-v1", "apollo-iar3-itcm-stock-handler-unicorn-v1",
                   "apollo-iar3-fixed-reviewed-stock-handler-unicorn-v2"}
IAR3_RECIPE = "apollo-iar3-itcm-stock-handler-unicorn-v1"
IAR3_FIXED_RECIPE = "apollo-iar3-fixed-reviewed-stock-handler-unicorn-v2"
APOLLO_REVIEW_004_PATH = "g2/build/pseudocode-first/20260930T190500Z/reviews/apollo-itcm-transform-004/review-004.json"
APOLLO_REVIEW_004_SHA256 = "5df7bf4e1c7f6aaa12b36628e87adbe49057e6f0a5af15c4d26005eb70cf4772"
APOLLO_MAIN_REVIEW_005_PATH = "g2/build/pseudocode-first/20260930T190500Z/reviews/apollo-main-initializers-005/review-005.json"
APOLLO_MAIN_REVIEW_005_SHA256 = "7e45e5d1cf9776999cf0071e00fea5a2764a7c2baf886173085d24d7d84ba99f"
BOOT_REVIEW_002_PATH = "g2/build/pseudocode-first/20260930T190500Z/reviews/bootloader-initializers-002/review-002.json"
BOOT_REVIEW_002_SHA256 = "bcc2fbd8d4bdf510a1c5ff957f88de4e6f77ea5ac83fe3b9ad4ef309fffa9c84"
APOLLO_MAIN_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
BOOT_SHA256 = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
APOLLO_ITCM_OUTPUT_SHA256 = "0676154418085b0630f2a20cc50fbbe3967dd2d9b7794fe1aad3f6af14f2fb83"
APOLLO_ITCM_HANDLER_SHA256 = "41e4a34428bb2c09774785d474f5209201f6551c823f0286eb66063dedc74a9d"
APOLLO_INIT_TABLE_RUNTIME_SPAN = (0x75D3C8, 0x75D410)
CODEC_MAPPING_REVIEW_002_PATH = "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-flash-loader-startup-001/review-002.json"
CODEC_MAPPING_REVIEW_002_SHA256 = "96936139137e6b6dd7a3b0fbd087620c01f08df8f4af56edce899baab6381d57"
CODEC_MAPPING_REVIEW_001_PATH = "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-flash-loader-startup-001/review-001.json"
CODEC_MAPPING_REVIEW_001_SHA256 = "d94c3e2a159ec579060ac0ce15572efa6890636da1dc3bc3429bafd416b86345"
CODEC_PAYLOAD_SHA256 = "b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0"
CODEC_LOADER_OBJDUMPS = {
    "a": ("g2/build/pseudocode-first/20260930T190500Z/attempts/P1-codec-flash-loader-mappings-001/002/loader-a.objdump.txt",
          "8887040f99ca177e1c18b21a3287c0fd8e9533999227ab39d6e59eb52a2dd0bd"),
    "b": ("g2/build/pseudocode-first/20260930T190500Z/attempts/P1-codec-flash-loader-mappings-001/002/loader-b.objdump.txt",
          "acb1ccacf18a038d962c29c0cd1fb78dee6d23e1d523626f92ed053902b9f002"),
}
CODEC_NESTING_PATH = "g2/build/pseudocode-first/20260930T190500Z/inventory/codec-nesting.json"
CODEC_NESTING_SHA256 = "1e86b1b382e1c6e7724d5453d64a513aade02ac70f6d720b5985b77a1b3870df"
CODEC_SEGMENT_MAP_PATH = "g2/tools/manifests/g2-codec-fwpk-segment-map.tsv"
CODEC_SEGMENT_MAP_SHA256 = "4160d70c38121ed02aae2392f71ce1f9c499e92a1a36e280ca53dce9b5a4c161"
CODEC_PARAMETRIC_IMAGE_ID = "binh_b_stage2"
CODEC_MAIN_COMPONENT_ORIGIN = 38284
CODEC_BINH_B_STAGE2_SEGMENT_OFFSET = 205748
CODEC_BINH_B_STAGE2_SIZE = 82060
CODEC_STAGE2_COMPONENT_SPAN = [244032, 326092]
CODEC_STAGE2_CONTENT_SHA256 = "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941"
CODEC_TYPE2_SHA256 = "60adadb83f3cc544c4f80729b01c20d5f94dc54dcbca254f7e7ca3f45b1b115f"
CODEC_SOURCE_ORIGIN_PATH = "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-loader-source-origin-034/finding.json"
CODEC_SOURCE_ORIGIN_SHA256 = "3eb5833013154bd0f5aa7a4034da7bdb484786768f3145aa105de980ebcf166f"
CODEC_ROUTES_028_REVIEW_PATH = "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-execution-route-inventory-028/review.json"
CODEC_ROUTES_028_REVIEW_SHA256 = "bb5f9531dd52ab5fed9d4b836ceb3c172b6844b40a182c09f6c5908143f8667c"
CODEC_ROUTES_028_PATH = "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-execution-route-inventory-028/routes.json"
CODEC_ROUTES_028_SHA256 = "7fbd04ab6077db1d1c1e85a57fdcab9b6d97f2cc4a56148b6816c5131a70fa32"
CODEC_TRANSFER_REVIEW_PATH = "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-software-transfer-root-review-037/review.json"
CODEC_TRANSFER_REVIEW_SHA256 = "f3be0c87b1b7b3632f8f88560be6ecd310fbb22d7f7db68349e1b28e406ade62"
CODEC_TRANSFER_PROPOSAL_SHA256 = "fed8be25a481cb34af03273eb39645e7d95484232aa715d7b3311d495d86635d"
CODEC_TRANSFER_ROUTES = {
    "binh-b-stage2-normal": {
        "loader_image_id": "binh_b_stage1", "loader_component_origin": 231740,
        "source_base_parameter": "b_loader_sampled_pmu_base", "source_offset": 12292,
        "predicate": "(PMU_CFG_BOOT_MODE & 0xF) == 2 && sentinel[0x20033ffc] != 0xaabbccdd",
        "write_space": "IRAM", "write_span": [268447744, 268529804],
        "entry_space": "IRAM", "entry_address": 268448000,
        "instruction_key": "b",
    },
    "binh-b-stage2-via-a-sentinel": {
        "loader_image_id": "binh_a_stage1", "loader_component_origin": 38284,
        "source_base_parameter": "a_loader_sampled_pmu_base", "source_offset": 205748,
        "predicate": "(PMU_CFG_BOOT_MODE & 0xF) == 2 && sentinel[0x20033ffc] == 0xaabbccdd",
        "write_space": "DRAM", "write_span": [536883200, 536965260],
        "entry_space": "IRAM", "entry_address": 268448000,
        "instruction_key": "a",
    },
}
CODEC_TRANSFER_INSTRUCTION_SPANS = {"a": [268438092, 268438144], "b": [268438864, 268438932]}
CODEC_TRANSFER_LOADERS = {
    "binh_a_stage1": {"component_origin": 38284, "component_span": [38284, 50572],
                      "parent_span": [0, 12288], "size": 12288,
                      "content_sha256": "9546164f32680de47fa99ba85ba08a3c538822260957de6c1baee772638da464"},
    "binh_b_stage1": {"component_origin": 231740, "component_span": [231740, 244028],
                      "parent_span": [193456, 205744], "size": 12288,
                      "content_sha256": "a80924ccf78205ef1761c4f568d4ce31f909635bf3ad7eecfaed250ad801626c"},
}
IAR3_FIXED_RECORDS = {
    # payload_id, descriptor runtime, descriptor words, dispatch word,
    # source runtime/span/hash, destination, output size/hash, handler entry
    # and pinned review basis. Source spans are offsets in the authenticated
    # parent payload; source runtime addresses are independently checked below.
    ("apollo_main", 0x75D3E4): {
        "words": (0x36F2A, 0x2C, 0x40), "dispatch_word": 0xFFCDCD3F,
        "source_runtime": 0x79430E, "source_span": (0x35C32E, 0x35C344),
        "source_sha256": "f7416eabf10e45a1b98a8034c0d649de0c6d680d354b6e6deb57f459f45a820f",
        "destination": 0x40, "output_size": 24,
        "output_sha256": APOLLO_ITCM_OUTPUT_SHA256, "handler": 0x43A11F,
        "handler_sha256": APOLLO_ITCM_HANDLER_SHA256,
        "review": (APOLLO_REVIEW_004_PATH, APOLLO_REVIEW_004_SHA256)},
    ("apollo_main", 0x75D3F4): {
        "words": (0x344AA, 0x54E0, 0x20000000), "dispatch_word": 0xFFCDCD2F,
        "source_runtime": 0x79189E, "source_span": (3512510, 3523374),
        "source_sha256": "bf6c95e35e2a134d1d1098e3e8e6a9b47ae8b9bdadcd996f2fff81673e8e07cb",
        "destination": 0x20000000, "output_size": 17752,
        "output_sha256": "df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743",
        "handler": 0x43A11F, "handler_sha256": APOLLO_ITCM_HANDLER_SHA256,
        "review": (APOLLO_MAIN_REVIEW_005_PATH, APOLLO_MAIN_REVIEW_005_SHA256)},
    ("apollo_main", 0x75D404): {
        "words": (0x322F3, 0x434E, 0x20080000), "dispatch_word": 0xFFCDCD1F,
        "source_runtime": 0x78F6F7, "source_span": (3503895, 3512510),
        "source_sha256": "94c9d167550d2abee7c9d2c74c861de5f1d48ea0745c08f5a2c5ad0bfde88106",
        "destination": 0x20080000, "output_size": 769646,
        "output_sha256": "a5be949c41cf1e9a7d4a6b4aa6e3a6cb2f9c9bcb3a04a866d15e49e3976a7d0c",
        "handler": 0x43A11F, "handler_sha256": APOLLO_ITCM_HANDLER_SHA256,
        "review": (APOLLO_MAIN_REVIEW_005_PATH, APOLLO_MAIN_REVIEW_005_SHA256)},
    ("apollo_bootloader", 0x4330F4): {
        "words": (0x136D, 0x2C, 0x40), "dispatch_word": 0xFFFE2237,
        "source_runtime": 0x434461, "source_span": (148577, 148599),
        "source_sha256": "f7416eabf10e45a1b98a8034c0d649de0c6d680d354b6e6deb57f459f45a820f",
        "destination": 0x40, "output_size": 24,
        "output_sha256": APOLLO_ITCM_OUTPUT_SHA256, "handler": 0x415327,
        "handler_sha256": APOLLO_ITCM_HANDLER_SHA256,
        "review": (BOOT_REVIEW_002_PATH, BOOT_REVIEW_002_SHA256)},
    ("apollo_bootloader", 0x433104): {
        "words": (0x10BC, 0x4E2, 0x20000000), "dispatch_word": 0xFFFE2227,
        "source_runtime": 0x4341C0, "source_span": (147904, 148529),
        "source_sha256": "5b8e3a303e0ca03dcf5375491441067823e17d840181ae16898c58b8cafde4f8",
        "destination": 0x20000000, "output_size": 1371,
        "output_sha256": "e3bea7ccd46bc324829152b5b5a9069aecce5db243876273084d29bd7d47b843",
        "handler": 0x415327, "handler_sha256": APOLLO_ITCM_HANDLER_SHA256,
        "review": (BOOT_REVIEW_002_PATH, BOOT_REVIEW_002_SHA256)},
    ("apollo_bootloader", 0x433114): {
        "words": (0x131D, 0x60, 0x20080000), "dispatch_word": 0xFFFE2217,
        "source_runtime": 0x434431, "source_span": (148529, 148577),
        "source_sha256": "5a14fdce36feee1baa2671a18a80b296b5fdde8a06709bde95cc0e75e57feb26",
        "destination": 0x20080000, "output_size": 4096,
        "output_sha256": "ad7facb2586fc6e966c004d7d1d16b024f5805ff7cb47c7a85dabd8b48892ca7",
        "handler": 0x415327, "handler_sha256": APOLLO_ITCM_HANDLER_SHA256,
        "review": (BOOT_REVIEW_002_PATH, BOOT_REVIEW_002_SHA256)},
}
for (_payload_id, _descriptor_runtime), _record in IAR3_FIXED_RECORDS.items():
    _record["descriptor_runtime"] = _descriptor_runtime
    _record["review_kind"] = ("legacy_itcm" if _record["review"][0] == APOLLO_REVIEW_004_PATH
                               else "apollo_main" if _payload_id == "apollo_main" else "bootloader")
    _record["decision"] = ({"legacy_itcm": "pass", "apollo_main": "pass_fixed_ram_mapping_evidence",
                            "bootloader": "pass_fixed_input_transform_evidence"}[_record["review_kind"]])
    _record["output_source_size"] = _record["source_span"][1] - _record["source_span"][0]


def crc32c_msb(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1EDC6F41) & 0xFFFFFFFF if crc & 0x80000000 else (crc << 1) & 0xFFFFFFFF
    return crc


def fail(message: str) -> None:
    raise ValueError(message)


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical_hash(value: dict[str, Any], omitted: set[str] | None = None) -> str:
    obj = {k: v for k, v in value.items() if k not in (omitted or set())}
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def read_json(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        fail(f"expected JSON object: {path}")
    return value


def read_jsonl(path: pathlib.Path) -> list[dict[str, Any]]:
    if not path.is_file():
        fail(f"missing required file: {path}")
    rows = []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            fail(f"blank JSONL line: {path}:{number}")
        row = json.loads(line)
        if not isinstance(row, dict):
            fail(f"expected JSON object: {path}:{number}")
        rows.append(row)
    return rows


def require_hash(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        fail(f"invalid SHA-256: {label}")
    return value


def hash_bound_file(item: dict[str, Any], label: str) -> None:
    if set(("path", "sha256")) - item.keys():
        fail(f"incomplete evidence reference: {label}")
    if not isinstance(item["path"], str):
        fail(f"invalid evidence path: {label}")
    p = ROOT / item["path"]
    expected = require_hash(item["sha256"], label)
    if not p.is_file() or sha256(p) != expected:
        fail(f"evidence file missing or hash mismatch: {item['path']}")


def mapped_runtime(image: dict[str, Any], image_start: int, length: int, label: str) -> int:
    """Return the unique loaded address for an image byte range."""
    matches = []
    for space in image.get("address_spaces", []):
        for mapping in space.get("mappings", []):
            if (mapping.get("image_start", -1) <= image_start
                    and image_start + length <= mapping.get("image_end", -1)):
                matches.append(mapping["loaded_start"] + image_start - mapping["image_start"])
    if not matches or len(set(matches)) != 1:
        fail(f"{label}: image range has no unique runtime mapping")
    return matches[0]


def mapped_image_offset(image: dict[str, Any], runtime_start: int, length: int, label: str) -> int:
    """Return the unique image offset for a loaded address range."""
    matches = []
    for space in image.get("address_spaces", []):
        for mapping in space.get("mappings", []):
            if (mapping.get("loaded_start", -1) <= runtime_start
                    and runtime_start + length <= mapping.get("loaded_end", -1)):
                matches.append(mapping["image_start"] + runtime_start - mapping["loaded_start"])
    if not matches or len(set(matches)) != 1:
        fail(f"{label}: runtime range has no unique image mapping")
    return matches[0]


def component_coordinate_span(image: dict[str, Any], image_by_id: dict[str, dict[str, Any]],
                             component_size: int) -> list[int]:
    """Map identity-only nested image coordinates back to component coordinates."""
    start = 0
    current = image
    seen: set[str] = set()
    while True:
        ident = current.get("id")
        if ident in seen or current.get("transform", {}).get("kind") != "identity":
            fail("mapping model requires an acyclic identity-only path to component bytes")
        seen.add(ident)
        source = current.get("source_span")
        if (not isinstance(source, list) or len(source) != 2
                or any(type(n) is not int for n in source) or source[0] < 0 or source[1] <= source[0]):
            fail("mapping model source ancestry is malformed")
        start += source[0]
        parent_id = current.get("parent_image_id")
        if parent_id is None:
            break
        parent = image_by_id.get(parent_id)
        if parent is None or parent.get("payload_id") != image.get("payload_id"):
            fail("mapping model ancestry has a missing or foreign parent")
        current = parent
    size = image.get("size")
    if type(size) is not int or start + size > component_size:
        fail("mapping model component coordinates exceed authenticated payload")
    return [start, start + size]


def _mapping_evidence_refs(model: dict[str, Any], image: dict[str, Any], expected_source: str) -> set[tuple[str, str]]:
    refs = model.get("evidence")
    if not isinstance(refs, list) or not refs:
        fail("mapping model lacks hash-bound evidence")
    image_refs = {(item.get("path"), item.get("sha256")) for item in image.get("evidence", [])}
    checked: set[tuple[str, str]] = set()
    for ref in refs:
        if not isinstance(ref, dict) or not {"path", "sha256"}.issubset(ref):
            fail("mapping model evidence reference is malformed")
        hash_bound_file(ref, "mapping model evidence")
        if (ref["path"], ref["sha256"]) not in image_refs:
            fail("mapping model evidence is not bound by the image record")
        if ref.get("input_sha256") not in (None, expected_source):
            fail("mapping model evidence references different source bytes")
        checked.add((ref["path"], ref["sha256"]))
    return checked


def _pass_review_ref(ref: Any, label: str) -> dict[str, Any]:
    if not isinstance(ref, dict) or set(ref) != {"path", "sha256"}:
        fail(f"{label} review reference is missing or malformed")
    hash_bound_file(ref, f"{label} review")
    review = read_json(ROOT / ref["path"])
    review_status = review.get("status")
    passed = (review_status == "pass" or str(review_status or "").startswith("pass_")
              or (review_status is None and review.get("decision") == "pass"))
    if not passed:
        fail(f"{label} review is not a passing review")
    return review


def validate_alias_mapping_result(review: dict[str, Any]) -> dict[str, Any]:
    """Require a typed alias finding; arbitrary truthy prose is not a proof."""
    result = review.get("alias_mapping_result")
    if (not isinstance(result, dict) or set(result) != {"status", "route_bindings"}
            or result.get("status") not in {"confirmed_alias", "confirmed_distinct_spaces"}
            or not isinstance(result.get("route_bindings"), list)):
        fail("conditional physical alias lacks its own reviewed evidence")
    return result


def _validate_codec_binh_b_software_transfer(image: dict[str, Any], model: dict[str, Any],
                                              image_by_id: dict[str, dict[str, Any]],
                                              component_size: int,
                                              evidence: set[tuple[str, str]],
                                              component_span: list[int]) -> None:
    """Admit only the two reviewed, loader-context-specific BINH-B routes."""
    if (image.get("id") != "binh_b_stage2" or image.get("payload_id") != "codec"
            or image.get("parent_image_id") != "main_type2_container"
            or image.get("transform", {}).get("kind") != "identity"
            or image.get("container_status") != "resolved"
            or component_size != 326092 or component_span != CODEC_STAGE2_COMPONENT_SPAN
            or image.get("source_span") != [205748, 287808]
            or image.get("source_size") != CODEC_BINH_B_STAGE2_SIZE
            or image.get("size") != CODEC_BINH_B_STAGE2_SIZE
            or image.get("source_sha256") != CODEC_TYPE2_SHA256
            or image.get("content_sha256") != CODEC_STAGE2_CONTENT_SHA256):
        fail("software_transfer is restricted to the authenticated identity BINH-B stage2 bytes")
    for loader_id, expected_loader in CODEC_TRANSFER_LOADERS.items():
        loader = image_by_id.get(loader_id)
        if (not isinstance(loader, dict) or loader.get("id") != loader_id
                or loader.get("payload_id") != "codec"
                or loader.get("parent_image_id") != "main_type2_container"
                or loader.get("transform", {}).get("kind") != "identity"
                or loader.get("source_span") != expected_loader["parent_span"]
                or loader.get("source_size") != expected_loader["size"]
                or loader.get("size") != expected_loader["size"]
                or loader.get("source_sha256") != CODEC_TYPE2_SHA256
                or loader.get("content_sha256") != expected_loader["content_sha256"]
                or component_coordinate_span(loader, image_by_id, component_size) != expected_loader["component_span"]):
            fail("software_transfer loader identity, ancestry, component origin, or content hash mismatch")

    required = {"schema_version", "kind", "component_span", "source", "runtime_parameters",
                "routes", "external_assumptions", "review_basis", "evidence"}
    if set(model) != required or model.get("schema_version") != 1 or model.get("kind") != "software_transfer":
        fail("software_transfer mapping model is incomplete or has unsupported fields")
    source = model.get("source")
    if (not isinstance(source, dict)
            or set(source) != {"image_span", "parent_image_id", "parent_span", "parent_sha256",
                               "component_span", "size", "sha256"}
            or source.get("image_span") != [0, CODEC_BINH_B_STAGE2_SIZE]
            or source.get("parent_image_id") != "main_type2_container"
            or source.get("parent_span") != [205748, 287808]
            or source.get("parent_sha256") != CODEC_TYPE2_SHA256
            or source.get("component_span") != CODEC_STAGE2_COMPONENT_SPAN
            or source.get("size") != CODEC_BINH_B_STAGE2_SIZE
            or source.get("sha256") != CODEC_STAGE2_CONTENT_SHA256):
        fail("software_transfer source identity, parent coordinates, bounds, or hash mismatch")

    expected_parameters = [
        {"name": "a_loader_sampled_pmu_base", "loader_image_id": "binh_a_stage1",
         "loader_component_origin": 38284, "source_register": "0xA0010068",
         "derivation": "register_word & 0xffffff00", "value_status": "external_unmeasured", "value": None},
        {"name": "b_loader_sampled_pmu_base", "loader_image_id": "binh_b_stage1",
         "loader_component_origin": 231740, "source_register": "0xA0010068",
         "derivation": "register_word & 0xffffff00", "value_status": "external_unmeasured", "value": None},
    ]
    if model.get("runtime_parameters") != expected_parameters:
        fail("software_transfer must retain distinct typed A/B loader origins and unmeasured PMU parameters")

    expected_external = [
        {"name": "spi_helper_success", "status": "external_unverified"},
        {"name": "dram_write_visible_to_iram_entry", "status": "external_unverified"},
    ]
    if model.get("external_assumptions") != expected_external:
        fail("software_transfer helper success and DRAM/IRAM visibility must remain explicitly external_unverified")

    routes = model.get("routes")
    if not isinstance(routes, list) or {r.get("route_id") for r in routes if isinstance(r, dict)} != set(CODEC_TRANSFER_ROUTES) or len(routes) != 2:
        fail("software_transfer must enumerate exactly the two reviewed BINH-B stage2 routes")

    expected_review_basis = [
        {"path": CODEC_SOURCE_ORIGIN_PATH, "sha256": CODEC_SOURCE_ORIGIN_SHA256},
        {"path": CODEC_ROUTES_028_REVIEW_PATH, "sha256": CODEC_ROUTES_028_REVIEW_SHA256},
        {"path": CODEC_ROUTES_028_PATH, "sha256": CODEC_ROUTES_028_SHA256},
        {"path": CODEC_TRANSFER_REVIEW_PATH, "sha256": CODEC_TRANSFER_REVIEW_SHA256},
    ]
    if model.get("review_basis") != expected_review_basis:
        fail("software_transfer lacks the exact independently reviewed source-origin and tuple basis")
    for ref in expected_review_basis:
        if (ref["path"], ref["sha256"]) not in evidence:
            fail("software_transfer review basis is not included in hash-bound image/model evidence")

    origin = read_json(ROOT / CODEC_SOURCE_ORIGIN_PATH)
    route_review = read_json(ROOT / CODEC_ROUTES_028_REVIEW_PATH)
    tuple_review = read_json(ROOT / CODEC_TRANSFER_REVIEW_PATH)
    if (origin.get("status") != "revision_required_loader_origin_conflation"
            or origin.get("payload_sha256") != CODEC_PAYLOAD_SHA256
            or route_review.get("review_id") != "codec-execution-route-inventory-028"
            or route_review.get("route_output") != {"path": CODEC_ROUTES_028_PATH, "sha256": CODEC_ROUTES_028_SHA256}
            or tuple_review.get("decision") != "pass_corrected_source_coordinate_and_transfer_tuple_proposal_only"
            or tuple_review.get("proposal_sha256") != CODEC_TRANSFER_PROPOSAL_SHA256):
        fail("software_transfer review records do not bind the corrected source-origin proposal")
    tuple_guards = tuple_review.get("mapping_guards")
    if not isinstance(tuple_guards, list) or len(tuple_guards) != 2:
        fail("software_transfer coordinator review lacks the exact two route tuple bindings")

    origin_evidence = {item.get("variant"): item for item in origin.get("evidence", []) if isinstance(item, dict)}
    if (origin_evidence.get("a", {}).get("path"), origin_evidence.get("a", {}).get("sha256")) != CODEC_LOADER_OBJDUMPS["a"] or (
            origin_evidence.get("b", {}).get("path"), origin_evidence.get("b", {}).get("sha256")) != CODEC_LOADER_OBJDUMPS["b"]:
        fail("software_transfer original A/B loader instruction hashes are not the reviewed listings")
    relations = {item.get("route"): item for item in origin.get("observed_relations", []) if isinstance(item, dict)}
    if (relations.get("B normal", {}).get("sampled_parameter") != "boot_base_B"
            or relations.get("B normal", {}).get("offset") != 12292
            or relations.get("B normal", {}).get("loader_component_origin") != 231740
            or relations.get("A sentinel-equal", {}).get("sampled_parameter") != "boot_base_A"
            or relations.get("A sentinel-equal", {}).get("offset") != 205748
            or relations.get("A sentinel-equal", {}).get("loader_component_origin") != 38284):
        fail("software_transfer source formulas do not match the independently reviewed loader origins")

    expected_tuple_rows = []
    for route_id, expected in CODEC_TRANSFER_ROUTES.items():
        key = expected["instruction_key"]
        insn_path, insn_sha = CODEC_LOADER_OBJDUMPS[key]
        for route in routes:
            if not isinstance(route, dict) or route.get("route_id") != route_id:
                continue
            route_expected_keys = {"route_id", "loader", "predicate", "source", "write", "entry",
                                   "instruction", "review_binding", "external_assumption_refs"}
            if set(route) != route_expected_keys:
                fail("software_transfer route contains unsupported or unauthenticated fields")
            loader = {"image_id": expected["loader_image_id"],
                      "component_origin": expected["loader_component_origin"],
                      "sampled_base_parameter": expected["source_base_parameter"]}
            if route.get("loader") != loader or route.get("predicate") != expected["predicate"]:
                fail("software_transfer guard or typed loader context does not match reviewed instructions")
            source_offset = expected["source_offset"]
            expression = f"{expected['source_base_parameter']} + 0x{source_offset:x}"
            if route.get("source") != {"image_span": [0, CODEC_BINH_B_STAGE2_SIZE],
                    "parent_span": [205748, 287808], "component_span": CODEC_STAGE2_COMPONENT_SPAN,
                    "base_parameter": expected["source_base_parameter"], "offset": source_offset,
                    "expression": expression}:
                fail("software_transfer route source formula, loader origin, or source bounds mismatch")
            if route.get("write") != {"operation": "spi_nor_read_request", "space": expected["write_space"],
                    "span": expected["write_span"], "size": CODEC_BINH_B_STAGE2_SIZE}:
                fail("software_transfer write destination tuple mismatch")
            if route.get("entry") != {"space": expected["entry_space"], "address": expected["entry_address"]}:
                fail("software_transfer entry tuple mismatch")
            if route.get("instruction") != {"path": insn_path, "sha256": insn_sha,
                    "runtime_span": CODEC_TRANSFER_INSTRUCTION_SPANS[key]}:
                fail("software_transfer route is not bound to its exact original loader instruction span/hash")
            if route.get("review_binding") != {"path": CODEC_TRANSFER_REVIEW_PATH,
                    "sha256": CODEC_TRANSFER_REVIEW_SHA256, "route_id": route_id}:
                fail("software_transfer route lacks its exact reviewed tuple binding")
            expected_assumptions = ["spi_helper_success"]
            if route_id == "binh-b-stage2-via-a-sentinel":
                expected_assumptions.append("dram_write_visible_to_iram_entry")
            if route.get("external_assumption_refs") != expected_assumptions:
                fail("software_transfer route omits or invents external premises")
        expected_tuple_rows.append({
            "route_id": route_id,
            "loader_image_id": expected["loader_image_id"],
            "loader_component_origin": expected["loader_component_origin"],
            "source_base_parameter": expected["source_base_parameter"],
            "source_offset": expected["source_offset"],
            "source_component_span": CODEC_STAGE2_COMPONENT_SPAN,
            "source_parent_span": [205748, 287808],
            "predicate": expected["predicate"],
            "write_space": expected["write_space"],
            "write_span": expected["write_span"],
            "entry_space": expected["entry_space"],
            "entry_address": expected["entry_address"],
            "external_assumptions": (["spi_helper_success", "dram_write_visible_to_iram_entry"]
                                      if route_id == "binh-b-stage2-via-a-sentinel" else ["spi_helper_success"]),
        })
    if tuple_guards != expected_tuple_rows:
        fail("software_transfer route tuples differ from the independently reviewed loader-specific bindings")


def _validate_guard_ast(node: Any, depth: int = 0) -> None:
    """Validate the small typed predicate AST used by execution contracts."""
    if depth > 16 or not isinstance(node, dict):
        fail("execution_contract guard AST is malformed")
    op = node.get("op")
    if op in {"eq", "ne"}:
        if set(node) != {"op", "left", "right"}:
            fail("execution_contract guard AST comparison is malformed")
        for side in (node["left"], node["right"]):
            if not isinstance(side, dict):
                fail("execution_contract guard AST operand is malformed")
            kind = side.get("kind")
            if kind == "constant":
                if set(side) != {"kind", "value"} or type(side["value"]) is not int:
                    fail("execution_contract guard AST constant is malformed")
            elif kind == "register":
                if set(side) != {"kind", "name"} or not isinstance(side["name"], str) or not side["name"]:
                    fail("execution_contract guard AST register is malformed")
            elif kind == "memory_u32":
                if (set(side) != {"kind", "address", "endianness"} or type(side["address"]) is not int
                        or side["address"] < 0 or side["endianness"] not in {"little", "big"}):
                    fail("execution_contract guard AST memory operand is malformed")
            else:
                fail("execution_contract guard AST has unsupported operand")
        return
    if op == "masked_eq":
        if (set(node) != {"op", "value", "mask", "expected"} or type(node["mask"]) is not int
                or type(node["expected"]) is not int or node["mask"] < 0 or node["expected"] < 0):
            fail("execution_contract guard AST masked comparison is malformed")
        _validate_guard_ast({"op": "eq", "left": node["value"],
                             "right": {"kind": "constant", "value": node["expected"]}}, depth + 1)
        return
    if op in {"and", "or"}:
        terms = node.get("terms")
        if set(node) != {"op", "terms"} or not isinstance(terms, list) or len(terms) < 2:
            fail("execution_contract guard AST boolean group is malformed")
        for term in terms:
            _validate_guard_ast(term, depth + 1)
        return
    fail("execution_contract guard AST uses an unsupported operator")


def _validate_execution_contract(image: dict[str, Any], image_by_id: dict[str, dict[str, Any]],
                                 component_size: int, expected_source: str,
                                 expected_component_span: list[int]) -> None:
    model = image.get("mapping_model")
    required = {"schema_version", "kind", "review_id", "execution_class", "route_set_scope", "source", "routes",
                "external_premises", "p2_unresolved", "evidence"}
    if not isinstance(model, dict) or set(model) != required:
        fail("execution_contract model is incomplete or has unsupported fields")
    if model.get("schema_version") != 1 or model.get("kind") != "execution_contract":
        fail("execution_contract model version/kind is unsupported")
    if not isinstance(model.get("review_id"), str) or not model["review_id"]:
        fail("execution_contract requires a trusted coordinator review")
    if image.get("transform", {}).get("kind") != "identity":
        fail("execution_contract currently requires identity source bytes")
    src = model.get("source")
    src_required = {"image_id", "parent_image_id", "parent_sha256", "parent_span", "component_span",
                    "image_span", "size", "content_sha256"}
    if not isinstance(src, dict) or set(src) != src_required:
        fail("execution_contract source identity is incomplete")
    if (src.get("image_id") != image.get("id") or src.get("parent_image_id") != image.get("parent_image_id")
            or src.get("parent_sha256") != expected_source or src.get("parent_span") != image.get("source_span")
            or src.get("component_span") != expected_component_span or src.get("image_span") != [0, image.get("size")]
            or src.get("size") != image.get("size") or src.get("content_sha256") != image.get("content_sha256")):
        fail("execution_contract source identity/hash/bounds differ from authenticated image ancestry")
    if (type(src.get("size")) is not int or src["size"] <= 0
            or src["component_span"][1] - src["component_span"][0] != src["size"]
            or src["image_span"][1] - src["image_span"][0] != src["size"]):
        fail("execution_contract source bounds/size are inconsistent")
    if model.get("execution_class") not in {"cpu_image", "device_data"}:
        fail("execution_contract cannot reclassify executable bytes as opaque/container data")
    if model.get("route_set_scope") != "known_inventory_transfer_alternatives":
        fail("execution_contract route set must declare its inventory-level scope")
    unresolved = model.get("p2_unresolved")
    if not isinstance(unresolved, list) or any(not isinstance(x, str) or not x for x in unresolved):
        fail("execution_contract P2 residuals must be an explicit string list")

    premises = model.get("external_premises")
    if not isinstance(premises, list):
        fail("execution_contract external premises must be explicit")
    premise_by_id: dict[str, dict[str, Any]] = {}
    premise_keys = {"id", "kind", "status", "statement"}
    allowed_premise_kinds = {"external_selected_image", "external_source_origin", "external_delivery",
                             "external_visibility", "xip_aperture", "external_parameter",
                             "helper_success", "device_invocation", "device_access"}
    for premise in premises:
        if not isinstance(premise, dict) or set(premise) != premise_keys:
            fail("execution_contract external premise is malformed")
        pid = premise.get("id")
        if (not isinstance(pid, str) or not pid or pid in premise_by_id
                or premise.get("kind") not in allowed_premise_kinds
                or premise.get("status") not in {"external_unverified", "external_unmeasured"}
                or not isinstance(premise.get("statement"), str) or not premise["statement"]):
            fail("execution_contract external premise must remain explicitly unverified")
        premise_text = premise["statement"].lower()
        if (("physical alias" in premise_text or "alias" in premise_text)
                and "unverified" not in premise_text
                and any(word in premise_text for word in ("proven", "confirmed", "measured", "resolved", "established"))
                or premise.get("id") == "physical_alias_proven"):
            fail("execution_contract cannot claim a proven physical alias")
        premise_by_id[pid] = premise

    evidence = model.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        fail("execution_contract lacks hash-bound raw-byte evidence")
    evidence_pairs: set[tuple[str, str, str]] = set()
    for ref in evidence:
        if not isinstance(ref, dict) or set(ref) != {"role", "path", "sha256"}:
            fail("execution_contract evidence reference is malformed")
        if ref.get("role") not in {"source_bytes", "instruction_bytes", "target_bytes", "header_bytes",
                                     "linked_layout", "device_pointer_bytes", "other_bytes"}:
            fail("execution_contract evidence role is unsupported")
        hash_bound_file(ref, "execution_contract evidence")
        evidence_pairs.add((ref["role"], ref["path"], ref["sha256"]))
    if ("source_bytes", image.get("content_path"), image.get("content_sha256")) not in evidence_pairs:
        fail("execution_contract source-byte evidence is not bound to the authenticated image content")

    routes = model.get("routes")
    if not isinstance(routes, list) or not routes:
        fail("execution_contract must enumerate known inventory mapping routes")
    route_ids: set[str] = set()
    route_keys = {"route_id", "selection", "loader_context", "transfer_kind", "write",
                  "expected_execution", "device_pointer", "external_refs", "p2_unresolved", "evidence"}
    selection_keys = {"kind", "ast", "evidence"}
    external_selection_keys = {"kind", "dependency_id", "selected_image_id", "source_origin", "status"}
    allowed_transfer = {"external_delivery", "software_copy", "direct_xip", "device_pointer_translation"}
    for route in routes:
        if not isinstance(route, dict) or set(route) != route_keys:
            fail("execution_contract route is malformed")
        route_id = route.get("route_id")
        if not isinstance(route_id, str) or not route_id or route_id in route_ids:
            fail("execution_contract route IDs must be unique")
        route_ids.add(route_id)
        if route.get("transfer_kind") not in allowed_transfer:
            fail("execution_contract transfer kind is unsupported")
        selection = route.get("selection")
        if not isinstance(selection, dict):
            fail("execution_contract route selection is missing")
        if selection.get("kind") == "guard_ast":
            if set(selection) != selection_keys:
                fail("execution_contract guard selection is malformed")
            _validate_guard_ast(selection["ast"])
            sel_evidence = selection.get("evidence")
            if not isinstance(sel_evidence, list) or not sel_evidence:
                fail("execution_contract guard AST lacks instruction evidence")
            for ref in sel_evidence:
                if (not isinstance(ref, dict) or set(ref) != {"role", "path", "sha256"}
                        or (ref.get("role"), ref.get("path"), ref.get("sha256")) not in evidence_pairs):
                    fail("execution_contract guard evidence is not bound by the model")
        elif selection.get("kind") == "external_selected_image":
            if set(selection) != external_selection_keys:
                fail("execution_contract external selected-image relation is malformed")
            dep_id = selection.get("dependency_id")
            if (selection.get("status") != "external_unverified" or not isinstance(dep_id, str)
                    or dep_id not in premise_by_id or premise_by_id[dep_id]["kind"] != "external_selected_image"
                    or selection.get("selected_image_id") != image.get("id")):
                fail("execution_contract lacks named external selected-image dependency")
            origin = selection.get("source_origin")
            if (not isinstance(origin, dict) or set(origin) != {"kind", "image_id", "sha256", "span"}
                    or origin.get("kind") not in {"locked_payload", "parent_image"}
                    or type_span(origin.get("span")) is None):
                fail("execution_contract selected-image source origin is malformed")
            origin_image_id = origin.get("image_id")
            if origin.get("kind") == "locked_payload":
                root = image
                seen_roots: set[str] = set()
                while root.get("parent_image_id") is not None:
                    if root["id"] in seen_roots:
                        fail("execution_contract payload ancestry is cyclic")
                    seen_roots.add(root["id"])
                    root = image_by_id.get(root["parent_image_id"])
                    if root is None:
                        fail("execution_contract payload ancestry is incomplete")
                if (origin_image_id != image.get("payload_id") or root.get("content_sha256") != origin.get("sha256")
                        or origin.get("span") != [0, component_size]):
                    fail("execution_contract external source origin differs from locked payload identity")
            else:
                parent = image_by_id.get(origin_image_id)
                if (parent is None or parent.get("payload_id") != image.get("payload_id")
                        or parent.get("content_sha256") != origin.get("sha256")
                        or origin.get("span") != [0, parent.get("size")]):
                    fail("execution_contract external source origin differs from authenticated parent")
        else:
            fail("execution_contract selection kind is unsupported")

        loader_context = route.get("loader_context")
        if loader_context is not None:
            loader_keys = {"loader_image_id", "loader_content_sha256", "loader_component_origin",
                           "source_base_parameter", "source_offset"}
            if not isinstance(loader_context, dict) or set(loader_context) != loader_keys:
                fail("execution_contract loader context is malformed")
            loader = image_by_id.get(loader_context.get("loader_image_id"))
            if (loader is None or loader.get("payload_id") != image.get("payload_id")
                    or loader.get("content_sha256") != loader_context.get("loader_content_sha256")):
                fail("execution_contract loader identity/ancestry is not authenticated")
            loader_component = component_coordinate_span(loader, image_by_id, component_size)
            if (type(loader_context.get("loader_component_origin")) is not int
                    or loader_context["loader_component_origin"] != loader_component[0]
                    or type(loader_context.get("source_offset")) is not int or loader_context["source_offset"] < 0
                    or loader_context["loader_component_origin"] + loader_context["source_offset"]
                    != expected_component_span[0]):
                fail("execution_contract loader origin/source offset do not resolve to authenticated source bytes")
            param_id = loader_context.get("source_base_parameter")
            if (not isinstance(param_id, str) or param_id not in premise_by_id
                    or premise_by_id[param_id]["kind"] != "external_parameter"
                    or premise_by_id[param_id]["status"] != "external_unmeasured"):
                fail("execution_contract source-base parameter is not a named external value")
        elif route.get("transfer_kind") == "software_copy" and selection["kind"] != "external_selected_image":
            fail("execution_contract software copy requires authenticated loader context or external selection")

        external_refs = route.get("external_refs")
        if (not isinstance(external_refs, list) or len(set(external_refs)) != len(external_refs)
                or any(ref not in premise_by_id for ref in external_refs)):
            fail("execution_contract route has missing/unknown external premises")
        if (selection.get("kind") == "external_selected_image"
                and selection["dependency_id"] not in external_refs):
            fail("execution_contract route omits its external selected-image premise")
        required_premise_kind = {"external_delivery": "external_delivery", "direct_xip": "xip_aperture"}.get(
            route["transfer_kind"])
        if required_premise_kind and not any(premise_by_id[x]["kind"] == required_premise_kind
                                             for x in external_refs):
            fail("execution_contract route omits its external delivery/aperture premise")
        if (route["transfer_kind"] == "device_pointer_translation"
                and not any(premise_by_id[x]["kind"] in {"device_invocation", "device_access"}
                            for x in external_refs)):
            fail("execution_contract device route omits its external consumer premise")
        route_p2 = route.get("p2_unresolved")
        if not isinstance(route_p2, list) or any(not isinstance(x, str) or not x for x in route_p2):
            fail("execution_contract route P2 residuals are malformed")
        route_evidence = route.get("evidence")
        if not isinstance(route_evidence, list) or not route_evidence:
            fail("execution_contract route lacks raw-byte evidence")
        for ref in route_evidence:
            if (not isinstance(ref, dict) or set(ref) != {"role", "path", "sha256"}
                    or (ref.get("role"), ref.get("path"), ref.get("sha256")) not in evidence_pairs):
                fail("execution_contract route evidence is not bound by the model")

        write = route.get("write")
        if write is not None:
            if (not isinstance(write, dict) or set(write) != {"space", "span", "size", "image_span"}
                    or not isinstance(write.get("space"), str) or not write["space"]
                    or type_span(write.get("span")) is None or type_span(write.get("image_span")) is None
                    or write["image_span"] != [0, image["size"]] or write.get("size") != image["size"]
                    or write["span"][1] - write["span"][0] != image["size"]
                    or write["span"][1] > 0x100000000):
                fail("execution_contract write destination/span/size mismatch")
        if route.get("transfer_kind") == "software_copy" and write is None:
            fail("execution_contract software copy lacks a write span")
        if route.get("transfer_kind") in {"external_delivery", "direct_xip"} and write is not None:
            fail("execution_contract direct/external mapping cannot invent a software write")

        expected = route.get("expected_execution")
        device = route.get("device_pointer")
        if model["execution_class"] == "cpu_image":
            if device is not None or not isinstance(expected, dict) or set(expected) != {
                    "space", "span", "image_span", "entry_offset", "entry_address"}:
                fail("execution_contract CPU image requires an expected execution span and entry")
            if (not isinstance(expected.get("space"), str) or not expected["space"]
                    or type_span(expected.get("span")) is None or type_span(expected.get("image_span")) is None
                    or expected["image_span"] != [0, image["size"]]
                    or expected["span"][1] - expected["span"][0] != image["size"]
                    or expected["span"][1] > 0x100000000
                    or type(expected.get("entry_offset")) is not int
                    or not 0 <= expected["entry_offset"] < image["size"]
                    or type(expected.get("entry_address")) is not int
                    or expected["entry_address"] != expected["span"][0] + expected["entry_offset"]):
                fail("execution_contract expected execution bounds/entry offset mismatch")
            if write is not None and write["span"] != expected["span"]:
                has_visibility = any(premise_by_id[x]["kind"] == "external_visibility" for x in external_refs)
                if not has_visibility:
                    fail("execution_contract separate write/expected entry requires external visibility premise")
        else:
            if expected is not None or not isinstance(device, dict) or set(device) != {
                    "kind", "input_address", "mask", "device_address", "span", "image_span"}:
                fail("execution_contract device data requires an explicit device-pointer relation")
            if (route.get("transfer_kind") != "device_pointer_translation" or write is None
                    or device.get("kind") != "masked_address" or type(device.get("input_address")) is not int
                    or type(device.get("mask")) is not int or type(device.get("device_address")) is not int
                    or device.get("device_address") != (device["input_address"] & device["mask"])
                    or device.get("input_address") != write["span"][0]
                    or type_span(device.get("span")) is None or type_span(device.get("image_span")) is None
                    or device["image_span"] != [0, image["size"]]
                    or device["span"] != [device["device_address"], device["device_address"] + image["size"]]
                    or device["span"][1] > 0x100000000
                    or not 0 <= device["input_address"] <= 0xFFFFFFFF
                    or not 0 <= device["mask"] <= 0xFFFFFFFF
                    or not 0 <= device["device_address"] <= 0xFFFFFFFF):
                fail("execution_contract device pointer/address/span relation is inconsistent")


def type_span(value: Any) -> list[int] | None:
    if (not isinstance(value, list) or len(value) != 2 or any(type(n) is not int for n in value)
            or value[0] < 0 or value[1] <= value[0]):
        return None
    return value


def validate_mapping_model(image: dict[str, Any], image_by_id: dict[str, dict[str, Any]],
                           component_size: int, expected_source: str,
                           execution_contract_review: Callable[[dict[str, Any], dict[str, Any]], None] | None = None) -> None:
    """Validate non-numeric mapping forms without weakening resolved-map rules."""
    status = image.get("mapping_status")
    spaces = image.get("address_spaces")
    if status == "resolved":
        if not isinstance(spaces, list) or not spaces:
            fail("resolved image mapping requires concrete numeric address spaces")
        if "mapping_model" in image:
            fail("resolved numeric mappings cannot carry an alternate mapping model")
        return
    if status not in {"container_only", "parametric", "conditional", "software_transfer", "execution_contract"}:
        fail(f"unresolved mapping facts: {image.get('id')}")
    if not isinstance(spaces, list) or spaces:
        fail("non-numeric mappings must not invent fixed runtime address spaces")
    model = image.get("mapping_model")
    if not isinstance(model, dict) or model.get("schema_version") != 1 or model.get("kind") != status:
        fail("non-numeric mapping requires a matching versioned mapping_model")
    expected_component_span = component_coordinate_span(image, image_by_id, component_size)
    if status == "execution_contract":
        _validate_execution_contract(image, image_by_id, component_size, expected_source,
                                     expected_component_span)
        _mapping_evidence_refs(model, image, expected_source)
        if execution_contract_review is None:
            fail("execution_contract requires trusted coordinator review binding")
        execution_contract_review(image, model)
        return
    if model.get("component_span") != expected_component_span:
        fail("mapping model component span differs from authenticated image ancestry")
    evidence = _mapping_evidence_refs(model, image, expected_source)
    if status == "container_only":
        actual_children = sorted(iid for iid, child in image_by_id.items()
                                 if child.get("parent_image_id") == image.get("id"))
        if (image.get("transform", {}).get("kind") != "identity" or not actual_children
                or sorted(model.get("child_image_ids", [])) != actual_children
                or image.get("container_status") not in {"resolved", "container_only"}):
            fail("container-only mapping must be a verified identity parent with explicitly listed children")
        if set(model) != {"schema_version", "kind", "component_span", "child_image_ids", "evidence"}:
            fail("container-only mapping model has unsupported fields")
        return
    if status == "software_transfer":
        _validate_codec_binh_b_software_transfer(image, model, image_by_id, component_size,
                                                 evidence, expected_component_span)
        return
    if status == "parametric":
        if image.get("transform", {}).get("kind") != "identity" or image.get("container_status") != "resolved":
            fail("parametric mappings require resolved identity-image container facts")
        root_image = image
        while root_image.get("parent_image_id") is not None:
            root_image = image_by_id[root_image["parent_image_id"]]
        if (image.get("payload_id") != "codec" or root_image.get("source_sha256") != CODEC_PAYLOAD_SHA256
                or root_image.get("source_size") != component_size):
            fail("codec parametric mapping is restricted to the authenticated codec payload ancestry")
        required = {"schema_version", "kind", "component_span", "runtime_parameter", "runtime_mappings", "guard", "evidence"}
        required |= {"mapping_role", "placement"}
        if set(model) != required:
            fail("parametric mapping model is incomplete or has unsupported fields")
        if (model.get("mapping_role") != "flash_source"
                or model.get("placement") != {"main_segment_component_origin": CODEC_MAIN_COMPONENT_ORIGIN,
                    "segment_relative_offset": CODEC_BINH_B_STAGE2_SEGMENT_OFFSET}):
            fail("parametric mapping lacks the reviewed main-segment placement coordinates")
        fail("loader-origin conflation: legacy shared-base flash_source mapping is disabled pending a reviewed loader-context-specific software_transfer recipe")
    required = {"schema_version", "kind", "component_span", "alternatives", "alias_status", "unresolved_facts", "evidence"}
    if set(model) not in (required, required | {"alias_review"}):
        fail("conditional mapping model is incomplete or has unsupported fields")
    if model.get("unresolved_facts"):
        fail("conditional mapping retains unresolved required facts")
    if model.get("alias_status") == "unresolved":
        fail("conditional mapping has an unresolved physical alias")
    if model.get("alias_status") not in {"not_applicable", "reviewed"}:
        fail("conditional mapping must state whether a physical alias is required")
    alias_review = None
    if model.get("alias_status") == "reviewed":
        alias_ref = model.get("alias_review")
        alias_review = _pass_review_ref(alias_ref, "conditional physical alias")
        validate_alias_mapping_result(alias_review)
        if (alias_ref["path"], alias_ref["sha256"]) not in evidence:
            fail("conditional physical alias lacks its own reviewed evidence")
    if image.get("transform", {}).get("kind") != "identity" or image.get("container_status") != "resolved":
        fail("conditional routes require resolved identity-image container facts")
    alternatives = model.get("alternatives")
    if not isinstance(alternatives, list) or len(alternatives) < 2:
        fail("conditional mapping requires at least two explicit guarded alternatives")
    route_ids: set[str] = set()
    predicates: set[str] = set()
    route_spaces: set[str] = set()
    route_bindings: list[dict[str, Any]] = []
    for alternative in alternatives:
        if not isinstance(alternative, dict) or set(alternative) != {"route_id", "guard", "space", "image_span", "loaded_start", "size"}:
            fail("conditional mapping alternative is malformed")
        route_id = alternative.get("route_id")
        if not isinstance(route_id, str) or not route_id or route_id in route_ids:
            fail("conditional mapping route IDs must be unique")
        route_ids.add(route_id)
        guard = alternative.get("guard")
        if not isinstance(guard, dict) or set(guard) != {"predicate", "guard_review", "instruction_evidence"}:
            fail("conditional mapping route lacks an instruction-backed guard")
        if not isinstance(guard.get("predicate"), str) or not guard["predicate"] or guard["predicate"] in predicates:
            fail("conditional routes require distinct explicit guard predicates")
        predicates.add(guard["predicate"])
        guard_ref = guard.get("guard_review")
        if not isinstance(guard_ref, dict) or set(guard_ref) != {"path", "sha256", "finding_id"}:
            fail("conditional route must name the exact reviewed guard finding")
        guard_review = _pass_review_ref({"path": guard_ref.get("path"), "sha256": guard_ref.get("sha256")},
                                        "conditional route guard")
        if (guard_ref["path"], guard_ref["sha256"]) not in evidence:
            fail("conditional route guard review is not bound to image evidence")
        mapping_tuple = {key: alternative[key] for key in ("space", "image_span", "loaded_start", "size")}
        matching_guard_rows = [row for row in guard_review.get("mapping_guards", [])
                               if row.get("route_id") == route_id
                               and row.get("finding_id") == guard_ref["finding_id"]]
        if (len(matching_guard_rows) != 1 or matching_guard_rows[0].get("predicate") != guard["predicate"]
                or matching_guard_rows[0].get("mapping") != mapping_tuple):
            fail("conditional guard review does not bind the exact route predicate and mapping tuple")
        instruction_evidence = guard.get("instruction_evidence")
        if not isinstance(instruction_evidence, list) or not instruction_evidence:
            fail("conditional route guard has no instruction evidence")
        for ref in instruction_evidence:
            hash_bound_file(ref, "conditional route guard instruction evidence")
            if (ref["path"], ref["sha256"]) not in evidence or not any(
                    item.get("path") == ref["path"] and item.get("sha256") == ref["sha256"]
                    for item in guard_review.get("evidence", [])):
                fail("conditional route instruction evidence is not bound by its passing review")
        span = alternative.get("image_span")
        if (not isinstance(span, list) or len(span) != 2 or span != [0, image["size"]]
                or not isinstance(alternative.get("space"), str) or not alternative["space"]
                or type(alternative.get("loaded_start")) is not int or alternative["loaded_start"] < 0
                or type(alternative.get("size")) is not int or alternative["size"] != image["size"]):
            fail("conditional route mapping must cover the exact image bytes")
        route_spaces.add(alternative["space"])
        route_bindings.append({key: alternative[key] for key in
                               ("route_id", "space", "image_span", "loaded_start", "size")})
    if len(route_spaces) > 1:
        if model.get("alias_status") == "not_applicable":
            fail("conditional cross-space routes require an explicit reviewed alias determination")
        expected_bindings = sorted(route_bindings, key=lambda row: row["route_id"])
        actual_bindings = alias_review.get("alias_mapping_result", {}).get("route_bindings", [])
        if (not isinstance(actual_bindings, list)
                or any(not isinstance(row, dict) or set(row) !=
                       {"route_id", "space", "image_span", "loaded_start", "size"}
                       for row in actual_bindings)
                or sorted(actual_bindings, key=lambda row: row.get("route_id", "")) != expected_bindings):
            fail("conditional alias review does not bind every exact route mapping tuple")
    elif model.get("alias_status") == "reviewed":
        fail("conditional alias review is not applicable without cross-space routes")


def validate_image_load_mapping_requirement(image: dict[str, Any]) -> None:
    """Do not count a source-location formula as an executable load/entry map."""
    model = image.get("mapping_model", {})
    if (image.get("mapping_status") == "parametric" and isinstance(model, dict)
            and model.get("mapping_role") == "flash_source"):
        fail("flash-source mapping proves source offsets only; executable image still needs a load/copy/XIP and entry mapping")


def signed_i32(value: int) -> int:
    if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
        fail("relative word is not an unsigned 32-bit value")
    return value if value < 0x80000000 else value - 0x100000000


def decode_iar3_descriptor(words: list[int], descriptor_runtime: int) -> dict[str, int]:
    """Decode this IAR three-word ABI; R9 relocation is deliberately unsupported."""
    if len(words) != 3 or any(type(word) is not int or not 0 <= word <= 0xFFFFFFFF for word in words):
        fail("IAR descriptor must contain exactly three uint32 words")
    displacement = signed_i32(words[0])
    relocation_flag = words[1] & 1
    if relocation_flag:
        fail("IAR descriptor R9 relocation flag is unsupported")
    compressed_size = words[1] >> 1
    if compressed_size <= 0:
        fail("IAR descriptor compressed source size is zero")
    source_runtime = descriptor_runtime + displacement
    if not 0 <= source_runtime < 0x100000000:
        fail("IAR descriptor signed source address overflows address space")
    return {"source_displacement": displacement, "compressed_size": compressed_size,
            "relocation_flag": relocation_flag, "source_runtime": source_runtime,
            "destination_runtime": words[2]}


def verify_iar3_mapping(words: list[int], descriptor_runtime: int, source_runtime: int,
                        source_size: int, output_size: int, destination_runtime: int,
                        dispatch_word_address: int, dispatch_relative_handler: int,
                        handler_runtime_entry: int) -> dict[str, int]:
    """Check signed descriptor/source/length/destination and enclosing-table handler links."""
    decoded = decode_iar3_descriptor(words, descriptor_runtime)
    if decoded["source_runtime"] != source_runtime:
        fail("IAR descriptor signed source offset disagrees with mapped source span")
    if decoded["compressed_size"] != source_size:
        fail("IAR descriptor compressed length disagrees with source span size")
    if output_size <= 0 or destination_runtime != decoded["destination_runtime"]:
        fail("IAR descriptor destination or decoded output size is invalid")
    table_handler = dispatch_word_address + signed_i32(dispatch_relative_handler)
    if table_handler != handler_runtime_entry:
        fail("IAR enclosing initialization table does not select the recorded handler")
    return decoded


def verify_iar3_fixed_record(payload_id: str, descriptor_runtime: int, words: list[int],
                             source_runtime: int, source_span: list[int], source_sha256: str,
                             output_size: int, output_sha256: str, destination_runtime: int,
                             dispatch_word_address: int, dispatch_relative_handler: int,
                             handler_runtime_entry: int, handler_sha256: str,
                             handler_runtime: int, handler_size: int) -> dict[str, Any]:
    """Admit only one of the six reviewed IAR3 tuples; never generalize the decoder."""
    expected = IAR3_FIXED_RECORDS.get((payload_id, descriptor_runtime))
    if expected is None:
        fail("IAR3 fixed recipe does not support this payload/descriptor scope")
    if (tuple(words) != expected["words"]
            or dispatch_relative_handler != expected["dispatch_word"]
            or source_runtime != expected["source_runtime"]
            or source_span != list(expected["source_span"])
            or source_sha256 != expected["source_sha256"]
            or output_size != expected["output_size"]
            or output_sha256 != expected["output_sha256"]
            or destination_runtime != expected["destination"]
            or handler_runtime_entry != expected["handler"]
            or handler_sha256 != expected["handler_sha256"]
            or handler_runtime != (expected["handler"] & ~1)
            or handler_size != 126):
        fail("IAR3 fixed recipe tuple differs from its pinned reviewed mapping")
    return expected


def verify_iar3_review_basis(basis: dict[str, Any], campaign_id: str, target_hash: str,
                             expected: dict[str, Any]) -> None:
    path, file_hash = expected["review"]
    if basis != {"path": path, "sha256": file_hash}:
        fail("IAR3 fixed transform lacks its exact pinned independent review basis")
    hash_bound_file(basis, "IAR3 fixed review basis")
    review = read_json(ROOT / path)
    if (review.get("campaign_id") != campaign_id or review.get("decision") != expected["decision"]
            or not review.get("reviewer")):
        fail("IAR3 fixed review basis has the wrong campaign or decision")
    if expected["review_kind"] == "apollo_main":
        if review.get("authenticated_input_hashes", {}).get("apollo_main", {}).get("sha256") != APOLLO_MAIN_SHA256:
            fail("Apollo main review basis does not bind the authenticated payload")
        trace_ref = review.get("authenticated_input_hashes", {}).get("independent_trace_results", {})
        trace_path = ROOT / trace_ref.get("path", "")
        if not trace_path.is_file() or sha256(trace_path) != trace_ref.get("sha256"):
            fail("Apollo main independent trace results are not hash-bound")
        trace = read_json(trace_path)
        found = [row for row in trace.get("records", []) if row.get("descriptor") == hex(expected["descriptor_runtime"])]
        if (len(found) != 1 or found[0].get("source_payload_span") != list(expected["source_span"])
                or found[0].get("output_size") != expected["output_size"]
                or found[0].get("output_sha256") != expected["output_sha256"]
                or found[0].get("source_effective_address_set_exact") is not True
                or found[0].get("all_backreferences_in_prior_output") is not True):
            fail("Apollo main independent trace does not support this fixed mapping")
    elif expected["review_kind"] == "bootloader":
        if review.get("authenticated_input_hashes", {}).get("authenticated_payload", {}).get("sha256") != BOOT_SHA256:
            fail("bootloader review basis does not bind the authenticated payload")
        trace_ref = review.get("authenticated_input_hashes", {}).get("review_trace_results", {})
        trace_path = ROOT / trace_ref.get("path", "")
        if not trace_path.is_file() or sha256(trace_path) != trace_ref.get("sha256"):
            fail("bootloader independent trace results are not hash-bound")
        trace = read_json(trace_path)
        idx = {0x4330F4: 0, 0x433104: 1, 0x433114: 2}[expected["descriptor_runtime"]]
        rows = trace.get("source_bound_traces", [])
        if (len(rows) != 3 or rows[idx].get("source_raw_span") != list(expected["source_span"])
                or rows[idx].get("executed_source_LDRB_count") != expected["output_source_size"]
                or rows[idx].get("out_of_span_loads") != 0
                or rows[idx].get("returned_to_sentinel") is not True):
            fail("bootloader independent review does not support this fixed source mapping")
    else:
        facts = review.get("authenticated_input", {})
        mapping = review.get("transform_mapping_result", {})
        if (facts.get("bundle_sha256") != target_hash or facts.get("apollo_main_sha256") != APOLLO_MAIN_SHA256
                or facts.get("source_descriptor") != "0x75d3e4"
                or mapping.get("observed_destination_sha256") != APOLLO_ITCM_OUTPUT_SHA256):
            fail("Apollo ITCM review004 does not support this fixed mapping")


def verify_fresh_main_execution(receipt: dict[str, Any], output: dict[str, Any],
                               descriptor_runtime: int) -> dict[str, Any]:
    """Bind the main RAM transform to its separately captured canonical replay."""
    ref = receipt.get("fresh_execution_receipt", {})
    expected_path = ("g2/build/pseudocode-first/20260930T190500Z/attempts/"
                     "P1-apollo-main-canonical-replay-009/001/execution-receipt.json")
    if not isinstance(ref, dict) or ref.get("path") != expected_path:
        fail("Apollo main RAM transform lacks the fresh canonical replay receipt")
    hash_bound_file(ref, "Apollo main fresh execution receipt")
    fresh = read_json(ROOT / expected_path)
    toolchain, execution = receipt.get("toolchain", {}), receipt.get("execution", {})
    if (fresh.get("schema_version") != 1 or fresh.get("campaign_id") != "20260930T190500Z"
            or fresh.get("source_payload", {}).get("sha256") != APOLLO_MAIN_SHA256
            or fresh.get("toolchain") != toolchain or fresh.get("execution") != execution):
        fail("Apollo main canonical execution provenance differs from the transform receipt")
    found = [row for row in fresh.get("outputs", []) if row.get("descriptor") == hex(descriptor_runtime)]
    if (len(found) != 1 or found[0].get("path") != output.get("path")
            or found[0].get("size") != output.get("size")
            or found[0].get("sha256") != output.get("sha256")):
        fail("Apollo main canonical replay output does not match the fixed transform")
    return ref


def partition(rows: list[dict[str, Any]], total: int, label: str) -> None:
    cursor = 0
    for row in sorted(rows, key=lambda x: x.get("start", -1)):
        start, end = row.get("start"), row.get("end")
        if type(start) is not int or type(end) is not int or start != cursor or end <= start or end > total:
            fail(f"{label}: gap, overlap, invalid or out-of-bounds span at {cursor}")
        if row.get("kind") not in KINDS:
            fail(f"{label}: unsupported coverage kind")
        if not row.get("evidence"):
            fail(f"{label}: missing interval evidence")
        cursor = end
    if cursor != total:
        fail(f"{label}: closes at {cursor}, expected {total}")


def parse_evenota(bundle: bytes, target: dict[str, Any], payloads: dict[str, bytes], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse and validate the authenticated EVENOTA table, headers and CRCs."""
    if len(bundle) < EVENOTA_TOC_OFFSET or bundle[:8] != b"EVENOTA\0":
        fail("authenticated bundle lacks EVENOTA header")
    version = bundle[0x30:0x40].split(b"\0", 1)[0].decode("ascii", errors="strict")
    package = manifest.get("package", {})
    if (manifest.get("schema_version") != 1 or package.get("format") != "EVENOTA"
            or package.get("expected_size") != target["bundle"]["size"]
            or package.get("expected_sha256") != target["bundle"]["sha256"]
            or version != target.get("version") or version != package.get("version")
            or bundle[0x10:0x20].split(b"\0", 1)[0].decode("ascii") != package.get("build_date")
            or bundle[0x20:0x30].split(b"\0", 1)[0].decode("ascii") != package.get("build_time")):
        fail("EVENOTA header version differs from target")
    count = struct.unpack_from("<I", bundle, 8)[0]
    components = target["components"]
    manifest_components = {c.get("name"): c for c in manifest.get("components", [])}
    if len(manifest_components) != 6 or set(manifest_components) != {c.get("id") for c in components}:
        fail("hash-pinned manifest component set differs from target")
    if count != 6 or count != len(components):
        fail("EVENOTA TOC must contain exactly six components")
    toc_end = EVENOTA_TOC_OFFSET + count * EVENOTA_TOC_ENTRY_SIZE
    trailer_end = toc_end + len(EVENOTA_TRAILER)
    if trailer_end > len(bundle) or bundle[toc_end:trailer_end] != EVENOTA_TRAILER:
        fail("EVENOTA TOC trailer missing or out of bounds")
    entries = []
    expected_offset = trailer_end
    seen_ids = set()
    for index, component in enumerate(components):
        mc = manifest_components[component["id"]]
        provider = mc.get("provider", {})
        if (mc.get("entry_id") != component.get("entry_id")
                or mc.get("package_filename") != component.get("package_filename")
                or provider.get("size") != component.get("size")
                or provider.get("sha256") != component.get("sha256")):
            fail(f"hash-pinned manifest disagrees with target component {component['id']}")
        toc_at = EVENOTA_TOC_OFFSET + index * EVENOTA_TOC_ENTRY_SIZE
        entry_id, offset, entry_size, checksum = struct.unpack_from("<IIII", bundle, toc_at)
        if entry_id != component.get("entry_id") or entry_id in seen_ids:
            fail("EVENOTA TOC entry IDs do not match target order")
        seen_ids.add(entry_id)
        if offset != expected_offset or entry_size < EVENOTA_HEADER_SIZE or offset + entry_size > len(bundle):
            fail("EVENOTA package entry span invalid or out of bounds")
        header_end = offset + EVENOTA_HEADER_SIZE
        end = offset + entry_size
        header, payload = bundle[offset:header_end], bundle[header_end:end]
        if len(payload) != component["size"] or payload != payloads[component["id"]]:
            fail(f"EVENOTA payload bytes do not match target: {component['id']}")
        if struct.unpack_from("<I", header, 8)[0] != len(payload):
            fail("EVENOTA component header size mismatch")
        if (struct.unpack_from("<I", header, 12)[0] != checksum or crc32c_msb(payload) != checksum
                or struct.unpack_from("<I", header, 0x14)[0] != EVENOTA_COMPONENT_MAGIC
                or struct.unpack_from("<I", header, 0x24)[0] != mc.get("type_id")
                or struct.unpack_from("<I", header, 0x28)[0] != mc.get("storage_type")
                or struct.unpack_from("<IIIIIII", header, 0)[0:2] != (0, 0)
                or struct.unpack_from("<I", header, 0x10)[0] != 0
                or struct.unpack_from("<II", header, 0x18) != (0xFFFFFFFF, 0xFFFFFFFF)
                or struct.unpack_from("<I", header, 0x20)[0] != 0
                or struct.unpack_from("<I", header, 0x2C)[0] != 0xFFFFFFFF):
            fail("EVENOTA component header or CRC mismatch")
        name = header[0x30:0x80].split(b"\0", 1)[0].decode("ascii", errors="strict")
        if name != component.get("package_filename"):
            fail("EVENOTA package filename mismatch")
        entries.append({"payload_id": component["id"], "package_offset": [offset, end],
                        "package_payload_span": [header_end, end], "payload_local_span": [0, len(payload)],
                        "checksum": checksum})
        expected_offset = end
    if expected_offset != len(bundle):
        fail("EVENOTA entries do not account for bundle EOF")
    return entries


def verify_identity(campaign: pathlib.Path, target: dict[str, Any], trusted_registry_sha256: str) -> tuple[dict[str, Any], dict[str, bytes], dict[str, Any]]:
    rec = read_json(campaign / "identity.json")
    target_hash = sha256(ROOT / "g2/workflow/target.json")
    if rec.get("campaign_id") != campaign.name or rec.get("target_id") != target["target_id"]:
        fail("identity campaign or target mismatch")
    if rec.get("target_sha256") != target["bundle"]["sha256"] or rec.get("target_lock_sha256") != target_hash:
        fail("identity target or target-lock hash mismatch")
    bundle = rec.get("bundle", {})
    bundle_path = ROOT / bundle.get("path", "")
    if bundle.get("sha256") != target["bundle"]["sha256"] or bundle.get("size") != target["bundle"]["size"]:
        fail("identity bundle receipt mismatch")
    if not bundle_path.is_file() or bundle_path.stat().st_size != bundle["size"] or sha256(bundle_path) != bundle["sha256"]:
        fail("authenticated bundle missing or mismatched")
    components = {c["id"]: c for c in target["components"]}
    if set(rec.get("components", {})) != set(components) or len(components) != 6:
        fail("identity must bind exactly six payloads")
    for cid, component in components.items():
        receipt = rec["components"][cid]
        path = ROOT / component["local_payload_path"]
        if (receipt.get("sha256") != component["sha256"] or receipt.get("size") != component["size"]
                or not path.is_file() or path.stat().st_size != component["size"]
                or sha256(path) != component["sha256"]):
            fail(f"payload identity mismatch: {cid}")
    manifest_sources = target.get("identity_sources", [])
    manifest_ref = next((item for item in manifest_sources if item.get("path", "").endswith("g2-2.2.6.10.json")), None)
    if manifest_ref is None:
        fail("target does not pin its package manifest")
    hash_bound_file(manifest_ref, "target manifest")
    manifest = read_json(ROOT / manifest_ref["path"])
    if manifest.get("package", {}).get("format") != target.get("format"):
        fail("hash-pinned manifest format differs from target")
    bundle_data = bundle_path.read_bytes()
    payload_data = {cid: (ROOT / component["local_payload_path"]).read_bytes() for cid, component in components.items()}
    entries = parse_evenota(bundle_data, target, payload_data, manifest)
    validation = rec.get("container_validation", {})
    outer_path = ROOT / validation["receipt_path"] if "receipt_path" in validation else campaign / "inventory" / "outer-container.json"
    if validation.get("status") != "passed" or validation.get("receipt_sha256") != sha256(outer_path):
        fail("outer-container identity receipt missing or mismatched")
    outer = read_json(outer_path)
    if outer.get("campaign_id") != campaign.name or outer.get("artifact_sha256") != target["bundle"]["sha256"]:
        fail("outer-container identity mismatch")
    if outer.get("parser_sha256") != sha256(ROOT / "g2/tools/open_cfw.py"):
        fail("outer-container parser hash differs from inspected parser")
    if outer.get("entry_spans") != entries:
        fail("outer-container declarations differ from authenticated EVENOTA parse")
    registry_ref = rec.get("review_registry")
    if not isinstance(registry_ref, dict):
        fail("coordinator authenticated review registry is required")
    if require_hash(trusted_registry_sha256, "trusted registry pin") != registry_ref.get("sha256"):
        fail("review registry hash does not match out-of-band trusted pin")
    hash_bound_file(registry_ref, "review registry")
    registry_path = ROOT / registry_ref["path"]
    registry = read_json(registry_path)
    if registry.get("campaign_id") != campaign.name or registry.get("status") != "authenticated":
        fail("review registry is not coordinator-authenticated for this campaign")
    identities = registry.get("reviewers", [])
    reviewers = {entry.get("reviewer_id") for entry in identities if entry.get("status") == "authenticated"}
    if not reviewers or len(reviewers) != len(identities):
        fail("review registry has missing or unauthenticated reviewer entries")
    receipts = registry.get("review_records", {})
    if not isinstance(receipts, dict):
        fail("authenticated registry lacks coordinator-observed review receipts")
    return outer, payload_data, {"reviewers": reviewers, "review_records": receipts, "payloads": payload_data,
                                 "bundle": bundle_data, "bundle_path": bundle.get("path")}


def verify(campaign: pathlib.Path, trusted_registry_sha256: str) -> None:
    target = read_json(ROOT / "g2/workflow/target.json")
    if (target.get("schema_version") != 1 or target.get("format") != "EVENOTA"
            or not isinstance(target.get("components"), list) or len(target["components"]) != 6
            or len({c.get("id") for c in target["components"]}) != 6
            or any(not all(c.get(k) for k in ("id", "entry_id", "package_filename",
                                               "local_payload_path", "sha256", "size")) for c in target["components"])):
        fail("target.json does not match required six-component EVENOTA schema")
    outer, payload_bytes, trust = verify_identity(campaign, target, trusted_registry_sha256)
    campaign_id = campaign.name
    target_hash = target["bundle"]["sha256"]
    components = {c["id"]: c for c in target["components"]}

    # Validate coordinate spaces independently before constructing partitions.
    package_rows = [{"start": 0, "end": EVENOTA_TOC_OFFSET, "kind": "container", "evidence": ["header"]},
                    {"start": EVENOTA_TOC_OFFSET, "end": EVENOTA_TOC_OFFSET + 6 * EVENOTA_TOC_ENTRY_SIZE,
                     "kind": "container", "evidence": ["entry table"]},
                    {"start": EVENOTA_TOC_OFFSET + 6 * EVENOTA_TOC_ENTRY_SIZE,
                     "end": EVENOTA_TOC_OFFSET + 6 * EVENOTA_TOC_ENTRY_SIZE + len(EVENOTA_TRAILER),
                     "kind": "container", "evidence": ["trailer"]}]
    package_rows += [{"start": e["package_offset"][0], "end": e["package_offset"][1],
                      "kind": "container", "evidence": [e["payload_id"]]} for e in outer["entry_spans"]]
    if {e.get("payload_id") for e in outer["entry_spans"]} != set(components):
        fail("outer container does not identify exactly six payloads")
    for e in outer["entry_spans"]:
        cid = e.get("payload_id")
        if cid not in components:
            fail("outer container references unknown payload")
        a, b = e.get("package_offset", []); x, y = e.get("package_payload_span", []); u, v = e.get("payload_local_span", [])
        if any(type(n) is not int for n in (a, b, x, y, u, v)):
            fail("EVENOTA span coordinates must be integers")
        if not (0 <= a < b <= target["bundle"]["size"] and a <= x < y <= b):
            fail("EVENOTA package span out of bounds")
        if not (0 <= u < v <= components[cid]["size"]):
            fail("payload-local span out of bounds")
        if y - x != v - u or (x, y) != (a + EVENOTA_HEADER_SIZE, b):
            fail("package payload span does not match EVENOTA component layout")
        if payload_bytes[cid][u:v] != trust["bundle"][x:y]:
            fail(f"package source bytes do not match extracted payload: {cid}")
    partition(package_rows, target["bundle"]["size"], "package container")
    images = read_jsonl(campaign / "inventory" / "images.jsonl")
    coverage = read_jsonl(campaign / "inventory" / "coverage.jsonl")
    reviews = read_jsonl(campaign / "inventory" / "reviews.jsonl")
    plan = read_json(campaign / "inventory" / "analysis-plan.json")
    for row in images + coverage + reviews:
        if row.get("schema_version") != SCHEMA or row.get("campaign_id") != campaign_id or not row.get("id"):
            fail("record schema/campaign/id mismatch")

    # Reviews bind canonical record bytes, evidence hashes, and the reviewed input artifact.
    review_by_id = {r["id"]: r for r in reviews}
    if len(review_by_id) != len(reviews):
        fail("duplicate review id")
    consumed_reviews: set[str] = set()
    def reviewed(review_id: str, record_type: str, record: dict[str, Any], inputs: set[str],
                 record_path: pathlib.Path, *, canonical_record: dict[str, Any] | None = None,
                 additional_required: set[tuple[str, str, str]] | None = None) -> dict[str, Any]:
        review = review_by_id.get(review_id)
        if not review or review.get("record_type") != record_type or review.get("record_id") != record["id"]:
            fail(f"missing matching review for {record_type}:{record.get('id')}")
        consumed_reviews.add(review_id)
        omitted = {"review_id", "accounting_review_id"}
        reviewed_value = canonical_record if canonical_record is not None else record
        if review.get("record_sha256") != canonical_hash(reviewed_value, omitted if canonical_record is None else set()):
            fail(f"reviewed record hash mismatch: {record['id']}")
        if trust["review_records"].get(review_id) != canonical_hash(review):
            fail(f"review receipt is not bound by the trusted coordinator registry: {review_id}")
        if (not review.get("author") or review.get("reviewer") not in trust["reviewers"]
                or review["author"] == review["reviewer"]):
            fail(f"reviewer must be independent: {record['id']}")
        if review.get("decision") != "pass":
            fail(f"review decision is not pass: {record['id']}")
        actual_pairs = {(x.get("role"), x.get("path"), x.get("sha256")) for x in review.get("input_hashes", [])}
        if not review.get("input_hashes"):
            fail(f"review has no input hashes: {record['id']}")
        for item in review["input_hashes"]:
            hash_bound_file(item, f"review:{record['id']}")
            if not item.get("role"):
                fail(f"review input lacks a role: {record['id']}")
        required = {("record", str(record_path.relative_to(ROOT)), sha256(record_path))}
        for item in record.get("evidence", []) if canonical_record is None else []:
            required.add(("evidence", item["path"], item["sha256"]))
        for item in record.get("source_evidence", []) if canonical_record is None else []:
            required.add(("source", item["path"], item["sha256"]))
        # Existing record schemas carry source hashes separately; require these
        # to be bound to the actual payload/image path for their role.
        if record_type == "image":
            image_cid = record["payload_id"]
            source_path = components[image_cid]["local_payload_path"] if record.get("parent_image_id") is None else image_by_id[record["parent_image_id"]]["content_path"]
            required.add(("source", source_path, record["source_sha256"]))
            required.add(("content", record["content_path"], record["content_sha256"]))
            if record.get("transform", {}).get("kind") == "decoded":
                receipt_ref = record["transform"].get("receipt", {})
                required.add(("transform_receipt", receipt_ref.get("path", ""), receipt_ref.get("sha256", "")))
        elif record_type == "coverage":
            scope = record["scope"]
            input_path = (trust["bundle_path"] if scope["kind"] == "package" else
                          components[scope["id"]]["local_payload_path"] if scope["kind"] == "payload" else
                          image_by_id[scope["id"]]["content_path"])
            expected_hash = (target_hash if scope["kind"] == "package" else
                             components[scope["id"]]["sha256"] if scope["kind"] == "payload" else
                             image_by_id[scope["id"]]["content_sha256"])
            required.add(("source", input_path, expected_hash))
        elif record_type == "analysis_plan":
            for plan_row in record.get("architecture_plans", []):
                for item in plan_row.get("evidence", []):
                    required.add(("evidence", item["path"], item["sha256"]))
        elif record_type == "discovery":
            for item in record.get("evidence", []):
                required.add(("evidence", item["path"], item["sha256"]))
        if additional_required:
            required.update(additional_required)
        if not required.issubset(actual_pairs):
            fail(f"review does not bind required path/hash roles: {record['id']}")
        return review

    image_by_id = {r["id"]: r for r in images}
    if len(image_by_id) != len(images) or not images:
        fail("images missing or duplicate image id")
    image_record_path = campaign / "inventory" / "images.jsonl"
    def bind_execution_contract_review(image: dict[str, Any], model: dict[str, Any]) -> None:
        """Use the coordinator registry path for the complete nested model review."""
        required_roles: set[tuple[str, str, str]] = set()
        source_path = (components[image["payload_id"]]["local_payload_path"]
                       if image.get("parent_image_id") is None
                       else image_by_id[image["parent_image_id"]]["content_path"])
        required_roles.add(("source", source_path, image["source_sha256"]))
        required_roles.add(("content", image["content_path"], image["content_sha256"]))
        for item in model.get("evidence", []):
            required_roles.add((f"execution_contract:{item['role']}", item["path"], item["sha256"]))
        review = reviewed(model["review_id"], "execution_contract", image, set(), image_record_path,
                          canonical_record=model, additional_required=required_roles)
        required_scope = {"conditional_mapping", "known_route_set", "external_premises_scoped"}
        if set(review.get("review_scope", [])) != required_scope:
            fail(f"execution_contract review lacks complete independent mapping scope: {image['id']}")

    image_sizes: dict[str, int] = {}
    image_bytes: dict[str, bytes] = {}
    roots_by_payload: dict[str, int] = {cid: 0 for cid in components}
    for image in images:
        cid = image.get("payload_id")
        if cid not in components:
            fail(f"unknown image payload: {cid}")
        if image.get("mapping_status") not in {"resolved", "container_only", "parametric", "conditional", "software_transfer", "execution_contract"}:
            fail(f"unresolved mapping facts: {image['id']}")
        if image.get("container_status", "resolved") not in {"resolved", "container_only"}:
            fail(f"unresolved container facts: {image['id']}")
        if image.get("parent_image_id") is not None and image["parent_image_id"] not in image_by_id:
            fail(f"missing parent image: {image['id']}")
        if image.get("parent_image_id") is not None and image_by_id[image["parent_image_id"]].get("payload_id") != cid:
            fail(f"nested image crosses payload ownership: {image['id']}")
        if image.get("parent_image_id") is None:
            roots_by_payload[cid] += 1
        source = image.get("source_span", [])
        if len(source) != 2 or any(type(n) is not int for n in source) or source[0] < 0 or source[1] <= source[0]:
            fail(f"invalid image source span: {image['id']}")
        if type(image.get("size")) is not int or image["size"] <= 0:
            fail(f"invalid decoded image size: {image['id']}")
        parent_data = (ROOT / components[cid]["local_payload_path"]).read_bytes() if image.get("parent_image_id") is None else image_bytes.get(image["parent_image_id"])
        parent_size = components[cid]["size"] if image.get("parent_image_id") is None else image_sizes.get(image["parent_image_id"])
        source_size = image.get("source_size")
        if (parent_size is None or source[1] > parent_size or type(source_size) is not int
                or source_size != source[1] - source[0]):
            fail(f"image source span outside parent: {image['id']}")
        if parent_data is None:
            fail(f"parent image bytes unavailable: {image['id']}")
        expected_source = components[cid]["sha256"] if image.get("parent_image_id") is None else image_by_id[image["parent_image_id"]]["content_sha256"]
        if image.get("source_sha256") != expected_source:
            fail(f"image source hash is not bound to parent bytes: {image['id']}")
        validate_mapping_model(image, image_by_id, components[cid]["size"], expected_source,
                               bind_execution_contract_review if image.get("mapping_status") == "execution_contract" else None)
        validate_image_load_mapping_requirement(image)
        image_sizes[image["id"]] = image["size"]
        content_path = image.get("content_path")
        cp = ROOT / content_path if content_path else None
        if cp is None or not cp.is_file():
            fail(f"image content file missing: {image['id']}")
        content = cp.read_bytes()
        if len(content) != image["size"] or sha256(cp) != image["content_sha256"]:
            fail(f"image content size/hash mismatch: {image['id']}")
        transform = image.get("transform", {})
        if not isinstance(transform, dict):
            fail(f"invalid transform description: {image['id']}")
        transform_review_inputs = None
        fresh_execution_ref = None
        if transform.get("kind") == "identity":
            if image.get("size") != source_size:
                fail(f"identity image source and decoded sizes differ: {image['id']}")
            if content != parent_data[source[0]:source[1]]:
                fail(f"identity image bytes do not match source span: {image['id']}")
        elif transform.get("kind") == "decoded":
            if transform.get("recipe_id") not in DECODED_RECIPES:
                fail(f"unsupported decoded transform recipe: {image['id']}")
            parent_id = image.get("parent_image_id")
            if parent_id is None:
                fail(f"decoded image requires an explicitly inventoried parent image: {image['id']}")
            receipt_ref = transform.get("receipt")
            if not isinstance(receipt_ref, dict):
                fail(f"decoded image receipt missing: {image['id']}")
            hash_bound_file(receipt_ref, f"decoded transform receipt:{image['id']}")
            receipt = read_json(ROOT / receipt_ref["path"])
            if (receipt.get("schema_version") != 1 or receipt.get("campaign_id") != campaign_id
                    or receipt.get("recipe_id") != transform["recipe_id"]):
                fail(f"decoded transform receipt identity mismatch: {image['id']}")
            source_receipt = receipt.get("source", {})
            parent_image = image_by_id[parent_id]
            parent_path = parent_image["content_path"]
            if (source_receipt.get("parent_image_id") != parent_id
                    or source_receipt.get("parent_content_path") != parent_path
                    or source_receipt.get("parent_content_sha256") != expected_source
                    or source_receipt.get("source_span") != source
                    or source_receipt.get("source_size") != source_size
                    or source_receipt.get("source_span_sha256") != hashlib.sha256(parent_data[source[0]:source[1]]).hexdigest()):
                fail(f"decoded transform source identity/span mismatch: {image['id']}")
            output_receipt = receipt.get("output", {})
            if (output_receipt.get("path") != content_path or output_receipt.get("size") != image["size"]
                    or output_receipt.get("sha256") != image["content_sha256"]
                    or output_receipt.get("size") != len(content)
                    or output_receipt.get("sha256") != hashlib.sha256(content).hexdigest()):
                fail(f"decoded transform output size/hash mismatch: {image['id']}")
            descriptor = receipt.get("descriptor", {})
            descriptor_image_id = descriptor.get("image_id")
            descriptor_image = image_by_id.get(descriptor_image_id)
            descriptor_span = descriptor.get("image_span")
            descriptor_runtime = descriptor.get("runtime_span")
            recipe_id = transform["recipe_id"]
            descriptor_width = 12 if recipe_id in {IAR3_RECIPE, IAR3_FIXED_RECIPE} else 16
            if (descriptor_image is None or descriptor_image.get("payload_id") != cid
                    or not isinstance(descriptor_span, list) or len(descriptor_span) != 2
                    or any(type(n) is not int for n in descriptor_span)
                    or descriptor_span[1] - descriptor_span[0] != descriptor_width
                    or not isinstance(descriptor_runtime, list) or len(descriptor_runtime) != 2
                    or any(type(n) is not int for n in descriptor_runtime)
                    or descriptor_runtime[1] - descriptor_runtime[0] != descriptor_width):
                fail(f"decoded transform descriptor location invalid: {image['id']}")
            descriptor_bytes = image_bytes.get(descriptor_image_id)
            if descriptor_bytes is None:
                descriptor_bytes = (ROOT / descriptor_image["content_path"]).read_bytes()
            if (mapped_runtime(descriptor_image, descriptor_span[0], descriptor_width, "descriptor") != descriptor_runtime[0]
                    or descriptor_span[1] > len(descriptor_bytes)
                    or hashlib.sha256(descriptor_bytes[descriptor_span[0]:descriptor_span[1]]).hexdigest() != descriptor.get("bytes_sha256")):
                fail(f"decoded transform descriptor bytes/mapping mismatch: {image['id']}")
            words = list(struct.unpack("<" + "I" * (descriptor_width // 4),
                                       descriptor_bytes[descriptor_span[0]:descriptor_span[1]]))
            if descriptor.get("words") != words:
                fail(f"decoded transform descriptor words mismatch: {image['id']}")
            handler = receipt.get("handler", {})
            handler_image = image_by_id.get(handler.get("image_id"))
            handler_span = handler.get("image_span")
            if (handler_image is None or handler_image.get("payload_id") != cid
                    or not isinstance(handler_span, list) or len(handler_span) != 2
                    or any(type(n) is not int for n in handler_span)
                    or handler_span[0] < 0 or handler_span[1] <= handler_span[0]):
                fail(f"decoded transform handler location invalid: {image['id']}")
            handler_bytes = image_bytes.get(handler["image_id"])
            if handler_bytes is None:
                handler_bytes = (ROOT / handler_image["content_path"]).read_bytes()
            handler_runtime = mapped_runtime(handler_image, handler_span[0], handler_span[1] - handler_span[0], "handler")
            if (handler_runtime != (handler.get("runtime_entry", -1) & ~1)
                    or handler_span[1] > len(handler_bytes)
                    or hashlib.sha256(handler_bytes[handler_span[0]:handler_span[1]]).hexdigest() != handler.get("bytes_sha256")):
                fail(f"decoded transform handler bytes/mapping mismatch: {image['id']}")
            arch_name = str(handler_image.get("architecture", {}).get("name", "")).lower()
            isa_mode = str(handler_image.get("architecture", {}).get("isa_mode", "")).lower()
            if ("arm" not in arch_name and "cortex" not in arch_name) or "thumb" not in isa_mode:
                fail(f"decoded handler does not match the supported Thumb recipe: {image['id']}")
            if recipe_id == "thumb-stock-handler-unicorn-v1":
                source_runtime = mapped_runtime(parent_image, source[0], source_size, "decoded source")
                destination_runtime = mapped_runtime(image, 0, image["size"], "decoded output")
                if words != [source_runtime, destination_runtime, image["size"], handler.get("runtime_entry")]:
                    fail(f"decoded transform descriptor disagrees with source/output/handler spans: {image['id']}")
            elif recipe_id in {IAR3_RECIPE, IAR3_FIXED_RECIPE}:
                if recipe_id == IAR3_RECIPE and (cid != "apollo_main" or components[cid]["sha256"] != APOLLO_MAIN_SHA256):
                    fail("Apollo IAR3 legacy recipe is pinned to the authenticated Apollo main payload")
                expected_record = None
                if recipe_id == IAR3_FIXED_RECIPE:
                    if ((cid == "apollo_main" and components[cid]["sha256"] != APOLLO_MAIN_SHA256)
                            or (cid == "apollo_bootloader" and components[cid]["sha256"] != BOOT_SHA256)):
                        fail("IAR3 fixed recipe payload does not match its locked firmware identity")
                    expected_record = IAR3_FIXED_RECORDS.get((cid, descriptor_runtime[0]))
                    if expected_record is None:
                        fail("IAR3 fixed recipe does not admit this payload or descriptor")
                dispatch = receipt.get("dispatch", {})
                dispatch_image = image_by_id.get(dispatch.get("image_id"))
                dispatch_span = dispatch.get("image_span")
                if (dispatch_image is None or dispatch_image["id"] != descriptor_image_id
                        or not isinstance(dispatch_span, list) or len(dispatch_span) != 2
                        or any(type(n) is not int for n in dispatch_span)
                        or dispatch_span != [descriptor_span[0] - 4, descriptor_span[0]]
                        or dispatch.get("runtime_address") != descriptor_runtime[0] - 4
                        or dispatch_span[0] < 0):
                    fail("Apollo IAR3 enclosing init-table handler selector is invalid")
                dispatch_image_bytes = image_bytes.get(dispatch_image["id"], descriptor_bytes)
                if dispatch_span[1] > len(dispatch_image_bytes):
                    fail("Apollo IAR3 handler selector is outside parent image")
                dispatch_word = struct.unpack_from("<I", dispatch_image_bytes, dispatch_span[0])[0]
                if (dispatch.get("relative_handler_word") != dispatch_word
                        or mapped_runtime(dispatch_image, dispatch_span[0], 4, "init-table handler selector") != dispatch["runtime_address"]):
                    fail("Apollo IAR3 handler selector bytes or mapping mismatch")
                source_runtime = mapped_runtime(parent_image, source[0], source_size, "decoded source")
                destination_runtime = mapped_runtime(image, 0, image["size"], "decoded output")
                mapping = verify_iar3_mapping(words, descriptor_runtime[0], source_runtime, source_size,
                    image["size"], destination_runtime, dispatch["runtime_address"], dispatch_word,
                    handler["runtime_entry"])
                if mapped_image_offset(parent_image, mapping["source_runtime"], mapping["compressed_size"], "IAR3 source") != source[0]:
                    fail("IAR3 signed-relative source resolves outside the declared parent source span")
                if recipe_id == IAR3_RECIPE:
                    if (descriptor_runtime[0] != 0x75D3E4 or words != [0x00036F2A, 0x0000002C, 0x00000040]
                            or not (APOLLO_INIT_TABLE_RUNTIME_SPAN[0] <= dispatch["runtime_address"]
                                    and descriptor_runtime[1] <= APOLLO_INIT_TABLE_RUNTIME_SPAN[1])
                            or mapping["source_runtime"] != 0x79430E or mapping["compressed_size"] != 22
                            or image["size"] != 24 or destination_runtime != 0x40
                            or handler["runtime_entry"] != 0x43A11F
                            or image["content_sha256"] != APOLLO_ITCM_OUTPUT_SHA256
                            or handler_runtime != 0x43A11E or handler_span[1] - handler_span[0] != 126
                            or handler["bytes_sha256"] != APOLLO_ITCM_HANDLER_SHA256):
                        fail("Apollo IAR3 evidence scope exceeds review004's fixed 22-byte to 24-byte ITCM transform")
                    basis = receipt.get("review_basis", {})
                    if basis != {"path": APOLLO_REVIEW_004_PATH, "sha256": APOLLO_REVIEW_004_SHA256}:
                        fail("Apollo IAR3 transform lacks the pinned narrow ITCM review004 basis")
                    hash_bound_file(basis, "Apollo review004 basis")
                    basis_record = read_json(ROOT / APOLLO_REVIEW_004_PATH)
                    facts = basis_record.get("authenticated_input", {})
                    mapped_facts = basis_record.get("transform_mapping_result", {})
                    if (basis_record.get("campaign_id") != campaign_id or basis_record.get("decision") != "pass"
                            or not basis_record.get("author") or not basis_record.get("reviewer")
                            or basis_record.get("author") == basis_record.get("reviewer")
                            or facts.get("bundle_sha256") != target_hash or facts.get("apollo_main_sha256") != APOLLO_MAIN_SHA256
                            or facts.get("source_descriptor") != "0x75d3e4"
                            or facts.get("source_stream_half_open") != ["0x79430e", "0x794324"]
                            or facts.get("source_stream_length") != 22 or facts.get("destination_start") != "0x40"
                            or facts.get("handler_entry") != "0x43a11f"
                            or mapped_facts.get("observed_destination_span") != ["0x40", "0x58"]
                            or mapped_facts.get("observed_destination_length") != 24
                            or mapped_facts.get("observed_destination_sha256") != APOLLO_ITCM_OUTPUT_SHA256):
                        fail("Apollo review004 does not pass the pinned narrow transform scope")
                else:
                    root_origin = parent_image.get("source_span")
                    if (parent_image.get("parent_image_id") is not None
                            or parent_image.get("transform", {}).get("kind") != "identity"
                            or not isinstance(root_origin, list) or len(root_origin) != 2
                            or any(type(n) is not int for n in root_origin)):
                        fail("IAR3 fixed recipe source must map directly through an authenticated identity root")
                    component_source = [source[0] + root_origin[0], source[1] + root_origin[0]]
                    if (source[1] - source[0] != mapping["compressed_size"]
                            or component_source != list(expected_record["source_span"])):
                        fail("IAR3 fixed source span/size differs from the reviewed tuple")
                    checked = verify_iar3_fixed_record(cid, descriptor_runtime[0], words,
                        source_runtime, component_source, source_receipt["source_span_sha256"], image["size"],
                        image["content_sha256"], destination_runtime, dispatch["runtime_address"],
                        dispatch_word, handler["runtime_entry"], handler["bytes_sha256"],
                        handler_runtime, handler_span[1] - handler_span[0])
                    verify_iar3_review_basis(receipt.get("review_basis", {}), campaign_id,
                                             target_hash, checked)
                    if checked["review_kind"] == "apollo_main" and descriptor_runtime[0] in {0x75D3F4, 0x75D404}:
                        fresh_execution_ref = verify_fresh_main_execution(receipt, output_receipt,
                                                                           descriptor_runtime[0])
            toolchain = receipt.get("toolchain", {})
            python_tool = toolchain.get("python", {})
            script = toolchain.get("script", {})
            if not all(isinstance(item, dict) for item in (python_tool, script)):
                fail(f"decoded transform tool/script receipt missing: {image['id']}")
            hash_bound_file(python_tool, f"decoded transform Python:{image['id']}")
            hash_bound_file(script, f"decoded transform script:{image['id']}")
            if not python_tool.get("version"):
                fail(f"decoded transform Python version missing: {image['id']}")
            libraries = toolchain.get("libraries")
            if not isinstance(libraries, list) or not libraries:
                fail(f"decoded transform library hashes missing: {image['id']}")
            for library in libraries:
                hash_bound_file(library, f"decoded transform library:{image['id']}")
                if not library.get("name") or not library.get("version"):
                    fail(f"decoded transform library identity incomplete: {image['id']}")
            if not any(item.get("name", "").lower() == "unicorn" for item in libraries):
                fail(f"decoded stock-handler receipt lacks Unicorn library identity: {image['id']}")
            execution = receipt.get("execution", {})
            actual_argv = execution.get("argv")
            if (not isinstance(actual_argv, list) or len(actual_argv) < 2
                    or any(not isinstance(arg, str) for arg in actual_argv)
                    or actual_argv[:2] != [python_tool["path"], script["path"]]
                    or type(execution.get("exit_code")) is not int
                    or execution.get("exit_code") != 0):
                fail(f"decoded transform actual argv/exit receipt mismatch: {image['id']}")
            for stream_name in ("stdout", "stderr"):
                hash_bound_file(execution.get(stream_name, {}), f"decoded transform {stream_name}:{image['id']}")
            transform_review_inputs = {
                ("transform_receipt", receipt_ref["path"], receipt_ref["sha256"]),
                ("source", parent_path, expected_source),
                ("output", content_path, image["content_sha256"]),
                ("descriptor", descriptor_image["content_path"], descriptor_image["content_sha256"]),
                ("handler", handler_image["content_path"], handler_image["content_sha256"]),
                ("tool", python_tool["path"], python_tool["sha256"]),
                ("script", script["path"], script["sha256"]),
                ("stdout", execution["stdout"]["path"], execution["stdout"]["sha256"]),
                ("stderr", execution["stderr"]["path"], execution["stderr"]["sha256"]),
            }
            transform_review_inputs.update(("library", item["path"], item["sha256"]) for item in libraries)
            if recipe_id in {IAR3_RECIPE, IAR3_FIXED_RECIPE}:
                basis = receipt["review_basis"]
                transform_review_inputs.add(("review_basis", basis["path"], basis["sha256"]))
            if fresh_execution_ref is not None:
                transform_review_inputs.add(("fresh_execution", fresh_execution_ref["path"],
                                             fresh_execution_ref["sha256"]))
        else:
            fail(f"unsupported transform kind: {image['id']}")
        image_bytes[image["id"]] = content
        arch = image.get("architecture", {})
        if not all(arch.get(k) for k in ("name", "endianness", "isa_mode")):
            fail(f"architecture facts missing: {image['id']}")
        spaces = image.get("address_spaces", [])
        if image.get("mapping_status") == "resolved" and not spaces:
            fail(f"resolved image has no address-space mapping: {image['id']}")
        if image.get("mapping_status") != "resolved" and spaces:
            fail(f"non-numeric mapping model must not declare fixed address spaces: {image['id']}")
        for space in spaces:
            maps = space.get("mappings", [])
            if not space.get("id") or not maps:
                fail(f"incomplete address-space mapping: {image['id']}")
            for m in maps:
                if any(type(m.get(k)) is not int for k in ("image_start", "image_end", "loaded_start", "loaded_end")):
                    fail(f"non-integer mapping bounds: {image['id']}")
                if (m["image_start"] < 0 or m["image_end"] <= m["image_start"] or m["image_end"] > image["size"]
                        or m["loaded_start"] < 0 or m["loaded_end"] <= m["loaded_start"]
                        or m["image_end"] - m["image_start"] != m["loaded_end"] - m["loaded_start"]):
                    fail(f"invalid file-to-loaded-address bounds: {image['id']}")
        image_evidence = image.get("evidence", [])
        if not image_evidence:
            fail(f"image lacks hash-bound source evidence: {image['id']}")
        for ev in image_evidence:
            hash_bound_file(ev, f"image:{image['id']}")
            if ev.get("input_sha256") != expected_source:
                fail(f"image evidence is not bound to source bytes: {image['id']}")
        review_inputs = {image["source_sha256"], image["content_sha256"], *(ev["sha256"] for ev in image_evidence)}
        image_review = reviewed(image.get("accounting_review_id", ""), "image", image, review_inputs,
                                campaign / "inventory" / "images.jsonl")
        if transform.get("kind") == "decoded":
            transform_review_id = transform.get("review_id")
            if not isinstance(transform_review_id, str) or not transform_review_id:
                fail(f"decoded transform lacks independent pass review: {image['id']}")
            reviewed(transform_review_id, "transform", image, set(),
                     campaign / "inventory" / "images.jsonl",
                     canonical_record=transform,
                     additional_required=transform_review_inputs or set())

    # Whole-package and six payload ledgers, plus a full byte ledger per listed image.
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    coverage_ids: set[str] = set()
    for row in coverage:
        if row["id"] in coverage_ids:
            fail("duplicate coverage record id")
        coverage_ids.add(row["id"])
        scope = row.get("scope", {})
        kind, ident = scope.get("kind"), scope.get("id")
        if kind not in {"package", "payload", "image"}:
            fail("invalid coverage scope")
        if kind == "payload" and ident not in components or kind == "image" and ident not in image_by_id:
            fail("coverage references unknown payload/image")
        grouped.setdefault((kind, ident), []).append(row)
        evidence_hashes = {target_hash if kind == "package" else
                           components[ident]["sha256"] if kind == "payload" else image_by_id[ident]["content_sha256"]}
        for ev in row.get("evidence", []):
            hash_bound_file(ev, f"coverage:{row['id']}")
            require_hash(ev.get("input_sha256"), f"coverage input:{row['id']}")
            expected_input = target_hash if kind == "package" else components[ident]["sha256"] if kind == "payload" else image_by_id[ident]["content_sha256"]
            if ev["input_sha256"] != expected_input:
                fail(f"coverage evidence is not bound to its scope bytes: {row['id']}")
            evidence_hashes.add(ev["sha256"])
        if not row.get("evidence"):
            fail(f"coverage evidence missing: {row['id']}")
        reviewed(row.get("review_id", ""), "coverage", row, evidence_hashes,
                 campaign / "inventory" / "coverage.jsonl")
    expected_scopes = {("package", "package")} | {("payload", cid) for cid in components} | {("image", iid) for iid in image_by_id}
    if set(grouped) != expected_scopes:
        fail("missing package, payload, or explicit nested-image byte accounting")
    partition(grouped[("package", "package")], target["bundle"]["size"], "package coverage")
    for cid, component in components.items():
        partition(grouped[("payload", cid)], component["size"], f"payload {cid}")
    for iid, image in image_by_id.items():
        partition(grouped[("image", iid)], image["size"], f"image {iid}")
    if any(count == 0 for count in roots_by_payload.values()):
        fail("images.jsonl must contain an explicit root inventory record for all six payloads")

    if plan.get("schema_version") != SCHEMA or plan.get("campaign_id") != campaign_id or plan.get("id") != "analysis-plan" or plan.get("target_sha256") != target_hash:
        fail("analysis plan identity mismatch")
    plans = plan.get("architecture_plans", [])
    if {p.get("payload_id") for p in plans} != set(components) or len(plans) != 6:
        fail("analysis plan must contain exactly six payload architecture plans")
    for p in plans:
        if not all(p.get(k) for k in ("architecture", "endianness", "isa_mode", "address_spaces")):
            fail(f"architecture plan incomplete: {p.get('payload_id')}")
        if p.get("decoder_support") not in {"verified", "planned_with_local_decoder", "unsupported_pending"}:
            fail(f"invalid decoder support statement: {p.get('payload_id')}")
        for ev in p.get("evidence", []):
            hash_bound_file(ev, f"analysis plan:{p.get('payload_id')}")
            if ev.get("input_sha256") != components[p["payload_id"]]["sha256"]:
                fail(f"architecture evidence is not bound to payload: {p.get('payload_id')}")
        if not p.get("evidence"):
            fail(f"architecture plan lacks evidence: {p.get('payload_id')}")
    # A separately reviewed discovery-reconciliation receipt is required for
    # each payload. It is an evidence-backed completeness claim, not proof the
    # validator can derive by scanning arbitrary firmware encodings.
    discoveries = read_jsonl(campaign / "inventory" / "discovery-reconciliation.jsonl")
    if len(discoveries) != 6 or {d.get("payload_id") for d in discoveries} != set(components):
        fail("discovery reconciliation must cover exactly six payloads")
    listed_ids = {iid for d in discoveries for iid in d.get("image_ids", [])}
    if listed_ids != set(image_by_id):
        fail("discovery reconciliation image IDs differ from images.jsonl")
    for discovery in discoveries:
        expected_for_payload = {iid for iid, image in image_by_id.items() if image.get("payload_id") == discovery.get("payload_id")}
        if len(discovery.get("image_ids", [])) != len(set(discovery.get("image_ids", []))) or set(discovery.get("image_ids", [])) != expected_for_payload:
            fail(f"discovery image IDs do not match payload inventory: {discovery.get('payload_id')}")
    for discovery in discoveries:
        if (discovery.get("schema_version") != SCHEMA or discovery.get("campaign_id") != campaign_id
                or discovery.get("unresolved") != [] or not discovery.get("evidence")):
            fail(f"discovery reconciliation unresolved or malformed: {discovery.get('payload_id')}")
        for ev in discovery["evidence"]:
            hash_bound_file(ev, f"discovery:{discovery['payload_id']}")
            if ev.get("input_sha256") != components[discovery["payload_id"]]["sha256"]:
                fail("discovery evidence is not bound to payload bytes")
        reviewed(discovery.get("review_id", ""), "discovery", discovery, set(),
                 campaign / "inventory" / "discovery-reconciliation.jsonl")
    reviewed(plan.get("review_id", ""), "analysis_plan", plan, set(),
             campaign / "inventory" / "analysis-plan.json")
    if consumed_reviews != set(review_by_id):
        fail("reviews.jsonl contains unreferenced review records")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=pathlib.Path)
    parser.add_argument("--trusted-review-registry-sha256", required=True,
                        help="coordinator-supplied out-of-band SHA-256 pin for the authenticated reviewer registry")
    args = parser.parse_args()
    try:
        verify(args.campaign if args.campaign.is_absolute() else ROOT / args.campaign,
               args.trusted_review_registry_sha256)
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS: P1 inventory records are internally consistent and reviewed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
