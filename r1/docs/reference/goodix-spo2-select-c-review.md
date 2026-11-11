# Native SpO2 selection in C

`native_spo2_select.c/.h` implements native `0x36f88` and resolves the existing calculate import. It adds no assembly or writable global state.

The native five-argument selector uses software double promote/add-half/truncate on the newest window sample. Auxiliary state+24 is converted with native signed RTZ/FPSCR semantics; state+64 is multiplied by single-precision10000 before software rounding. Even parity enables signed-remainder6 adjustments to the cached byte, clamped to65..100. Both native VCVT sites use the proven pure C bit/status helper; no undefined C float-to-integer casts are introduced.

Modes0/1/2/12/21 retain their native transitions and policy-bit hysteresis. Unknown modes preserve selected/status values. Warm-up and fallback counters compare against the full unsigned iteration argument. Status5 refreshes the cached byte through UNSIGNED RTZ conversion before the late mode0 fallback; the fallback does not refresh the cache again. Output/status aliases retain live access order and cached versus reread fields.

Independent finite-integer oracles check transitions, hysteresis/parity, cache ordering and unsigned thresholds. Cartesian state/policy/iteration/flag tests separate dimensions that were correlated in an earlier fixture. An explicit UINT32_MAX iteration case detects the signed-comparison defect. Other direct tests include NaNs, infinities, subnormals and all32 FP configurations. Selected mapped output/status aliases cover state/configuration/auxiliary/parity fields.

Caller tests execute actual C calculate/quartic, heap, inference parent, model graph, output quality and selection. Earlier processing and the unfinished confidence/output stages are explicit boundaries. Source maps no stock executable code. Only45 guarded typed model callback fields are normalized after exact native-address/C-symbol checks.

734 native instruction bytes/276 starts execute within the744-byte body. The remaining10 bytes at37236/37238/3723a/37240/3726e are unreachable final-clamp blocks: signed remainder4 is in[-3,3], so adding97 is in[94,100]. C retains the clamp. REA authenticates the complete744-byte span and12 literal bytes (binary64 half and binary32 ten thousand).

369,694 stock/C comparisons pass, including4,864 independent integer oracle pairs and456 real calculate/model/inference/quality/selection caller pairs. Ten compiled defects are detected, covering conversions, parity scaling/remainder/adjustment, flag source, warm-up equality, signed iteration, cache refresh, fallback offset and unknown modes.

All937 normal units compile without failures or duplicate strong symbols. All925 prior source/object pairs are unchanged; the calculate header edit preserves its entire object. Normal sections and decoded symbols equal the tested candidate after source-file symbol normalization. Application imports fall65 to64; boot imports remain22.

Valid mapped owner/window descriptors and nonempty history are assumed. The tested public aliases do not establish recovery for invalid owner-pointer/count aliases. No new fallback is invented for invalid inputs. The stock incidental R0/R1 argument restoration is outside the void C consumer contract.

Comparisons check public RAM excluding8192 private stack bytes below incoming SP, full FPSCR, savedR4-R11/S16-S31, SP and interrupt masks. Caller scratch/APSR, hardware timing, interrupts and concurrency remain unverified. Candidate broad/edge/oracle/caller suites use32 FP settings; aliases use six. Normal broad/edge/caller samples use six, aliases two, and768 oracle cases cycle all32.

The normal937-unit build remains relocatable composition with64 application and22 boot imports, not a complete bootable firmware. Confidence and output packing remain open source-tree stages, alongside other hardware/startup dependencies. The output-packing candidate is an ignored probe outside this acceptance. Source plan and health-cache layout are unchanged.

[Machine-readable evidence](goodix-spo2-select-c-review.json).
