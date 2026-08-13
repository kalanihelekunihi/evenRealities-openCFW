# GoMore IIR coefficient-designer provider boundary

## Disposition

The former largest unclassified function at `0x000717AC` / 602 executable bytes is now routed to
the existing `gomore_health_algorithm_candidate` gate with disposition
`vendor_source_required_not_redistributable`. It is a private trigonometric IIR coefficient
designer used only by GoMore's already gated sleep-filter initializer.

This is an ownership boundary, not permission to reconstruct the formula. No exact public GoMore
SDK version, private symbol, or redistribution license has been authenticated. A matching licensed
GoMore provider is required before this algorithm can be enabled.

## Callgraph proof

The complete body `0x000717AC..<0x00071A06` is 602 bytes and has exactly one direct caller:

```text
GoMore sleep algorithm initializer 0x00071D62
  callsite 0x00071D76
    -> private coefficient designer 0x000717AC
```

Caller `0x00071D62` was already independently SHA-pinned by the sleep-algorithm audit and already
routed to GoMore. The designer has no outside caller. Its only callees are separately source-routed
Arm toolchain `cosf` (`0x00038A5C`), `sinf` (`0x0003AE04`), and `powf` (`0x0003A620`). Those math
bodies are not included in the 602-byte GoMore census and must come from the selected toolchain.

The function creates coefficient/state values from a normalized cutoff, mode, and order. Those
semantics and the exclusive provider callgraph identify its role, but they do not make the private
implementation, coefficient-generation structure, or GoMore integration locally reproducible.

## Exact evidence and exclusions

`summarize_r1_gomore_iir_designer.py` freezes the complete function SHA-256, sole caller set, and
the provider/toolchain split. With the later authorization-parser and sleep-stage-statistics closures, the resulting GoMore boundary contains 248 exact functions after
this supplemental closure.

Local code must not emit:

- a reconstruction of this coefficient designer or its private algorithm structure;
- copied or derived GoMore coefficient tables;
- a substitute presented as the authenticated GoMore provider; or
- local replacements for the Arm math runtime.

Portable openR1 code may retain only an abstract filter-provider interface and validate outputs
from a lawfully supplied provider. The summarizer is static, reads no sensor data, and emits no algorithm or generated coefficients.

## Reproduce

```sh
python3 tools/summarize_r1_gomore_iir_designer.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
