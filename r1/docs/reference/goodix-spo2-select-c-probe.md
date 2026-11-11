# SpO2 selection C probe

The ignored candidate at `build/goal-r1-spo2-select-c/candidate.c` implements native `0x36f88`; it is not yet a source-manifest unit or normal import provider.

303,776 stock/C comparisons pass:204,800 direct,61,440 live-alias,32,768 independent state/policy/iteration/flag Cartesian cases,4,096 finite-integer oracle cases,384 calculate-caller cases and288 extra coverage pairs. Candidate direct/edge/oracle/caller suites cover all32 FP configurations; aliases cover six. Ten compiled defects are detected. An explicit unsigned-iteration case was added after correlated test dimensions failed to detect that defect.

The routine uses actual C software float/double promotion/add/truncation plus the proven C RTZ/FPSCR helper for both native VCVT instructions. Preserve signed/unsigned conversion, scaled parity, byte-clamped cache adjustments, mode0/1/2/12/21 transitions, unknown modes, unsigned warm-up counters, cache-before-fallback ordering and output/status aliases. No assembly or writable globals are added.

Real caller tests execute calculate, quartic, heap, inference/model graph, output quality and selection together. Earlier processing and confidence/output remain explicit controlled boundaries. Full public RAM and saved ABI/FPSCR match; only45 guarded model callback fields are normalized. Source maps no stock executable code.

734 native instruction bytes/276 starts execute. The other10 bytes at0x37236/37238/3723a/37240/3726e are unreachable final-clamp blocks: signed remainder4 lies in[-3,3], so adding97 lies in[94,100]. The C clamp is retained. REA authenticates all744 instruction-span bytes and12 literal bytes (binary64 half and binary32 ten thousand).

Before admission: add the shared header/source unit, connect the native calculate import, verify normal objects and update ownership. Valid mapped descriptors and nonempty history are assumed; invalid pointer/count aliases, physical hardware, timing and concurrency remain unverified.

[Probe evidence](goodix-spo2-select-c-probe.json).
