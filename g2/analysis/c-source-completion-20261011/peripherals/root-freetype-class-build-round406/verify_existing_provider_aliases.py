#!/usr/bin/env python3
"""Audit an analysis-only symbol join to already qualified Main C bodies."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
MAIN = ROOT / "g2/build/c-firmware/20261013/peripherals-root-freetype-qalloc-round410/apollo_main/candidate.o"
SIDE = HERE / "main-plus-upstream-classes.o"
OUT = HERE / "main-plus-upstream-classes-qualified-aliases.o"
ALIASES = {
    "FT_Get_Module": "audio_uart_ft_get_module_5273b8",
    "FT_GlyphLoader_CreateExtra": "audio_uart_ft_glyph_loader_create_extra_524c88",
    "FT_GlyphLoader_Rewind": "audio_uart_ft_glyph_loader_rewind_524ba8",
    "FT_List_Add": "audio_uart_ft_list_add_529304",
    "FT_List_Finalize": "audio_uart_ft_list_finalize_529378",
    "FT_List_Find": "audio_uart_ft_list_find_5292e6",
    "FT_Stream_Close": "audio_uart_ft_stream_close_5288ce",
    "FT_Stream_Free": "audio_uart_ft_stream_free_52502a",
    "FT_Stream_OpenMemory": "audio_uart_ft_stream_open_memory_5288b8",
    "FT_Stream_Read": "audio_uart_ft_stream_read_528928",
    "FT_Stream_ReadAt": "audio_uart_ft_stream_read_at_528936",
    "FT_Stream_ReadULong": "audio_uart_ft_stream_read_ulong_528ba8",
    "FT_Stream_ReadUShort": "audio_uart_ft_stream_read_ushort_528b4a",
    "FT_Stream_Seek": "audio_uart_ft_stream_seek_5288e0",
    "FT_Stream_Skip": "audio_uart_ft_stream_skip_528914",
    "ft_mem_alloc": "audio_uart_font_mem_alloc",
    "ft_mem_free": "audio_uart_font_mem_free",
    "ft_mem_qalloc": "audio_uart_ft_mem_qalloc_529176",
    "ft_mem_realloc": "audio_uart_font_mem_realloc_items",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path):
    lines = subprocess.check_output(["arm-none-eabi-nm", "-g", str(path)], text=True)
    defined, imported = {}, set()
    for line in lines.splitlines():
        cells = line.split()
        if len(cells) >= 2 and cells[-2] == "U":
            imported.add(cells[-1])
        elif len(cells) >= 3 and cells[-2] in "TDRBSCWVA":
            defined[cells[-1]] = int(cells[0], 16)
    return defined, imported - set(defined)


def main():
    before_defs, before_imports = symbols(SIDE)
    main_defs, _ = symbols(MAIN)
    assert set(ALIASES) <= before_imports
    assert set(ALIASES.values()) <= set(main_defs) <= set(before_defs)
    cmd = ["arm-none-eabi-ld", "-r"]
    cmd += [item for name, target in sorted(ALIASES.items())
            for item in ("--defsym", f"{name}={target}")]
    cmd += [str(SIDE), "-o", str(OUT)]
    subprocess.run(cmd, check=True, cwd=ROOT)
    after_defs, after_imports = symbols(OUT)
    assert len(after_imports) == len(before_imports) - len(ALIASES)
    assert before_imports - after_imports == set(ALIASES)
    assert all(after_defs[name] == after_defs[target] for name, target in ALIASES.items())
    receipt = {
        "status": "PASS_ANALYSIS_ONLY_QUALIFIED_SYMBOL_JOIN",
        "main_candidate_sha256": digest(MAIN),
        "class_side_link_sha256": digest(SIDE),
        "alias_side_link_sha256": digest(OUT),
        "qualified_symbol_joins": ALIASES,
        "unresolved_imports_before": len(before_imports),
        "unresolved_imports_after": len(after_imports),
        "limits": ["Linker aliases are analysis-only; not admitted to selected Main build",
                   "These provider C bodies passed earlier native qualification; this check proves symbol/address joins, not connected callback runtime",
                   "Remaining imports and setjmp/longjmp ABI require qualification"],
    }
    (HERE / "existing-provider-alias-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "joined": len(ALIASES),
                      "remaining_imports": len(after_imports)}))


if __name__ == "__main__":
    main()
