# Independent review: Apollo GPIO IRQ subset

Review scope: `ambiq_gpio_irq.c/.h`, the ARM32 sparse compatibility view, build integration, pinned-source provenance, and the original/source Unicorn verifier. Read-only review; no firmware source or shared evidence was changed.

## Result

No blocking correctness or evidence-integrity defect found in this bounded subset. The final comparison at `g2/build/foundation/ambiq-gpio-simulator/comparison-final.json` reports PASS for 773 inputs. Its ELF hash, verifier hash, and C/header/linker-script source manifest match the current files. Four host tests in `g2/tests/test_ambiq_gpio.py` passed, including unchanged upstream excerpt/license checks, linking against the real PRIMASK provider, ARM32 callback/register ABI checks, and optimized-Python fail-closed behavior.

All four attributed function texts match the pinned Ambiq source excerpt hashes in `SOURCE_PROVENANCE.json`, with the BSD-3 Ambiq notice retained. The sparse compatibility ABI explicitly fixes the stock callback-table locations, four-byte pointers, seven-bank channel stride, and GPIO status/clear register offsets. The module uses the real `MRS PRIMASK` / `CPSID` / restore implementation for the status read critical section.

## Coverage and bounds

The comparison exercises all 126 bytes of status-get, 58 bytes of clear, and 154 bytes of registration, plus 110 reachable bytes of the 116-byte service body. The missing six service bytes are accounted for rather than silently treated as covered: `[0x4816ea,0x4816ee)` and `[0x4816fa,0x4816fc)`. Under the function's input guard, accepted IRQs are only 56–62 or 125–131. The first span requires contradictory IRQ bounds (`<63` and `>=125`); the second is reached only for 63–124, which the guard rejects. The verifier asserts this exact unreachable set.

The fixtures exercise status filtering, invalid IRQs and null output, clear bank addressing, channel registration and BOTH behavior, callback ordering/missing callbacks, and mutation of a later live callback slot by an earlier callback. Status MMIO accesses assert PRIMASK is masked and that the prior value is restored. The verifier authenticates the locked firmware payload and each compared body before replay.

## Limits

This is a GPIO interrupt subset, not a GPIO initialization or board driver. Registration checks channel only; callers remain responsible for valid pin/bank, callback lifetime, and serialization against dispatch. The fixtures do not establish real pad availability, GPIO initialization, electrical behavior, physical interrupt delivery, callback scheduling/concurrency safety, or a hardware W1C transaction. W1C clearing and callback functions are simulator fixtures. The comparison supports functional agreement for the selected stock bodies and inputs; it does not establish compiler/whole-firmware byte identity.

The GPIO Make target writes the verifier report with exclusive-create semantics. A repeat using the same default report filename can fail because the old report exists; set `GPIO_SIM_REPORT` to a fresh path when rerunning. This is a minor repeatability inconvenience, not a correctness issue.

## Cumulative accounting follow-up

The inventory arithmetic reconciles: 234 unique touch bytes plus 1,158 Apollo bytes equals 1,392 unique traced bytes. Evidence-input increments sum to those same payload totals (232+2 touch; 230+480+448 Apollo). The 448 executed GPIO bytes are the only GPIO trace increment; its six statically unreachable bytes are listed separately and excluded. The eight shared critical-helper bytes were already present and add zero unique bytes. Touch's trapped BKPT observation remains counted as an observed trace byte with that limitation stated; failed delay-decoder diagnostics and 24 statically decoded ITCM bytes are explicitly excluded.

The 22 listed source files all match their hashes and none is ignored: 9 implementation C, 10 headers, and 3 simulator entry/seam C files. All five callable-profile ELF hashes match current outputs. Their symbol lists are per-profile inventories, not additive function or completeness counts. The narrative and JSON both say no blob-free firmware payload and no byte-identical source-built bundle have been proven. The 33-module aggregate is internally consistent at 189 tests, 183 passes, zero failures/errors and 7 skips; the GPIO module contributes four passing tests.

The accounting is appropriately labeled a snapshot. Its evidence inputs include older receipts whose original compiler/source provenance and scope stay in force; this reconciliation does not upgrade historical inputs into a newly rerun end-to-end provenance pipeline. I found no material accounting contradiction or completeness overclaim.
