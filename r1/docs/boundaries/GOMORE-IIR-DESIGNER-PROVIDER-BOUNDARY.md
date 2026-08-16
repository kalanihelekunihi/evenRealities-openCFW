# GoMore IIR coefficient-designer provider boundary

## Disposition

The function at `0x000717AC` / 602 executable bytes is now source-admitted as
`gomore_primitives_iir_low_high_coefficients` with disposition
`clean_room_reimplementation_owner_authorized`. It is a private trigonometric low/high-pass IIR
coefficient designer used only by the recovered sleep-filter initializer.

No exact public GoMore SDK version, private symbol, or redistribution license has been
authenticated. Under the owner-authorized clean-room reduction, the body is independently
reconstructed from the pinned Ghidra/Thumb evidence. It includes no vendor source, firmware bytes,
absolute pointers, or coefficient table.

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

The typed implementation owns a 48-byte coefficient record, validates modes zero/one and orders
one through four, and leaves `cosf`, `sinf`, and `powf` as explicit toolchain dependencies. It
preserves the stock pole construction, polynomial expansion, low/high gain selection, and
alternating high-pass numerator signs.

## Exact evidence and exclusions

`summarize_r1_gomore_iir_designer.py` freezes the complete function SHA-256, sole caller set, and
the provider/toolchain split. `emulate_r1_iir_low_high.py` directly executes five production-Thumb
fixtures covering both modes and orders one through four, and pins every written and preserved
Float32 word.

The static summarizer emits no algorithm or generated coefficients. The compiled reconstruction:

- generates coefficients from caller inputs rather than retaining copied or derived tables;
- is labeled as a clean-room reconstruction, not an authenticated GoMore provider; and
- does not replace the Arm math runtime.

Host tests pin the stock order-two low-pass result and an order-four high-pass result. The host
libm path is allowed at most three ULPs from exact production words; the production emulator keeps
the exact bit-level oracle. The summarizer is static and reads no sensor data.

## Reproduce

```sh
python3 tools/evidence/summarize_r1_gomore_iir_designer.py
PYTHONPATH=/tmp/openr1-unicorn python3 tools/evidence/emulate_r1_iir_low_high.py \
  research/decompilation/rebuild/rebuilt-application.bin
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
