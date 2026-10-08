# Native startup runtime, INFO cache and memory configuration prerequisites

This batch addresses children of low-power initializer41c4b4 without yet retiring that selected boundary. Locked bootloader f89a4c46 is mapped at410000, little-endian Thumb. Apollo510B is Cortex-M55; offline fixtures use Unicorn's Cortex-M33 execution model, not physical hardware.

## Public-source shortcut and original-byte validation

Pinned Apollo510HAL5.1 commit5efc0228528a8adce5eae0d226fac85d2551eb3b (`upstream-worker/ambiqhal-apollo510/ambiqhal/mcu/apollo510/hal/am_hal_pwrctrl.c`) identifies41c4b4 as `am_hal_pwrctrl_low_power_init`,41c320 as `pwrctrl_INFO1_populate`,41b918 as `TrimVersionGet`,41bbd0 as MCU-memory configuration,41be36 as SRAM configuration and41ce52 as `am_hal_spotmgr_init`. The source corroborates factory trim names and initialization ordering; it does not establish exact producing revision/compiler or let public enum structure sizes replace stock five-byte layouts. Code was independently reconstructed and compared with locked original instructions.

Source: `g2/components/bootloader/initializer_callbacks/startup_runtime.c/.h`, `startup_memory_config.c/.h`, and `startup_initialize_leaves.c/.h`.

| Family | Original bytes | Validation |
|---|---:|---|
|SPOT installer41ce52..41d0ee|668|Native body, flag/MMIO writes and all60 callback-table bytes compare; four selected init callbacks are explicit cuts.|
|Trim-version41b918..41b954|60|Native selector/INFO dispatch/ROM thunk; only resident ROM48 modeled.|
|INFO cache41c320..41c480|352|Nine reads and partial commits compare; marker set only after all reads succeed. Native selector/dispatch/thunk tested.|
|MCU-memory41bbd0..41bd92|450|All450 visited in controlled-entry suite;442 visited with native polling/callback wrappers.|
|SRAM-memory41be36..41bf3a|256|All256 visited with native polling/callback wrappers.|
|Sleep-field and six registered hooks|230|956 direct original/source comparisons, all230 bytes visited.|

832 runtime comparisons PASS,168 native INFO comparisons PASS,936 controlled-entry memory comparisons PASS and936 native poll/callback comparisons PASS. Native memory suite controls only elapsed delay, registered callback body and command/status acknowledgement; remaining8 MCU bytes are a post-poll mismatch branch reached in the separate controlled-entry suite. No SRAM write hooks are installed.

## SPOT interface

The installer clears offsets00..3b of table20026e38. Revision is low byte4002000c; trim version is20000098. It derives flags200271a9..ae, including the inverse low patch bit at2002682c for revision34/trim2 and revision35/trim1. Certain flags change MCU registers40020028/40020060. Revision/trim chooses one of four initial callbacks:42abbc,42bdf0,42d6c0 or42f670; missing callbacks yield zero. The returned init status propagates. Other table entries include power-event handlers, before/after SIMOBUCK hooks and TON configuration hooks.

`runtime-target-frontier.json` enumerates the authenticated stored callback addresses. These are explicit implementation dependencies, not ignored data or proof of callback source closure. The selected-linker denominator remains the original ten OTA boundaries; the new internal callback frontier is recorded separately. Historic manifests claiming production source are not accepted without present code and native validation.

## INFO cache and trim semantics

Trim reads INFO1 word244 only while cached variant isffffffff. A zero result or read error forces cache0; null output returns6 after this potential read/cache update. Native INFO dispatcher intentionally ignores resident ROM status, so a synthetic ROM error is not necessarily exposed as a read failure.

INFO population requires OTP selected (`400201bc` bit3) and powered (`40021008` bit27), otherwise returns7. Reads `(space,offset,count,destination offset from200267f8)` are `(5,480,2,4)`, `(1,204,1,12)`, `(1,206,1,16)`, `(3,208,8,20)`, `(1,210,1,52)`, `(1,240,3,56)`, `(1,24a,2,72)`, `(1,250,12,80)`, `(1,245,1,68)`. On each success corresponding words commit immediately. First failure stops later reads but preserves earlier commits; final marker1f01600d is written only after all success. Available stock and public HAL identify fields including SBL version, patch tracking, temperature and ADC calibration; physical sample values require actual INFO content.

## Memory and ownership semantics

Both configuration inputs are borrowed five-byte records, not public enum-sized structures. MCU-memory cached ROM mode is written before validation. It computes different command/status masks, optionally forces AXI clock, disables unwanted power, calls operation5 with a borrowed stack desired-status word, then enables wanted power. The callback may mutate that word; its status is ignored. Initial polling failure can leave the AXI force bit set, while second-stage failure clears it. Invalid later cache-enable byte returns5 only after earlier side effects.

SRAM configuration compares raw requested byte with three-bit status before masking the command. On increase, operation6(enabled1) receives the borrowed configuration pointer before the write; on decrease, operation6(enabled0) receives null after acknowledgement. Callback status is ignored. It then updates retained-bank masks and timer power fields. No allocation, ownership extension or asynchronous retention is proven by either wrapper.

## Remaining closure

Selected initializer41c4b4 remains unbound. Its runtime init callbacks/event callbacks and clock-mux reset41acb2 are being recovered independently; unresolved bodies are not replaced by their historical source-owned labels. Seven integrated startup/logger providers still use existing models, so integration passing does not demonstrate native execution of these new bodies. ROM implementation, physical INFO values/peripheral acknowledgements, IRQ/task scheduling/drain, producing compiler, full-source completeness and byte equality remain outside this proof.

## Promotion

Checkpointc6a3ac92c9a69b906b8b8f7c3ec1a12d79928f5a58ae7367f731600fd157b5e1 promoted after all7 cases PASS,31 direct/regression receipts PASS,681 files/175 objects unchanged with exact frozen copies authenticated,496 mappings PASS and zero manifest mismatches. Prior64e52504/4edd remain preserved. Selected OTA entries10→10, same address-based scope; no new aliases. Seven-case observed instruction footprint remains38764/148599, not source-completeness or native integration coverage for these modeled startup bodies.
