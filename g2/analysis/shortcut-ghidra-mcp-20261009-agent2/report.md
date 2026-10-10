# Ghidra MCP shortcut evaluation, 2026-10-09

## Findings with operational evidence

The bridge works, but the current live instance is unrelated to the authenticated
G2 campaign. `list_instances` reported bridge v7.0.0 at localhost port 8089,
project `SyntheticSmoke`, PID 58627. `list_open_programs` returned zero programs;
`list_project_files(folder="/")` returned only `/synthetic.elf`. No firmware
program was opened, mutated, or decompiled through that instance during this pass.
The local bridge checkout is `/Users/kalani/Repos/ghidra-mcp`, commit
`9cc29c0f1efb6c63a7d6898c9a23aff39397f992`, upstream bethington/ghidra-mcp.
The local launcher sets script permission to zero. Its secret values are excluded
from this report. Ghidra is installed at
`/opt/homebrew/Cellar/ghidra/12.1.4/libexec`; JDK21 is available through Homebrew.

The installed C-SKY processor has a confirmed incorrect `movih` P-code lift.
The private four-byte synthetic probe `23 ea a0 a0` decoded as
`movih r3,0xa0a0`, then produced:

```
(unique, 0x11e00, 2) INT_LEFT (const, 0xa0a0, 2), (const, 0x10, 4)
(register, 0xc, 4) INT_ZEXT (unique, 0x11e00, 2)
```

The shift result is two bytes wide, so shifting left 16 discards every bit;
zero-extension subsequently yields zero. The intended high-immediate result is
`0xa0a00000`, also independently asserted by the existing instruction regression
`g2/tools/ghidra_scripts/CheckCskyMovih.java` for codec address `0x1000588c`.
This pass establishes that the currently installed processor remains affected,
although the repository already knew about the regression test. `probe.log`
preserves the actual successful Ghidra execution. This is a processor semantics
failure, regardless of bridge, decompiler naming, or completeness scores.

Both installed and submodule `32b_data.sinc` have SHA-256
`3dde82aa3bc3bfbb70dc8950705cd0c2a59173e924ee6f92f9005ed880d5210b`.
The installed compiled `csky_v2.sla` hash is
`ffd3dee2b2bdfe3586c1f7362a7cca079ba2fc2a6ab28b5cc5107bfd68187755`.
The CSKY submodule is clean at
`0daaa056e8c570ba514fc0d0226384ecf9f9df05`.

## Shortcut value and limits

The bridge can reduce interaction overhead for callers, callees, references,
prototypes, and data-flow investigation; its source advertises P-code graph
propagation, P-code emulation, documentation transfer, and headless support.
Those capabilities are candidates, not operational proof for this firmware.
Most byte, xref, function, and decompilation access overlaps the existing Java
export pipeline. Its extra value is rapid bounded interrogation and reversible
private-project hypothesis testing. A bridge completeness score cannot satisfy
the workflow's independently reviewed byte denominator or semantic gate.

P-code emulation and graph propagation inherit the installed processor semantics.
The confirmed `movih` error would contaminate constants, pointer references,
control flow, decompilation, and emulation. They cannot act as an independent
oracle for the affected instructions. GNU C-SKY objdump and vendor ISA material
remain independent evidence. Ghidra CSKY compiler specification currently lists
only r0 as the result register, and models lr as unaffected; multiword returns
and calling effects need validation against the actual ABI before trust.

The current campaign still has concrete mapping/behavior work beyond tool setup.
`attempts/P2-csky-reset-pseudocode-109/002/mapping-audit.json` reports
`correction_needed_coordinate_domains_underspecified`. Attempt 109/001 is partial:
startup callees at runtime `0x10000acc` and conditional `0x10023500`, and BKPT
exception/continuation semantics remain unresolved. A generic import base must
not erase the distinction between header-inclusive child offsets, stripped
payload offsets, runtime addresses, and conditional stage mappings.

## Exact next admissible integrations

