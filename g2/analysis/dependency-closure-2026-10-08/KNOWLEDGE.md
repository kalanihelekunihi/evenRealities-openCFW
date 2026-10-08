# Bootloader delay, terminal and diagnostic dependencies

These findings come from locked official148,599-byte Thumb bootloader at0x410000, SHA256 f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5. Source-defined offline candidates are not stock byte-identical firmware and are not deployed. Existing official payload providers remain unchanged.

## Delay and termination

CMSIS osDelay416378 uses context guard and returns-6 if rejected; otherwise returns0. Zero ticks skip the kernel call and do not yield. Kernel delay417fa8 with zero ticks requests rescheduling. Positive delay suspends scheduler, removes/inserts the current task using task_block(ticks,0), resumes, and explicitly requests PendSV only if resume returns0. UINT32_MAX is a finite wrapping delay, not indefinite wait; it can place a deadline in the overflow list. Count is scheduler ticks; no wall-time conversion is established. Actual native list/guard/scheduler bodies compare768 cases; interrupt delivery/task switching remain unexecuted.

Task-return41b390 uses stock critical word200004c4. Normal nonsentinel state masks interrupts then performs an invalid-address write and loops. SentinelUINTMAX permits a debugger to release a polling stack slot at entrySP-8, after which raw release word returns inR0. The release is synthetic in tests. Malloc failure41b5f6 prints exact `MallocFaile：cannot malloc memory\r\n` then spins. Stack overflow41b600 prints task name then BKPT0. Platform terminal4329c4 retains status inR7 and enters real IAR exit41b298: semihost operation18 with reason20026, BKPTAB. These are recovered original effects, stopped before faults/traps offline, not replacement traps for unknown code.

DFUterminal42e1da signals manager task1 and loops calling CMSIS delay(UINTMAX), ignoring return status. That body contains no immediate hardware-reset call. Reset/error transaction is a separate path writing original terminal control registers. No physical reset or scheduler lifetime conclusion follows from controlled terminal loops.

## Image metadata and diagnostics

The image header is32 bytes. Its field interpretation below is grounded in actual logger argument captures plus compare/verify/program instructions; opaque words remain opaque.

| Offset | Observed meaning |
| --- | --- |
| 0 | encoded size: low24 bits are declared total file size; bit26 controls CRC/install processing |
| 4 | expected CRC |
| 8,12 | header words not interpreted in this batch |
| 16 | logger prints low byte as `magicNum`; upper24 bits not decoded here |
| 20 | destination/run address |
| 24,28 | header words not interpreted in this batch |

CRC verification skips8 bytes and checks `low24_size-8`; programming skips32 bytes and uses `low24_size-32`. These lengths are raw stock semantics; underflow/malformed small sizes are outside tested-safe inputs. The program callback receives full storage chunk size even when final file read and comparison use a smaller chunk. The progress diagnostic prints remaining bytes and `100-(remaining*100)/low24_size`; its denominator includes the header. The final `---Install end---` string has no placeholders, so incidental saved register values at that call are irrelevant to consumed arguments.

The recovered DFU diagnostic family reports blobSize(low24), crcCheck(bit26), CRC(header+4), magicNum(low byte+16), targetRunAddr(+20), actual short-read byte count and destination vector words. The severity/line-only source interface lost the short-read count; an owned successor task explicitly passes it. Original canonical dfu_task/task.c remains preserved. Fixed call-site bridges support the18 documented source-line IDs; they are not new stock functions and receive no original-byte credit.

Elog's time provider returns a fixed28-byte buffer at20026f18. Original CMSIS tick query chooses task/interrupt helpers through the context guard; both read20027148. Actual original/native provider and formatter compare48 combinations of tick values, context and masks. `%d` prints high-bit counts as negative signed values. The count remains ticks. The EasyLogger startup string reports library version2.2.99; that is not the target firmware version2.2.6.10.

## Read-only dependency repair

Source code retained15 fixed-address update-core diagnostic pointers and21 platform/ADC/logger pointers without corresponding bytes in its ELF. Existing severity/line or raw-pointer child cuts hid this gap. Source-defined NUL-terminated literals now reconstruct those36 strings at their documented addresses. Typed ADC descriptor at43402c is two words{1025,30}; field names and units are not inferred. The entire1,166-byte admitted data set matches stock bytes exactly, with no executable opcodes or padding admitted. Executable segments and predecessor240 source objects are unchanged by these data additions. The full update-core diagnostic test compares97 original/native compare/verify/program cases with declared lower file/runtime/storage/output cuts.

## Validation boundaries

Seven integration cases use synthetic/coherent MMIO, firmware storage and controlled ROM/logger/initializer/interrupt contracts; passing them is a bounded checkpoint, not a complete boot proof. Fatal/logging boundary adapters in older regression suites retain the same declared events at new native addresses. Separate120 terminal-body,48 actual native mask/exit,213 full task-log,88 actual elog/IAR packaging and48 actual timestamp tests provide the stated additional execution evidence. UART sink/ownership, real mutex scheduling, hardware faults, exception delivery, factory state and uncontrolled concurrency remain outside it.

Two logging mutants reject incorrect size mask and discarded short-read count. The second initially revealed a test matcher omission for%u/%zu; corrected matcher and rerun evidence are preserved alongside earlier receipts. A metadata fixture initially returned an arbitrary time string pointer; matching original fixed-buffer ABI resolved that mismatch, with independent actual producer evidence. Source changes and fixture corrections are separate and explicitly recorded.

Resident ROM routines at40,48 and0200ff20 are not in the authenticated OTA image. Further implementation of those functions requires authenticated resident ROM bytes or matching vendor source/build inputs; a returning test stub is not recovery. Establishing physical behavior requires task/interrupt/peripheral traces with relevant clock, calibration, buffer and lifecycle state. Exact byte-identical reconstruction still needs the producing IAR toolchain/configuration and remaining whole-image source coverage. No commits/index/device writes were performed.


## Independent original memory-helper proof

840 Cortex-M55 QEMU cases now execute real stock fill41560c and aligned-copy4156ac against independent source: full guards, rawR0, seededR4-R11,SP and masks. Fill uses out,count,value and returns out; aligned copy's observed raw cursor is out+(count&~1), because the final byte does not advance it. Copy pointers are word-aligned/nonoverlapping in the tested corpus. Fill stock writes backward, source forward; interrupted/access-order equivalence is unproved. These helpers remain standalone; earlier integration oracle models are not silently reclassified. Source objects and fixture ELF reproduce exactly; two mutants rejected.

Resident ROM absence limits recovery/emulation of those external routines; it does not make their known external calls or the OTA's own bytes unaccountable. Byte-identical OTA reconstruction separately needs whole-image source completion and the exact producing build inputs.
