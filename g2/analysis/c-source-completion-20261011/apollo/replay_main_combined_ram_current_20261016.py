#!/usr/bin/env python3
"""Replay receipt-linked Main bindings from the combined RAM post-tail object."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BUILD = G2 / "build/c-firmware"
START = "g2/build/c-firmware/20261015/main-test-screen-registry-context-min/apollo-main-test-screen-registry-context-min.o"
END = "g2/build/c-firmware/20261016/main-terminal-rx-frame-5ce990/apollo-main-rx-frame-bound.o"
TAIL_RECEIPT = BUILD / "20261016/main-combined-ram-post-tail-replay/receipt.json"
OUT = BUILD / "20261016/main-combined-ram-current-replay"
ADDED = {"audio_registry_ring_connect_buffer", "audio_terminal_ui_state_base"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(name, digest):
    path = ROOT / name
    if sha(path) != digest:
        raise RuntimeError(f"artifact changed: {name}")
    return path


def names(path, *options):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *options, str(path)], text=True).splitlines()
        if line.strip()}


def graph():
    by_link = {}
    for day in ("20261015", "20261016"):
        for path in (BUILD / day).glob("**/*receipt.json"):
            try:
                row = json.loads(path.read_text())
            except (ValueError, OSError):
                continue
            if isinstance(row, dict) and row.get("base_object") and row.get("linked_object"):
                key = row["linked_object"]
                if key in by_link:
                    raise RuntimeError(f"duplicate linked receipt: {key}")
                by_link[key] = (path, row)
    result = []
    cursor = END
    while cursor != START:
        if cursor not in by_link or len(result) > 300:
            raise RuntimeError(f"incomplete Main receipt chain: {cursor}")
        path, row = by_link[cursor]
        result.append((path, row))
        cursor = row["base_object"]
    return list(reversed(result))


def object_inputs(path, row):
    objects = []
    for key, hash_key in (("object", "object_sha256"),
                          ("asset_object", "asset_object_sha256"),
                          ("assets_object", "assets_object_sha256"),
                          ("image_object", "image_object_sha256"),
                          ("icon_object", "icon_object_sha256"),
                          ("source_object", "source_object_sha256"),
                          ("action_object", "action_object_sha256"),
                          ("timer_object", "timer_object_sha256"),
                          ("wrapper_object", "wrapper_object_sha256"),
                          ("callback_object", "callback_object_sha256"),
                          ("constructor_object", "constructor_object_sha256"),
                          ("provider_object", "provider_sha256"),
                          ("ram_object", "ram_object_sha256"),
                          ("dispatch_object", "dispatch_object_sha256"),
                          ("placed_table_object", "placed_table_sha256")):
        if key in row:
            objects.append(checked(row[key], row[hash_key]))
    if "objects" in row:
        value = row["objects"]
        if isinstance(value, list):
            if value and isinstance(value[0], str):
                digests = row.get("object_sha256")
                if not isinstance(digests, list) or len(digests) != len(value):
                    raise RuntimeError(f"object hash list changed: {path}")
                objects.extend(checked(name, digest)
                               for name, digest in zip(value, digests))
            else:
                objects.extend(checked(item["path"], item["sha256"])
                               for item in value)
        elif isinstance(value, dict):
            objects.extend(checked(name, digest) for name, digest in value.items())
        else:
            raise RuntimeError(f"invalid object manifest: {path}")
    if not objects and "sources" in row and isinstance(row["sources"], list):
        for source_index, item in enumerate(row["sources"]):
            if isinstance(item, str):
                digest = row.get("source_sha256")
                if not isinstance(digest, list) or len(digest) != len(row["sources"]):
                    raise RuntimeError(f"source hash list changed: {path}")
                checked(item, digest[source_index])
                obj = path.parent / (Path(item).stem + ".o")
                if not obj.is_file():
                    raise RuntimeError(f"source object missing: {obj}")
                objects.append(obj)
                continue
            if "object" in item:
                objects.append(checked(item["object"], item["object_sha256"]))
            elif "object_sha256" in item:
                obj = path.parent / (Path(item["path"]).stem + ".o")
                if sha(obj) != item["object_sha256"]:
                    raise RuntimeError(f"source object changed: {obj}")
                objects.append(obj)
    if not objects and isinstance(row.get("source"), list):
        for item in row["source"]:
            checked(item["path"], item["sha256"])
            obj = path.parent / (Path(item["path"]).stem + ".o")
            if not obj.is_file():
                raise RuntimeError(f"compiled source object missing: {obj}")
            objects.append(obj)
    if "nanopb_archive" in row:
        objects.append(checked(row["nanopb_archive"], row["nanopb_archive_sha256"]))
    if not objects and isinstance(row.get("object_sha256"), str):
        matches = [obj for obj in path.parent.glob("*.o")
                   if sha(obj) == row["object_sha256"]]
        if len(matches) != 1:
            raise RuntimeError(f"object hash missing or ambiguous: {path}")
        objects.append(matches[0])
    seen = set()
    return [obj for obj in objects if not (str(obj) in seen or seen.add(str(obj)))]


def main():
    tail = json.loads(TAIL_RECEIPT.read_text())
    if tail["status"] != "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_POST_TAIL_REPLAY_C" or \
            tail["stage_count"] != 444 or tail["unresolved_after"] != 182:
        raise RuntimeError("combined post-tail input changed")
    current = checked(tail["linked_object"], tail["linked_sha256"])
    chain = graph()
    if len(chain) != 239:
        raise RuntimeError("later Main stage count changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stages = []
    for index, (path, row) in enumerate(chain, 1):
        digest = row.get("linked_sha256", row.get("linked_object_sha256"))
        baseline = checked(row["linked_object"], digest)
        objects = object_inputs(path, row)
        aliases = row.get("same_entry_aliases", row.get("aliases", {}))
        if "linker_alias" in row:
            name, provider = row["linker_alias"].split("=", 1)
            aliases[name] = provider
        target = OUT / f"{index:03d}-{path.parent.name}.o"
        if not objects and not aliases:
            if row.get("imports_resolved") or row.get("imports_added"):
                raise RuntimeError(f"missing replay inputs: {path}")
            shutil.copyfile(current, target)
        else:
            subprocess.run(["arm-none-eabi-ld", "-r", str(current),
                            *(str(obj) for obj in objects),
                            *(f"--defsym={name}={provider}"
                              for name, provider in aliases.items()),
                            "-o", str(target)], check=True)
        old_u, new_u = names(baseline, "-u"), names(target, "-u")
        old_d = names(baseline, "-g", "--defined-only")
        new_d = names(target, "-g", "--defined-only")
        resolved = old_u & ADDED
        if old_u - new_u != resolved or new_u - old_u or \
                new_d - old_d != ADDED or old_d - new_d:
            raise RuntimeError(f"unexpected combined replay delta at {index} {path.parent.name}: "
                               f"imports {old_u-new_u}, {new_u-old_u}; "
                               f"providers {new_d-old_d}, {old_d-new_d}")
        stages.append({"stage": path.parent.name, "receipt": str(path.relative_to(ROOT)),
                       "receipt_sha256": sha(path),
                       "baseline": row["linked_object"], "baseline_sha256": digest,
                       "linked": str(target.relative_to(ROOT)), "linked_sha256": sha(target),
                       "objects": {str(obj.relative_to(ROOT)): sha(obj) for obj in objects},
                       "aliases": aliases,
                       "imports_resolved_vs_baseline": sorted(resolved),
                       "providers_added_vs_baseline": sorted(ADDED),
                       "imports_remaining": len(new_u)})
        current = target
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_CURRENT_REPLAY_C",
               "replay_script": str(Path(__file__).resolve().relative_to(ROOT)),
               "replay_script_sha256": sha(Path(__file__).resolve()),
               "post_tail_receipt": str(TAIL_RECEIPT.relative_to(ROOT)),
               "post_tail_receipt_sha256": sha(TAIL_RECEIPT),
               "stage_count": len(stages), "stages": stages,
               "linked_object": str(current.relative_to(ROOT)),
               "linked_sha256": sha(current),
               "unresolved_after": stages[-1]["imports_remaining"],
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Replay reaches the October 16 RX-frame branch; final RAM placement, remaining imports, whole-image link and hardware operation remain open."]}
    output = OUT / "receipt.json"
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], receipt["stage_count"],
          receipt["unresolved_after"], sha(output))


if __name__ == "__main__":
    main()
