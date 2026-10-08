# Earlier PCM GPU, temperature and sleep recovery

Eight new native bodies now have [readable C](../../components/audio/early_pcm_gpu_offline/gpu.c) and [interfaces](../../components/audio/early_pcm_gpu_offline/gpu.h). Two previously sealed native outer wrappers are reused and integrated. Exact ELF `e25974080eb18ff6974bf10b2fe5976409ed298213cc72654afd87d9ec6cb59b` passes **5,622 comparisons**, including48 on→on→off sequences and32 actual registered TON callback cases. [Exact-build validation](exact-build-validation.json), [build](build_offline.py), [tests/results](results.json), [annotated original instructions](disassembly-evidence.txt), [addresses and body hashes](function-bindings.json).

## New knowledge

PCM0.7 GPU-on0x59FBAC requests TON update for byte state other than2. With buck inactive it saves core-temperature and memory trims, writes core-temperature2, and raises memory trim by5 capped63. With buck active and cached-original-trims flag0x20074F63 set, it disables the buck, installs cached VDDC+9/VDDF+15 capped127, sets boost/clock controls and re-enables the buck. Its switch helper0x59FB70 orders the enable register,5-unit shared delay and actual buck-control helper differently for enable/disable. GPU-off0x59FCA2 restores cached fields in the corresponding branch and always requests TON-off. Original registered TON0x59FE5A executes in32 fixtures; other fixtures deliberately leave that slot NULL.

PCM1.x/2.0-family GPU-on0x5A0328 instead temporarily raises core by12 capped1023, sets memory trim5, delays5, optionally boosts VDDF+15 according to flag0x20074F6F, sets four rail-short controls and delays10. The same flag selects VDDC+9 and one of two fixed TON families; byte state1 selects LP values and other states select the other values. It clears short controls, subtracts its actual core increment and installs memory trim0 or1 according to0x20074F6E. GPU-off0x5A05E0 follows another ordered sequence, subtracting optional VDDF/VDDC boosts with floor0 and restoring saved core-temperature trim. Inactive-buck paths restore saved LDO fields. These are internal variant-dependent power settings, not app-level packet fields.

Repeated GPU-on is not assumed idempotent. In an explicit synthetic flag-enabled fixture with initial VDDC/VDDF trims0, two later-family on calls then one off leave VDDC9 and VDDF15. That is instruction-backed sequence behavior under the fixture, not a proven naturally reachable device defect. CFW retry/mode-change logic needs actual caller/variant/state analysis rather than assuming one off reverses arbitrary repeated on calls.

Temperature0x5A00FC classifies[-273,35),[35,50),[50,1000). It returns0 and lower/upper bounds[-273,35],[33,50],[48,1000], respectively; invalid/NaN/infinite values return1 with zero bounds. Depending on0x20074F67 it updates forced-buck-active0x20074F7B. Publication0x5A00C8 preserves PRIMASK, caches range0x20074F74 and either sets pending0x20074F72 when postpone0x20074F71 is set or executes actual hardware-temperature apply0x5A001C. This request/deferral contract is now native; the apply body remains an original-code dependency.

Sleep preparation0x5A0204 is gated by0x20074F67. Range2 forces buck active; otherwise active STIMER clocks1/2 or enabled timer clocks0..5,19..24,256..479 do so. Other fixtures clear the flag. Boundary tests cover timer indices0/15, running/disabled clocks and STIMER halt/freeze bits. This resembles later-family clock scanning, but has a separate stock address, cached range and variant gate.

## Source comparison and practical use

Pinned SDK5.1.0 supplies direct GPU/tempco/sleep function leads. Newly interpreted `am_hal_pwrctrl.h` defines BOOST_VDDF_FOR_SDIO=false and thresholds35/50, consistent with the selected stock paths. This does not infer historical compile flags or whole-module equivalence. Stock outer wrappers accept fewer stimuli than SDK and do not implement its INIT_STATE/SDIO handling or saved-float temperature paths. The earlier-family35 threshold must not be substituted for the later PCM2.1/2.2 classifier's different ranges.

This yields reusable offline power-state interfaces and explains why firmware variants can change GPU/display-related trim sequencing and why a temperature report may only mark work pending. It does not justify a firmware patch without identifying the actual silicon/calibration selection and scheduler behavior.

[Source pin, file hashes, search outcome and remaining leads](source-reference.json). A bounded public-source search returned no additional version; no new download or submodule change was needed. Concrete remaining bodies are temperature hardware application0x5A001C, postpone/pending0x5A07E6/0x5A07F0, earlier TON configuration0x59FDC2/0x59FE5A and initialization/reset/suspend callbacks. Source-search exhaustion has not been reached.

## Limits and preservation

All common delay, buck-register, TON-dispatch, STIMER and temperature-apply providers execute original instructions without success-return stubs. Native wrappers use the eight reconstructed bodies. Tests compare meaningful SRAM/metadata, ordered MMIO writes and common-provider calls; scratch registers and every stack byte are outside scope. Original startup/ITCM bytes are authenticated, but trims/caches/MMIO are synthetic. No physical settling, full M55, real exception delivery or live RTOS/quiescence proof is claimed.

All1,298 prior sealed entries,110 audit inputs,four checkpoints and root index were checked before sealing. No commits, staging, production changes or device writes.
