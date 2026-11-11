# Native SpO2 output packing in C

`native_spo2_output.c/.h` implements native `0x36974` and resolves the existing calculate import. No assembly or writable global state is added.

The native eight-argument output stage first updates the68-byte channel state snapshot using raw floating payloads, unsigned status bytes, summary fields and optionally confidence fields. Preserve field-store order and reread configuration/confidence references rather than caching across writes. It then emits the64-byte public packet with the native zero/reserved fields and fixed count1.

Packet validity is sign extended from its8-bit input, while the summary flags remain unsigned. Scaling is single-precision multiplication FIRST, then software binary64 promotion/add0.5/truncation through actual C helpers. Factors10000/100000/100 and the unscaled confidence field preserve native rounding order, including biased negative-integer results. Independent Fraction oracles check exact snapshot/packet layout and unchanged FPSCR for finite half-integer exact products.

Public aliases cover snapshots, selected/status scalars, summary/confidence data and configuration. Packet writes can change the second confidence-mode check or subsequent summary/confidence reads; those changes are retained. Nine compiled defects detect wrong offsets, signed validity, confidence gate, factor, half bias, missing zero, flag byte and stale configuration/confidence reads.

Caller tests execute actual C calculate/quartic, heap, model/inference, output quality, selection and output packing together. Earlier processing and confidence remain explicit controlled boundaries. The confidence boundary supplies mapped output data when enabled; this is not confidence-algorithm evidence. Only45 guarded model callback fields are normalized after exact native-address/C-symbol checks. Source maps no stock executable code.

REA authenticates all460 native instruction bytes and24 literal bytes. All460 bytes/134 starts execute. Direct/oracle/caller candidate suites cover all32 FP configurations; aliases cover six. Normal direct/caller samples use six, aliases two, and768 oracle cases cycle all32.

134,344 stock/C comparisons pass, including4,864 independent rational oracle pairs and456 real calculate/model/inference/quality/selection/output caller pairs. Nine compiled defects are detected.

All938 normal units compile without failures or duplicate strong symbols. All926 prior source/object pairs are unchanged; the calculate header edit preserves its entire object. Normal sections and decoded symbols equal the tested candidate after source-file symbol normalization. Application imports fall64 to63; boot imports remain22.

Valid mapped and suitably aligned owners/configuration/state/packet buffers are assumed. Selected public aliases are tested; invalid pointer/count aliases are not given invented recovery. The void C interface does not promise incidental native caller-scratch registers or APSR.

Comparisons check public RAM excluding8192 private stack bytes below incoming SP, full FPSCR, savedR4-R11/S16-S31, SP and interrupt masks. Hardware timing, interrupts/concurrency and physical-device operation remain unverified.

The normal938-unit build is relocatable composition with63 application and22 boot imports, not a complete bootable firmware. Confidence is the remaining open SpO2 parent stage, with feature/statistics/math dependencies still being traced. Other hardware and startup dependencies remain. Source plan and health-cache layout are unchanged.

[Machine-readable evidence](goodix-spo2-output-c-review.json).
