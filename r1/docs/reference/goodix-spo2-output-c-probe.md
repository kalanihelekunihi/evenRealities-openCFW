# SpO2 output-packing C probe

The ignored candidate at `build/goal-r1-spo2-output-c/candidate.c` implements native `0x36974`; it is not yet a source unit or normal import provider.

104,832 stock/C comparisons pass:32,768 direct,67,584 ordered-alias,4,096 independent rational-oracle and384 calculate-caller pairs. Nine compiled defects are detected, including signed validity, confidence gating, selected scaling, half bias, zero fields and stale configuration/confidence reads. All460 instruction bytes/134 starts execute. REA authenticates the complete body and24 literal bytes.

State snapshots preserve raw floating payloads and unsigned status bytes. Packet validity is sign extended. Scaling uses hardware single-precision multiplication FIRST, followed by native software double promotion/add-half/truncation. The first and second confidence-mode checks and data reads remain live across earlier state/packet writes. Independent Fraction oracles cover negative half-bias behavior and exact layout/FPSCR; NaNs, infinities and subnormals are covered by the direct suites.

Caller tests run actual C calculate, quartic, heap, model/inference, output quality, selection and output packing together. Earlier processing and confidence remain explicit test boundaries. Confidence-output data is supplied in the controlled boundary when configuration enables it. The source maps no stock executable code; only45 guarded model callback fields are normalized.

Before admission: add the shared native source/header, connect the existing calculate import, verify normal objects and update ownership. Valid mapped backing spans are assumed. Physical hardware, timing and concurrency remain unverified.

[Probe evidence](goodix-spo2-output-c-probe.json).
