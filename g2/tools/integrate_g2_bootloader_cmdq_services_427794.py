#!/usr/bin/env python3
"""Register the reviewed G2 bootloader command-queue service family.

This tool updates source-ownership metadata only.  It never signs, flashes, or
communicates with hardware.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_cmdq_services_427794.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
BOOT_BASE = 0x00410000
UPDATER = "open_cfw_bootloader_cmdq_update_indices_427754"
UPDATER_ADDRESS = 0x00427754

FLAGS = [
    "-mcpu=cortex-m55",
    "-mthumb",
    "-Oz",
    "-ffreestanding",
    "-fno-builtin",
    "-ffunction-sections",
    "-fdata-sections",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-Wall",
    "-Wextra",
    "-Werror",
    "-fno-ident",
    "-mllvm",
    "-enable-machine-outliner=never",
]

# function, start, full stock end, full stock SHA, optional updater-call offset,
# Apple(size, relocated SHA, unrelocated SHA, stock-prefix SHA),
# Linux(size, relocated SHA, unrelocated SHA, stock-prefix SHA)
SERVICES = (
    (
        "open_cfw_bootloader_cmdq_init_427794", 0x00427794, 0x00427878,
        "ad7e3d6257b791855a8cd7fe90389313dfb9496262724777900d6a4193c09b52", None,
        (184, "3c8afb0ce303e98a857377cca97fc803374fd844cb53aabf13141d4f4f4fbcd4", "3c8afb0ce303e98a857377cca97fc803374fd844cb53aabf13141d4f4f4fbcd4", "4585f3cd240ac64fbea2544a98b3029661232854b291d1dbb0f9705cda37080e"),
        (176, "a9665ff8db82be43551e53535af9dc6079f8c79ee501f781a8ea9a6da39245ac", "a9665ff8db82be43551e53535af9dc6079f8c79ee501f781a8ea9a6da39245ac", "3dc7e26e9d12ec938e4ac1cdbed9d6e857c5a093614fa99090ff21c76ec1094d"),
    ),
    (
        "open_cfw_bootloader_cmdq_enable_427878", 0x00427878, 0x004278C8,
        "7564cbb55095105d158e045e602b9765e60c6c976503911d40b4155aac0fd425", None,
        (68, "f06fde8d9bdee95cad617c36d1ad9dcf5dd85087f1d6f3e1099ee6a5f8ca58c5", "f06fde8d9bdee95cad617c36d1ad9dcf5dd85087f1d6f3e1099ee6a5f8ca58c5", "0900272f9c71d2a7f225b835d090ab53ab8fdb1aa4a7df52cb07bffe6d1134cb"),
        (68, "f06fde8d9bdee95cad617c36d1ad9dcf5dd85087f1d6f3e1099ee6a5f8ca58c5", "f06fde8d9bdee95cad617c36d1ad9dcf5dd85087f1d6f3e1099ee6a5f8ca58c5", "0900272f9c71d2a7f225b835d090ab53ab8fdb1aa4a7df52cb07bffe6d1134cb"),
    ),
    (
        "open_cfw_bootloader_cmdq_disable_4278c8", 0x004278C8, 0x0042790A,
        "e551b7b0af10daaeae0056297928d36e9754c6cb212984e37afc0d3bb7354651", None,
        (52, "81ba64db3322e3ba638c263f7c540ee815bbd9165d054b963812da24e35166d4", "81ba64db3322e3ba638c263f7c540ee815bbd9165d054b963812da24e35166d4", "40e73674a02a27f57580d575d843bd83fc4cafde8c93c8d8fafcdf05393139d6"),
        (52, "81ba64db3322e3ba638c263f7c540ee815bbd9165d054b963812da24e35166d4", "81ba64db3322e3ba638c263f7c540ee815bbd9165d054b963812da24e35166d4", "40e73674a02a27f57580d575d843bd83fc4cafde8c93c8d8fafcdf05393139d6"),
    ),
    (
        "open_cfw_bootloader_cmdq_alloc_block_42790a", 0x0042790A, 0x004279BE,
        "74a57509503aa339dce2f40cdbff6d283585b7eac2f526c7d4939548e55baa3c", 38,
        (148, "7c9b9bd67859beb885ab36dfa0b4fbf97fbab98450e7cf5564c357ef332a2abb", "7b1af0db936c40ed6e1f89095ce96561b9aaa5eadd59b842ab192a05e77d5eb1", "8cc57bcc418fcec85783b0ddb0caf359960eaa853bf6ea8a2810cc6faf442eca"),
        (148, "7ba24d5266706d5c43f5cf682277342d59eea1180a9fabe6e0cfe13d3cfb74df", "e000ad1344714d33fb5e932a055826d1d1c1602e5acd56a56d0fb9f38711744b", "8cc57bcc418fcec85783b0ddb0caf359960eaa853bf6ea8a2810cc6faf442eca"),
    ),
    (
        "open_cfw_bootloader_cmdq_release_block_4279be", 0x004279BE, 0x004279F0,
        "fe6aa75bf496d31d548a672df580b21d9be19bb36a4d412b6ab08c72ed0371a8", None,
        (48, "228c34b661f47b4715d3c23751436171d5840f95f47634a047424ccde8b22dda", "228c34b661f47b4715d3c23751436171d5840f95f47634a047424ccde8b22dda", "96890176fec41f0052e82586dbac6893f9a49080daba538f789ae5d92130237c"),
        (48, "2832fdcd4fbb41565a521c934285194c4b473fc31694842f2aeedc1a5e31c841", "2832fdcd4fbb41565a521c934285194c4b473fc31694842f2aeedc1a5e31c841", "96890176fec41f0052e82586dbac6893f9a49080daba538f789ae5d92130237c"),
    ),
    (
        "open_cfw_bootloader_cmdq_post_block_4279f0", 0x004279F0, 0x00427A56,
        "457794f4df1853b69f6e267d49376d35858cf949ea4f990881492be01e3ee359", None,
        (92, "c3d76d042a275386ecb27fcf9b4881d80240726513b4fef8a3d84b77f30308d5", "c3d76d042a275386ecb27fcf9b4881d80240726513b4fef8a3d84b77f30308d5", "f04a57c2f9f58a7cd8accc264748cb672de4e0663b6ec61f53a79125bc7e8d85"),
        (88, "22100c69e69ca38db17456bb3c0cf14dc1f73bb6bf7e116913ba0a5166ee00c8", "22100c69e69ca38db17456bb3c0cf14dc1f73bb6bf7e116913ba0a5166ee00c8", "38d6add34de07fc94fef5d4e9f4c8a1437fd5ad0f54f04b50ffe700e19b2b75e"),
    ),
    (
        "open_cfw_bootloader_cmdq_get_status_427a56", 0x00427A56, 0x00427AD6,
        "54f4dd9239da03fdb828d767378d1650218cb59a76e2f1cc57e628ff0bac9cd4", 24,
        (104, "88a7f28e7090d0109e59658cab9cbc460d4457af0c10f750f53da95274973342", "1cc4b4d8b5ce51873821922b0c5d1c542247a1c4c62d9b7d16bd049eab3cb5c5", "b24b7c41f409a0c28684c5756ee856775ac648661b8c660b1e5145d0f0ff0649"),
        (108, "7e2f6c043a8eed632b2410f3015ac30f1a874e873d8a447fb5eb2be93fd402b0", "45e1c5b33f9a43a08f4c043c19037b48af232b6c89012087c31cd312b72676f2", "78b629041674a9dbea3f10006947bf7a1e798cf0ed1958a63241e488b6171b06"),
    ),
    (
        "open_cfw_bootloader_cmdq_term_427ad6", 0x00427AD6, 0x00427B38,
        "7b9043e48ae0dd5f4e067a1f0884e7696abcc0bbd570b345a76391a8de201bad", 22,
        (88, "79febaa0d9a3240a90a559cbbcd7e7de01106777d749083ee49a7d4486210e29", "af2bea8c0e82800efa35ba2b347cd31a1b9ec912be1697193dc771268c3261f3", "b22a10aa2155b78c874c577fcb075a63b07f056e9f6da2a4dcce557051926df4"),
        (88, "10112f17b0ac36dd5e93419361e5ffb71698d1a5e57816d7122ed6ffdf3718a6", "19a3e4ab4315ba63ff4d2a8b065018a641698a2020df3555f68c32a54d179448", "b22a10aa2155b78c874c577fcb075a63b07f056e9f6da2a4dcce557051926df4"),
    ),
    (
        "open_cfw_bootloader_cmdq_error_resume_427b38", 0x00427B38, 0x00427BAA,
        "bf382cf043bcfbd2443bb5c687740f48d4f970d90119ce671859e6852a4e33b7", None,
        (88, "ada58e044510d4073485f9fe2a43fbedeb653c64703e9d7b506b45532c1027f6", "ada58e044510d4073485f9fe2a43fbedeb653c64703e9d7b506b45532c1027f6", "ff979acdf07007286d4a92c72a4b158a22cfc7a694d52e56e62287dc646d2158"),
        (88, "b25cfce5926696af43dcd0ecf232d460a65d7281b1882b1a2a16195084598b1c", "b25cfce5926696af43dcd0ecf232d460a65d7281b1882b1a2a16195084598b1c", "ff979acdf07007286d4a92c72a4b158a22cfc7a694d52e56e62287dc646d2158"),
    ),
    (
        "open_cfw_bootloader_cmdq_reset_427baa", 0x00427BAA, 0x00427C12,
        "ab799f96661b76eb277c61e39d8e443657951731c97b77106f64680463d67fc3", None,
        (88, "a4b1177cd1d06a54b8446ff3cfc69f95498233f71c5654c904f92847b28cf7e7", "a4b1177cd1d06a54b8446ff3cfc69f95498233f71c5654c904f92847b28cf7e7", "5e8af22d90d882840a5281ed0b730b934e946e500317d63c178762ae0cfc67f4"),
        (84, "6fbafe3174eb270189891b033b9fa2343df0cfe0609ca914dab109ca1814775f", "6fbafe3174eb270189891b033b9fa2343df0cfe0609ca914dab109ca1814775f", "444bc2071d106b94e20f8be997248515ed43297c26c1457235dbd9126b82c5c9"),
    ),
    (
        "open_cfw_bootloader_cmdq_post_loop_block_427c12", 0x00427C12, 0x00427C80,
        "dc82d59544555e204d3bd07610e56276de602047193daf61f5970ff633f3cf6e", None,
        (96, "7dd6f40fb520c8198af130aee58bd2d774c6123c48e049bfdee18b8c680da128", "7dd6f40fb520c8198af130aee58bd2d774c6123c48e049bfdee18b8c680da128", "57f28a96b2f0de46491ac07232d021ae8dd58a94cc9141b04527b67092052b42"),
        (96, "5ad27da11edd5710faad693828dce6f9c16922491e31c061ac346860fbf1bb47", "5ad27da11edd5710faad693828dce6f9c16922491e31c061ac346860fbf1bb47", "57f28a96b2f0de46491ac07232d021ae8dd58a94cc9141b04527b67092052b42"),
    ),
)


def digest(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: Any) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def pins(values: tuple[int, str, str, str]) -> dict[str, Any]:
    size, relocated, unrelocated, _stock = values
    return {
        "size": size,
        "sha256": relocated,
        "unrelocated_sha256": unrelocated,
    }


def stock(values: tuple[int, str, str, str]) -> dict[str, Any]:
    size, _relocated, _unrelocated, stock_sha = values
    return {"size": size, "sha256": stock_sha}


def update_census(boot: bytes) -> None:
    with CENSUS.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = list(reader.fieldnames or ())
        rows = list(reader)
    service_by_start = {item[1]: item for item in SERVICES}
    service_intervals = [(item[1], item[2]) for item in SERVICES]
    output: list[dict[str, str]] = []
    emitted: set[int] = set()
    for row in rows:
        row_start = int(row["start"], 16)
        if any(start < row_start < end for start, end in service_intervals):
            continue
        spec = service_by_start.get(row_start)
        if spec is None:
            output.append(row)
            continue
        name, start, end, _full_sha, _call_offset, apple, _linux = spec
        if start in emitted:
            continue
        emitted.add(start)
        source_end = start + apple[0]
        short_name = name.removeprefix("open_cfw_bootloader_")
        source_body = boot[start - BOOT_BASE:source_end - BOOT_BASE]
        output.append({
            "kind": "source_function",
            "name": short_name,
            "start": f"0x{start:08x}",
            "end": f"0x{source_end:08x}",
            "size": str(len(source_body)),
            "sha256": digest(source_body),
            "disposition": "source_owned_production",
            "provider": f"AmbiqSuite 5.1.0 {short_name}",
            "license_status": "BSD-3-Clause",
            "evidence": "reviewed production C is compiled in place at the authenticated public entry with strict dual-toolchain pins",
        })
        tail = boot[source_end - BOOT_BASE:end - BOOT_BASE]
        output.append({
            "kind": "unreachable_tail",
            "name": f"{short_name}_tail_{source_end:06x}_{end:06x}",
            "start": f"0x{source_end:08x}",
            "end": f"0x{end:08x}",
            "size": str(len(tail)),
            "sha256": digest(tail),
            "disposition": "retained_unreachable_tail",
            "provider": "authenticated stock suffix superseded by the in-place C return paths",
            "license_status": "official binary redistribution unresolved",
            "evidence": "no public or direct interior ingress; retained as authenticated nonexecuted complement after the reviewed source leaf",
        })
    if emitted != set(service_by_start):
        raise SystemExit("command-queue census source intervals were not found")
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t",
                            lineterminator="\n")
    writer.writeheader()
    writer.writerows(output)
    CENSUS.write_text(stream.getvalue(), encoding="utf-8")


def main() -> int:
    source = SOURCE.read_bytes()
    boot = BOOT.read_bytes()
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    names = {item[0] for item in SERVICES}

    entries = []
    for name, start, end, full_sha, call_offset, apple, linux in SERVICES:
        body = boot[start - BOOT_BASE:end - BOOT_BASE]
        if digest(body) != full_sha:
            raise SystemExit(f"{name}: authenticated stock body changed")
        if digest(body[:apple[0]]) != apple[3]:
            raise SystemExit(f"{name}: Apple stock replacement span changed")
        if digest(body[:linux[0]]) != linux[3]:
            raise SystemExit(f"{name}: Linux stock replacement span changed")
        relocations = [] if call_offset is None else [{
            "offset": call_offset,
            "type": "R_ARM_THM_CALL",
            "symbol": UPDATER,
            "symbol_type": "STT_NOTYPE",
            "target_address": UPDATER_ADDRESS,
        }]
        entry: dict[str, Any] = {
            "function": name,
            "runtime_address": start,
            "source": {
                "path": SOURCE.relative_to(ROOT).as_posix(),
                "size": len(source),
                "sha256": digest(source),
                "license": "BSD-3-Clause",
                "origin": "bounded AmbiqSuite 5.1.0 command-queue public-service adaptation",
                "upstream": "AmbiqMicro/ambiqhal_ambiq mcu/apollo510/hal/mcu/am_hal_cmdq.c",
                "upstream_commit": "5efc0228528a8adce5eae0d226fac85d2551eb3b",
                "evidence": "docs/research/g2-bootloader-cmdq-services-427794-427c80-source-closure.md",
            },
            "toolchain": {
                "target": "arm-none-eabi",
                "reviewed_version_prefix": "Apple clang version 21.0.0",
                "flags": FLAGS,
            },
            "strict_relocation_contract": True,
            "expected": pins(apple),
            "stock": stock(apple),
            "relocations": relocations,
            "allow_discarded_alloc_sections": True,
            "toolchain_profiles": {
                "linux-clang": {
                    "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                    "expected": pins(linux),
                    "stock": stock(linux),
                    "relocations": relocations,
                }
            },
        }
        if start & 3:
            entry["allow_halfword_placement"] = True
        entries.append(entry)

    retained = [
        item for item in overlay["in_place_leaves"]
        if item.get("function") not in names
    ]
    overlay["in_place_leaves"] = sorted(
        [*retained, *entries], key=lambda item: int(item["runtime_address"])
    )
    write_json(OVERLAY, overlay)
    update_census(boot)
    print(f"registered {len(entries)} command-queue in-place C leaves")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
