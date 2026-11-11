# Parent SpO2 inference C probe

The ignored candidate at `build/goal-r1-spo2-parent-infer-c/candidate.c` implements native `0x968c4`. It is not yet a source-manifest unit or the `r1_goodix_spo2_infer` import provider.

640 stock/C comparisons execute the real model graph, constructors, heap and normalization across all 32 FP settings, four reset bytes, exact/excess history and insufficient history in either channel. Full public RAM, output, state, FPSCR, saved registers, SP and masks are compared. Only the 45 guarded model callback fields are normalized; the source machine maps no stock executable code.

A distinct injected graph boundary suite passes 2,688 comparisons for parent clamp and graph-status handling. It includes NaNs, infinities and subnormals. Ordinary C comparisons initially failed quiet-NaN invalid-status behavior; the candidate now uses a C bit/status helper preserving VCMPE and FZ effects. This boundary suite is not graph algorithm evidence.

36 additional boundary cases cover all 290 native instruction bytes/100 instruction starts. Nine compiled defects are detected, covering dimensions, workspace size, exact history, reset-byte offset, NaN/FZ status, signed clamp and successful cleanup. Insufficient-history/error allocations leak in stock and are deliberately preserved.

Before admission: bind the native caller ABI, integrate the existing calculate consumer, verify the normal build object and update source ownership. The other remaining SpO2 stages are output quality (`0x44a78`), selection (`0x36f88`), confidence (`0x95828`) and output packing (`0x36974`); REA dossiers are saved beside the probe. Physical boot and hardware operation remain unverified.

[Probe evidence](goodix-spo2-parent-infer-c-probe.json).
