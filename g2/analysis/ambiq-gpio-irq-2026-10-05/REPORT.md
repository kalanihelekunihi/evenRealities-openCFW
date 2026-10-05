# GPIO IRQ delivery foundation

This cycle moved away from the unresolved delay emulator diagnostic and implemented a directly consumed GPIO family: individual IRQ status, clear, callback registration and service. Four unchanged pinned public Ambiq HAL bodies now live in `g2/components/foundation/ambiq_gpio/ambiq_gpio_irq.c`, with reusable declarations in `ambiq_gpio.h` and a deliberately sparse stock ARM32 view in `ambiq_gpio_compat.h`. `SOURCE_PROVENANCE.json` records public commit5efc0228528a8adce5eae0d226fac85d2551eb3b, authenticated Git blobs, BSD-3-Clause notice and excerpt hashes. No whole-driver attribution or complete firmware equality is claimed.

## Concrete firmware consumer and recovered behavior

`HciDrvRadioBoot` at0x4b48a6 calls registration at0x4b49b2 with channel0, pin117, handler0x4b4a99 (Thumb0x4b4a98), argument0. That is bank3/bit21: callback slot0x200683fc and argument slot0x20068afc. `GPIO0_607F_IRQHandler` at0x4b80be obtains an initial seven-word all-bank snapshot whose values it does not subsequently use, then calls status(IRQ59, enabledOnly=false), clear(mask), service(mask), ignoring their return codes. These are static authenticated caller facts, not a executed hardware ISR claim. Exact caller/site hashes are in `original/results-final.json`.

| Function | Stock address | Body bytes | Behavior |
| --- | --- | ---: | --- |
| am_hal_gpio_interrupt_irq_status_get | 0x481574 | 126 | Null/invalid IRQ returns6; valid status reads are PRIMASK-masked, optionally filtered by EN, with previous mask restored. |
| am_hal_gpio_interrupt_irq_clear | 0x4815f2 | 58 | Invalid IRQ returns6; valid call writes the supplied mask once to CLR. No wait. |
| am_hal_gpio_interrupt_register | 0x48162c | 154 | Channel0/1/both publishes callback then argument in selected table(s); invalid channel returns6. No pin bounds check or critical section. |
| am_hal_gpio_interrupt_service | 0x4816c6 | 116 | Invalid IRQ returns5. Ascending set-bit dispatch reads live callback/argument slots. Missing callback sets return7 and processing continues. Zero valid mask returns0. |

IRQs56..62 /125..131 select seven32-bit banks per channel. EN/STAT/CLR start at0x40010530/534/538; bank stride0x10, channel stride0x70. For IRQ59 the targets are0x40010560/564/568. Callback and argument arrays are separate14x32-word tables at0x20068228 /0x20068928. These layouts are recovered interfaces; initialization, physical pin availability and asynchronous publication are separate responsibilities.

For CFW/app integration, preserve the distinction between raw pending status and enabled-only status: this stock ISR asks for raw status. Clearing pending bits precedes callback dispatch, while missing callback errors are ignored by this caller. Callback arguments must remain live through dispatch; registration does not transfer/free ownership, validate a pin, or serialize callback publication. Synthetic mutation tests show that a callback can alter a later slot in the same dispatch; service reads that later slot live rather than snapshotting the table. This is a tested serialized fixture, not proof of a race on hardware.

## Actual source build and fresh validation

`make -C g2 ambiq-gpio-simulator` builds a separate source-only callable module, using the actual shared PRIMASK entry/restore provider. The GPIO build selects a Cortex-M4-compatible Thumb-2 subset valid on Cortex-M55, because the M55 optimizer emitted CSEL unsupported by installed Unicorn. The target identity remains the authenticated M55 firmware; this is a compatibility compilation, not an M4 hardware claim. `-fwrapv` defines the unchanged upstream FFS expression's signed-negation wrapping for bit31.

The final `g2/build/foundation/ambiq-gpio-simulator/comparison-final.json` passes773 fresh original/source cases and independent expected-state checks. Tests exercise every accepted IRQ bank and invalid boundary, prior PRIMASK0/1, raw/EN-filtered status and null output, mask endpoints/all bits, registration channel and bank boundaries, null/missing handlers, ascending callback order, arguments and later-slot mutation. They compare full callback/argument tables, output writes, MMIO reads/writes, callback calls, and final mask state. Every MMIO status read is observed with PRIMASK1.

**454 original body bytes are identified;448 execute.** Six bytes at[0x4816ea,0x4816ee) and[0x4816fa,0x4816fc) are statically unreachable after the original valid-range guard: one path requires IRQ<63 and>=125; the other requires IRQ63..124, already rejected. The verifier asserts the exact missing ranges, reports them separately, and does not promote entire code pages. The shared critical helper's eight bytes execute again but contribute **zero new bytes** in this cycle. No new exact compiled-body equality is claimed for GPIO.

Four new GPIO unittest methods pass. `foundation-test` now includes GPIO:33 focused methods pass across touch, HAL and resources. The affected aggregate runs33 modules/189 method invocations:183 pass, zero failures/errors, six method skips plus one class setup skip. Independent review found no blocking issue; see `review/report.md`.

Only injected callback fixtures are intercepted. W1C semantics are synthetic. The tests do not establish pinmux, clocks, NVIC setup, electrical events, callback concurrency, preemption, cache effects or actual radio callback behavior. Read the caller preconditions in `ambiq_gpio.h`. Reports are exclusive-create; choose a fresh `GPIO_SIM_REPORT` on rerun.

## Reconciled cumulative inventory

`cumulative-inventory.json` and its rerunnable script bind each source file, callable target and original trace input. The current foundation has22 C/header files:9 implementation C files,10 interface/compatibility headers and3 simulator entry/seam C files. All are visible to Git, not ignored. Five callable linked target profiles exist; their shared source/API symbols are listed per target and are not summed as independent implemented bodies. Production reference providers remain official binaries.

Deduplicating actual trace bytes by payload identity+runtime address, and checking byte values agree on overlaps, gives **1,392 unique original trace bytes**:234 touch and1,158 Apollo. That is the prior944 plus448 new GPIO bytes; lifecycle, CMDQ and the critical helper are counted once despite repeated tests/profile links. Touch includes a two-byte trapped BKPT observation, clearly distinguished from completed-path/hardware proof. The six statically unreachable GPIO bytes are excluded from trace counts. Failed scatter decoder diagnostics and statically decoded ITCM bytes are also excluded. Test case counts and source-file counts do not measure firmware completeness.

No complete blob-free source payload or source-built byte-identical bundle has been demonstrated. Protected packer, manifest, workflow state and official Apollo hashes remain unchanged. Prior maps/reports and failed diagnostics are preserved; no staging commands, commits, flashing, deployment or shared campaign edits were performed.

## Exact remaining boundary and next useful batch

Delay remains inconclusive: the authenticated startup/ITCM record and static mirrored decode explain where the loop comes from, but installed Unicorn fails the decoder's conditional branch. Those diagnostics remain intact; this cycle did not force them or claim missing ROM/adjacent input. Full delay FP/clock conversion, runtime initialization and physical timing are separate gaps.

The next useful GPIO contract is interrupt-enable/control around pin117 callback publication and radio GPIO configuration, using the already pinned source and caller evidence. It can connect this IRQ-delivery primitive to a defensible setup/teardown sequence. Callback ownership and actual scheduling still require their own proven contracts; no speculative memory or interrupt-management patch is supplied.