1. Create a private CSKY processor copy and move zero-extension before the shift
   (`zext(imm16:2) << 16`); compile its SLEIGH and rerun this synthetic probe and
   the existing authenticated `CheckCskyMovih` test. Preserve hashes and raw
   P-code. Do not silently replace the globally installed processor or rewrite
   previous raw evidence. Independently review the correction and other changed
   instruction semantics.
2. Use one private project per nested image/address space, with reviewed loader
   mappings and input hashes from the active campaign. Connect a dedicated bridge
   instance; keep the current SyntheticSmoke instance intact. Bind project path,
   language/cspec/SLA hashes, binary hashes, options, and tool version in receipts.
3. Start with read-only bridge queries on complete bounded startup bodies at
   `0x10000acc` and `0x10023500`, after reconciling the mapping audit. Export raw
   decompilation, complete body ranges, instructions, callers/callees, references,
   and graph diagnostics. Compare instruction by instruction to independent
   C-SKY objdump and the NationalChip CK804 startup source.
4. Test calling-convention and type hypotheses only in private projects. Save
   baseline and changed exports separately. Track changed constants, edges,
   undefined intrinsics, and register effects. Promote only reviewed evidence
   through the coordinator; never treat cosmetic improvement as new coverage.
5. Enable arbitrary script execution only if a concrete script needs it on a
   dedicated private instance. Existing Java headless exporters already provide
   an operational route without changing the current bridge configuration.

## Scope and reproducibility

Read the full current README, PROCEDURE, CONTRACTS, and REPOSITORY instructions.
No firmware source, global inventory, gates, submodule, or existing analysis
project was changed. The only Ghidra execution used a synthetic four-byte input
and the private `PrivateCskyProbe` project within this report directory.
First attempt without JAVA_HOME exited 1; the JDK21 run exited 0.

Reproduce in a fresh private project directory (the script preserves its output;
an existing project/import name can conflict on repeat):

```
JAVA_HOME=/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home python3 g2/analysis/shortcut-ghidra-mcp-20261009-agent2/probe.py
```

No newly required third-party repository was found beyond the downloaded bridge
and existing processor source. The coordinator can pin the bridge's existing
checkout as a submodule if repository ownership permits. The useful new knowledge
is live operational state and proof that the installed CSKY lift is still wrong;
the bridge itself has not yet recovered new firmware semantics in this pass.

## Follow-up: private correction verified

The coordinator authorized the bounded correction. Applied
`csky-movih-width.patch` only in a private copied processor, then compiled
SLEIGH successfully. The corrected expression moves zero-extension before
the shift. The actual new P-code now has a four-byte temporary:

```
(unique, 0x11e00, 4) INT_ZEXT (const, 0xa0a0, 2)
(register, 0xc, 4) INT_LEFT (unique, 0x11e00, 4), (const, 0x10, 4)
PROBE_RESULT=a0a00000 EXPECTED=a0a00000
```

The probe explicitly evaluates COPY/ZEXT/LEFT operations with their declared
output widths and compares against an independent 32-bit arithmetic result,
`0xa0a0 * 65536 = 0xa0a00000`. The Java check fails on a mismatch.
`validate_fix.py` recompiles the private SLEIGH, reruns the private stored
synthetic program without analysis, records argv/logs/hashes, and rechecks
that installed and submodule source hashes equal their original values.
`fixed-receipt.json` and `fixed-evaluated-probe.log` retain the proof.

A partially symlinked installation was insufficient: Ghidra resolved shared
framework jars back to the global installation and still used the original
processor. A complete 767 MB private installation copy resolved this. It and
the private project databases are ignored in Git; the patch and replay scripts
remain versionable. No global extension or existing campaign project changed.

The exact existing `CheckCskyMovih.java` firmware test was not run: its fixed
address `0x1000588c` is not directly established by the currently inspected
conditional canonical mappings. Authentic canonical images contain the same
four bytes at several offsets (for example BINH-A SRAM child offset `0x2a4c`,
conditionally runtime `0x10025e4c`). Reusing the old fixed address without its
mapping receipt would create misleading firmware proof. The new test verifies
the same instruction and expected value synthetically; it does not establish
image mapping, full firmware semantics, or completeness. Those remain a separate
bounded campaign integration step.
