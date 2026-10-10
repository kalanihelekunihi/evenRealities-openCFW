# G2 tool-derived shortcut frontier — 2026-10-10

Three Daybreak Blue Low agents investigated Ghidra-MCP, Ablation, and REA in separate lanes against authenticated G2 analysis views. Each lane retained its exact inputs, tool identity, method, outputs, and limitations. No canonical coverage ledger, gate receipt, installed processor, shared Ghidra project, firmware source, or submodule pin changed. The campaign remains `P2_EXECUTING`.

## Concrete leverage for later C reconstruction

| Tool | Validated use | Boundary |
| --- | --- | --- |
| Ghidra-MCP | High P-code on a reviewed 402-byte Thumb body recovered 31 blocks, 355 operations, and all 24 independently counted direct calls. It exposes call-site argument storage and a candidate `r1` record layout with reads at offsets 0, 2, 3, and 8. | The imported ELF's stored function body is degenerate (size 1). Ordinary CFG, call graph, xrefs, and documentation score are misleading; P-code ABI facts are review candidates, not source signatures. |
| Ablation | With authenticated bytes, reviewed starts and Thumb state, its direct-call inventory covered every GNU-decoded body call in the retained Apollo-main function spans at most 4,096 bytes. The audit covered 8,853 ranges in total. | It missed 1,198 calls in 23 larger spans. Whole-image graph included 4,661 decoded gap calls assigned to preceding functions and nine further false candidates. It omits indirect calls and its graph loses call sites. |
| REA | A whole authenticated Apollo mapping overcame the narrow ELF's empty-callee result. It exposed 7,341 procedures, 17,010 strings, named-function pseudocode, five resolved callees and nine incoming xrefs for `0x0054116e`, plus reusable snapshot replay. | Default decompiler types can be wrong (including a concrete `undefined8` return conflict); indirect calls still lack targets. Snapshot replay is repeatability, not independent semantic proof. |

Detailed evidence and reproduction are in `../ghidra-mcp-depth-20261010-daybreak/`, `../ablation-whole-main-frontier-20261010-daybreak-low/`, and `../rea-wide-mapping-exhaustion-20261010-daybreak-low/`.

## Combined workflow rule

For a named P2 function, start with authenticated bytes, load address, reviewed ISA state, and independently bounded code/data extent. Ablation can enumerate direct immediate calls inside a reviewed Thumb span no larger than 4 KiB; retain the call sites and cross-check a native decoder. Use REA's whole-image ephemeral mapping or a reviewed private Ghidra-MCP project to inspect callers, strings, high P-code, and candidate C interfaces. Check every proposed field, argument, branch, and target against original instructions, relocation/data records, controlled execution, or an independently authenticated source comparator. Keep indirect targets unresolved until their tables or runtime dispatch are independently established.

The current tool-specific frontier is exhausted for these views. Repeating unbounded tool queries will not fix Ghidra's bad stored extent, Ablation's hard scan cap or gap ownership, or decompiler type and indirect-target uncertainty. Further useful work needs a selected P2 review body, corrected wider mapping or types, a new authenticated producer input, or original-byte semantic validation. Tool outputs alone do not establish whole-firmware pseudocode completeness, a C-compilable payload, or byte-identical output; G2–G6 remain closed.
