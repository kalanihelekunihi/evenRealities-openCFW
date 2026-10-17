#!/usr/bin/env python3
"""Pin Conversate's exact audio-manager call targets to existing C bodies."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261016"
HERE = BASE / "main-conversate-audio-manager-aliases"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    prior = BASE / "main-conversate-start-request-5b1f2e/candidate.o"
    candidate = HERE / "candidate.o"
    removed = {"audio_conversate_page_show_54f380",
               "audio_conversate_page_hide_54f50e"}
    before, after = imports(prior), imports(candidate)
    if len(before) != 122 or len(after) != 120 or before-after != removed or after-before:
        raise RuntimeError("Conversate audio manager aliases changed import frontier")
    linker = ROOT / "g2/analysis/c-source-completion-20261011/apollo/main_conversate_audio_manager_aliases_20261016.ld"
    with candidate.open("rb") as stream:
        elf = ELFFile(stream)
        symbols = {item.name: item["st_value"] for item in
                   elf.get_section_by_name(".symtab").iter_symbols()}
        for alias, target in (("audio_conversate_page_show_54f380",
                               "audio_even_ai_app_acquire_54f380"),
                              ("audio_conversate_page_hide_54f50e",
                               "audio_terminal_reset_mode_notice_54f50e")):
            if alias not in symbols or target not in symbols or symbols[alias] != symbols[target]:
                raise RuntimeError(f"Audio-manager alias differs: {alias}")
        for name, address, size in (
                (".g2_conversate_reply_list_200d6b84", 0x200d6b84, 0xaac),
                (".g2_conversate_prep_note_ram_200d7630", 0x200d7630, 0xb4b1),
                (".g2_conversate_ui_settings_extension_20071369", 0x20071369, 0x94),
                (".g2_ram_200746dc", 0x200746dc, 4)):
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_type"] != "SHT_NOBITS" or
                    section["sh_addr"] != address or section["sh_size"] != size):
                raise RuntimeError(f"Fixed RAM changed: {name}")
    sources = []
    for label in ("main-even-ai-app-acquire", "main-even-ai-app-release"):
        path = BASE / label / "receipt.json"
        record = json.loads(path.read_text())
        if record["source_complete"] or record["status"] not in (
                "PASS_EXPERIMENTAL_MAIN_EVEN_AI_APP_ACQUIRE_C",
                "PASS_EXPERIMENTAL_MAIN_EVEN_AI_APP_RELEASE_C"):
            raise RuntimeError(f"Provider receipt changed: {label}")
        sources.append(ref(path))
    record = {
        "status": "PASS_BOUNDED_MAIN_CONVERSATE_AUDIO_MANAGER_ALIASES_INTEGRATION",
        "prior_candidate": ref(prior), "candidate_object": ref(candidate),
        "linker_script": ref(linker), "provider_receipts": sources,
        "native_targets": {"audio_conversate_page_show_54f380": "0x54f380",
                           "audio_conversate_page_hide_54f50e": "0x54f50e"},
        "unresolved_before": 122, "unresolved_after": 120,
        "removed_imports": sorted(removed), "new_imports": [],
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Underlying audio-manager bodies retain their bounded evidence limits; wider Main behavior remains.",
    }
    output = HERE / "receipt.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(output))


if __name__ == "__main__":
    main()
