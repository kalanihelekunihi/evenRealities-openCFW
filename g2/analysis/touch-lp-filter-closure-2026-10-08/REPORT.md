# LP hardware processing configuration and launch/reuse lifecycle

**1,952 original/source comparisons pass**:1920 guarded LP launch/composition cases and32 reset-copied configuration compositions. The latter execute explicit initialization/preparation slices, full LP launch, original/native ISR completion, repeated launch after frame mutation and a synthetic configured-window history transfer. No function-entry stubs. Source: ../../components/touch/lp_scan_offline/scan.c,h; original launch0x6d74..0x702c.

## Filter configuration recovered

Initialization slice4c84..4d8e sets LP raw coefficient1, baseline slow6/fast4, update delay10. Preparation slice71c8..7228 generates all four LP frames from the actual reset-copied widget0 configuration. The first five words are:

| Word | Stock-default value | Pinned public field interpretation |
| --- | --- | --- |
|0|0x0a1e0461|raw coefficient1, slow baseline6, fast baseline4, low-baseline reset30, update delay10|
|1|0x001e001e|positive and negative noise thresholds30/30|
|2|0x00010096|signal threshold150, debounce1, CSD signal-type bit0|
|3/4|0/0|initial processing state words|

Numbers are encoded register/count parameters; no voltage, elapsed milliseconds or filter transfer function is inferred. Changing the injected raw coefficient1→15 changes only word0's low nibble, as expected.

At0x6e16 the launch loads literal0x80000100 into HW+0x74 (`CE_CTL`). Pinned PDL header defines ENABLED bit31, BLSD_EN bit8 and RCF_EN bit0. **Channel engine and baseline/signal detection are enabled; LP raw IIR enable remains clear in this launch path.** A nonzero coefficient in the frame does not imply raw IIR is running. LP frames are copied as eleven words per slot into HW+0x2000. LAST mask0x4 (bit2) is ORed into the final slot's last word, SENSOR_INIT mask0x1 (bit0) into HW+0x3c00, then bridge-ready bit1 at+0x341c is checked.

Pinned public CapSense6.10 `Cy_CapSense_ScanLpSlots` follows this topology and conditionally enables RCF via CY_CAPSENSE_LP_RC_IIR_FILTER_EN. Source SHA/pin is retained; it is a semantic comparator, not a demonstrated exact whole-function compilation or unique producer release. The repository gitlink25fa... is a separate older dependency and was not changed.

## Actual launch behavior and errors

Guard context!=NULL, count1..8 and unsigned last=first+count-1<=3. Supported coherent project ranges in tests have first0..3/count1..4; unsigned overflow is not endorsed as a valid API. Invalid calls return1. Clear common status0x400 **before** testing busy bit0x80; busy returns0x40, so even a busy rejection clears signal-detected state.

Switch to mode2 through the recovered mode/GPIO/public PDL composition. A switch error returns immediately. Then set busy masks0x81 and repeat flaginternalbyte115=1. Reconfiguration sets current/end/count, operatingmode3, CTL operating bits, clears configuration offset and disables hardware. If IMO is down, request MRSS_START and wait315 iterations using existing actual delay/wait instructions. That return is propagated on this new-range path. If bridge is not ready after frame copy, return4. Even these failures set LP scan status0x20 and retain busy flags; no automatic cleanup is reconstructed here. An app/CFW caller must account for partial state changes on error rather than assume failure was side-effect free.

Successful configuration clamps internal timeoutu16+74 to0x3fff, programs AOS timeout/power-cycle and intervalu32+40, and sets result start address. These are raw fields/cycle parameters, not newly established wall-clock units. Start callback, if nonnull, receives active-scan-context pointer; this batch uses null callbacks. Disable/enable CTL, set/read interrupt mask0x10 and OR WAKEUP_CMD1. This is direct software launch, not physical scanning proof.

## Reuse does not reload changed coefficients

If current/end match and LP status0x20 remains set, skip frame copy and SENSOR_INIT. MRSS stop wait126 return is discarded on this reused path. The actual composition tests launch, invoke the full original/native ISR to clear busy, change RAM coefficient1↔15, then launch the same range again. Both sides return0 and perform **zero SENSOR_DATA stores**; the hardware coefficient remains the previous value. Static MRSS status deliberately forces the stop wait to time out, yet its error is ignored.

Thus editing a generated frame does not guarantee immediate filter reinitialization. A design needing changed processing settings must establish a reconfiguration path and callback/concurrency safety; no patch or production manipulation is implemented here.

## Configured result window and history allocation boundary

Stock computes `start=256-((floor(256/count)-11)*count)`, and programs SCAN_CTL1 result-start bits16..25. The pinned device configuration defines MSCLP_SRAM_SIZE1024 bytes, hence256 words. The generic IP header's SENSOR_DATA[1024] aperture is not proof that this chip supplies1024 words. Public source calls this a FIFO start-address configuration.

| LP slots | Programmed start word | Nominal complete result words | Frames | Logical u16 history bytes |
| --- | --- | --- | --- | --- |
|1|11|245|245|490|
|2|22|234|117|468|
|3|34|222|74|444|
|4|44|212|53|424|

Four-slot arithmetic fits424 bytes before the next known object426 bytes away. This offers a coherent configured-window explanation for the full range, **not a declared allocation**. The earlier54-frame overwrite required synthetic used216; it is not established to occur with this four-slot configuration.

After launching each range, tests inject the nominal complete-result count and FIFOraw0, enable the history gate, and invoke ISR. The1/2/3-slot synthetic transfers touch the next object, whereas4-slot212-value transfer does not. These demonstrate machine behavior under supplied counts. They do not prove real FIFO occupancy/wrap/saturation, partial-slot application reachability or a hardware defect. The sole direct BL found to0x6d74 is0x705a in wrapper0x7050, which supplies first0/count4. Indirect aliases/callback calls are not excluded by that bounded scan. No later access through corrupted partial-slot context is modeled.

No producer-generated cycfg history declaration or official target link map was found in documented configuration/campaign/dependency paths (allocation-boundary.json). Capacity remains blocked specifically on that artifact; physical backlog behavior needs an appropriate trace. No reason to expand metadata or invent a CPU consumer to fill either boundary.

## Validation limits and reproduction

Synthetic tests cover invalid counts/ranges, busy, prior modes0/2, requested reuse, MRSS states, bridge readiness and PDL driver locks0/2. Original6d74 and independent source execute recovered dependencies/public PDL, comparing MMIO read/write sequences, persistent SRAM and registers; dead stack0x20007c00..0x20008000 is excluded because compiler frames differ. Actual compositions compare reset-copied RAM0x20000000..0x20002000 and the hardware block. They use initialization/preparation **slices**, force prior mode2 before launch and inject coefficients/MRSS/bridge/FIFO; full startup and physical IRQ/analog/filter dynamics remain unproven.

build_offline.py with the GCC/public-object/output arguments recorded in reproduction-receipt.json rebuilds the scratch ELF; verify.py ELF reproduces1952 cases. No shared campaign, production firmware, Git index, commit or device writes. Preservation verifies prior610 sealed entries,110 inputs and4 checkpoints. Previous evidence: ../touch-lp-history-closure-2026-10-08/REPORT.md and ../touch-scan-isr-closure-2026-10-08/REPORT.md.

Next bounded dependency: reconstruct the all-LP wrapper0x7050 and its application caller/retry behavior, specifically how launch failures or requested reconfiguration are handled. Full generated allocation requires the external artifact above; it remains independent from software closure.
