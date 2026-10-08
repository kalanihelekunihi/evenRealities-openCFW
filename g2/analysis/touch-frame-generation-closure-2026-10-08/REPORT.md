# Per-sensor active/low-power frame generation

Independent source in `../../components/touch/frame_generation_offline/` reconstructs mask helper `0x5188`, divider adjustment `0x5528`, CDAC configuration `0x51bc` and sensor-frame generation `0x5548`. Original addresses, bytes and pinned comparator hashes are in provenance. This closes the selected per-sensor software family; `GenerateAllSensorConfig` at `0x56a4` remains open.

## Layout and behavior

Active frames have six scan words plus a hardware-IIR coefficient word at +24. Low-power frames prepend five processing words, then the six scan words. The prefix packs baseline/IIR coefficients, negative-baseline reset, noise/negative-noise thresholds, finger threshold, debounce and signal type. These are register fields, not electrical or time units.

Type 0 selects active slot descriptors at context+48. Nonzero values select LP descriptors at +52; only type 1 emits the LP prefix. Type 2 tests document raw machine behavior and do not endorse it as a supported SDK API value.

The scan-control word packs chop/subconversion counts minus one and optional coarse-init bypass. CDAC generation then ORs compensation divider minus one into that word. It writes CDAC clock/dither fields, reference/fine values selected by column/row sensor index and CSD compensation from sensor byte +9. Common status bit 12 suppresses these per-sensor values. The pinned 6.10 header identifies bit 12 as single-calibration and bit 14 as SmartSense; the stock branch is recorded directly rather than assuming that source release's complete behavior.

Only sense method 1 is accepted by the final selected frame generator after CDAC generation; other methods return 1 after earlier writes. CDAC generation itself returns zero. Successful control words include VALID/START bits, adjusted divider minus one, clock-source low bits and LFSR bits.

PRS source 2 shifts the divider by two for methods 1/10 and by one for other methods. There is **no minimum clamp** in the actual helper: a divider below four can become zero; subtracting one then encoding its low twelve bits produces 4095. API inputs therefore need validated configuration, not assumptions from general SDK wording.

## Validation and limits

Passed: 192 mask cases, 180 divider cases, 864 initial sensor-frame cases with an explicitly stubbed CDAC boundary, 1,728 actual CDAC cases and **1,296 complete original/native frame cases with no call stubs**. Complete comparisons include active/LP selection, invalid method after partial writes, clock/divider boundaries, bypass ordering, calibration bit and SmartSense bit. Data is synthetic; no physical scan or acquisition claim.

The all-slot mask/electrode orchestration, generated base frames and auto-dither path remain actionable static leads. No production, index, shared campaign, device or commit writes.
