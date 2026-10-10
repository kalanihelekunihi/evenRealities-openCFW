# Ablation and REA feasibility pass

Read the four active workflow specifications completely. This pass concerns P2 analysis support; no C implementation or canonical ledger/gate updates were performed.

## Identified tools and source provenance

* Ablation is https://github.com/Ablation-Tool/ablation, installed at `/Users/kalani/Repos/ablation`, commit `97e051b44d1ac8129b35556fe533e6e8b5338db2`. Read-only `git ls-remote` returned the same upstream HEAD. Its offline launcher is `.local/run-ablation`; local Capstone is 5.0.7.
* REA means Reverse Engineer Anything: https://github.com/morluto/rea. Installed checkout `/Users/kalani/Repos/rea` is `08ec2bf82fa88f5e8caa2b7da9093636731dc55c`, with clean Git status. Upstream HEAD `7aa4d768eb15317a63a476431ed75bafec086033` was inspected and is now pinned at `third-party/tools/rea`. Comparing those commits changes only CHANGELOG and JavaScript mutation-order uncertainty files; no new native firmware capability follows. No installation update is needed for this investigation.

Both tools are now registered as pinned reference submodules at `third-party/tools/ablation` and `third-party/tools/rea`. They are analysis references, not production dependencies.

## New source-backed tool boundaries

1. Ablation's general `ablation/analyzers/binary_context.py::_detect_arch` has no ARC or C-SKY case and defaults to x86_64. Read-only Python execution with synthetic machine labels `ARC_COMPACT2` and `CSKY` returned x86_64 for both. `FuncProfiler.__init__` selects the ARM annotator only for `arm32`; otherwise it selects the generic RegAnnotator. The README ARC table therefore cannot establish general profiler support for EM9305.
2. Its specialized `arc_decoder.py` falls back to a pure-Python 2/4-byte frame walker when Capstone lacks ARC. The installed runtime reported `arc_capstone=False`; `ARCDecoder.has_full_decode` consequently cannot provide full decoder evidence. Fallback source does not implement LIMM extension consumption, labels branch/prologue encodings approximate/tentative, and asks callers to verify them against real binaries. This is unsuitable as an instruction-coverage oracle. `analysis_arc.py` accepts instruction listings and tracks an explicit unknown set; it can assist analysis of an independently verified listing, not fill missing vendor ISA semantics.
3. REA's `src/domain/binaryTarget.ts::elfArchitecture` admits ELF machine IDs 3, 62, 40 and 183 only (x86, x86_64, ARM, ARM64). ARC and C-SKY ELF targets fail admission before Ghidra selection. Relabelling them as ARM would manufacture an invalid analysis context and must not be used. REA's firmware-analysis guide explicitly says arbitrary firmware bytes do not pass native executable admission, its extraction lane is verified on Linux x64, and raw flash load profiles/non-x64 native firmware child coverage remain unverified. Direct Ghidra with pinned processor specifications remains necessary for those components.

Probe command used only imports, architecture dispatch and the width helper in the installed venv; it read no device or target program and made no global cache/configuration writes:

```python
from types import SimpleNamespace as S
import capstone
from ablation.analyzers.binary_context import _detect_arch
import ablation.analyzers.arc_decoder as a
print(capstone.__version__, a._HAS_CAPSTONE_ARC)
print(_detect_arch(S(header=S(machine_type='ARC_COMPACT2'))))
print(_detect_arch(S(header=S(machine_type='CSKY'))))
```

Observed: `5.0.7 False`, `x86_64`, `x86_64`.

## Existing firmware evidence and usable shortcuts

Read existing `g2/analysis/source-discovery-parallel-2026-10-09/ablation-smp-20261010/{REPORT.md,probe.py,REA-FOLLOWUP.md}` and the coverage audit's SMP adapter review. Its authenticated 402-byte Thumb wrapper yielded 161 verified instruction starts and 24 BL sites/targets, matching independent GNU/Capstone evidence. Thumb bits and executable PT_LOAD need explicit adapter handling; invented ELF metadata is not original producer provenance. Repeating that closed bounded probe adds no new knowledge.

Useful next route: export already independently verified ARM function boundaries and explicit Thumb state to analysis-only ELF views, retain original-image byte receipts, then use Ablation for candidate ranking and direct-call triage and REA for evidence-bound Ghidra query orchestration. Include literal pools and external references when reasoning requires them. Review returned control flow and types against original instructions. Semantic ranking or successful decompilation cannot open G2/G3 or prove source/compiler identity.

For EM9305, feed verified ARC listings into specialized analysis only after instruction extension semantics are established using an independent decoder/specification; the installed pure-Python ARC decoder supplies no shortcut to that missing prerequisite. For codec C-SKY/DSP/NPU, neither tool currently removes the architecture-specific recovery requirement. Existing stock parsers and pinned Ghidra processor tooling should stay the primary route.

## Exhaustion and remaining inference

This finite tool-capability question is resolved at inspected pins; latest REA source does not change native support. No newly useful firmware dependency was identified by this tool pass, so no unrelated dependency acquisition is warranted. It is not possible to claim all third-party knowledge exhausted: verified ARM export/ranking at broader boundaries, ARC listing comparisons and source attribution remain actionable P2 work. Those require artifact-specific independently reviewed inputs and should become bounded coordinator contracts. No classifier rejection or model switch occurred.
