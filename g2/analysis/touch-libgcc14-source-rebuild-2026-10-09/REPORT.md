# Exact-release division source-provider rebuild

Unmodified GCC source at the official Arm14.2 release revision
`a05ea1e5ee0867191bb432a84c055be99dbdbc16` regenerates both real providers:
`L_udivsi3` emits276bytes; `L_dvmd_tls` emits4bytes. Their raw text matches
the independently reviewed authenticated archive members, including relocation
fields. Linking at stock-proven addresses reproduces all280stock bytes.
This is a focused source rebuild, not an executable-blob substitution.

The authoritative t-arm/t-elf rules select lib1funcs.S and these member names;
source selectors and compiler Cortex-M0+/Thumb macros choose the real bodies.
No source was modified and no opcode array/stub was introduced. The source
non-size Thumb branch is selected without defining __OPTIMIZE_SIZE__; no
optimization sweep or fabricated generated build header was used. Actual
preprocessing dependencies and their hashes show the consumed source includes.

`rebuild.py` saves preprocessing and dependency receipts; `results.json` pins
compiler/linker/source/license/object/ELF hashes and actual argv. Exact-revision
COPYING3 and Runtime Library Exception3.1 are retained by source discovery and
hashed here. No blanket licensing conclusion is inferred from these notices.

The98original-instruction cases in the preceding division packet already
validate the identical code and zero-hook semantics; they were not rerun.
The focused rebuild does not prove vendor full configure commands, debug/object
byte identity, a unique producing tree/compiler or whole-firmware completeness.
No54entrycensus increment or campaign admission follows. Independent source
rebuild review is pending; binary-provider review previously passed.

Proposed comparison reference (not installed as a submodule):
`third-party/reference/gcc-arm14-runtime`, upstream
`https://gcc.gnu.org/git/gcc.git`, exact revision above. Existing selected-source
acquisition remains immutable; no .gitmodules, index or production edits.
