# DFU runtime-context getter and wrapper

## Result

`runtime_context.c` reconstructs stock `runtime_context_get_42d88a` and the
manager-task call wrapper `runtime_context_wrapper_42dd68`. The standalone
source-versus-image test passes one direct getter case and five wrapper cases,
reaching all 14 original instruction bytes across the two routines. The
verified image is `ota_s200_bootloader.bin`, SHA-256
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

Reproduce with `make test`. The linked source ELF, input state cases, stock
instruction trace, and source/image hashes are in `out/comparison.json`.

## Exact source closure

At `0x0042d88a..0x0042d890`, stock executes `ldr.w r0, [pc, #0x878]` and
`bx lr`. The PC-relative load reads the word at `0x0042e104`, bytes
`00 40 60 00`, value `0x00604000`. The readable source returns that fixed
32-bit value. The leaf has no calls, writes, scheduler access, or side effects.

At `0x0042dd68..0x0042dd70`, stock executes `push {r7,lr}`, calls the getter,
then `pop {r0,pc}`. The call's R0 result is overwritten by the saved R7 during
the pop. This wrapper therefore returns the incoming R7 value in R0 and leaves
R7 unchanged. The source uses the same bounded wrapper sequence in inline
assembly so that its private register behavior is preserved. The public
declaration is `void` because the manager orchestrator discards the return;
the implementation still produces the stock R0 value.

The caller at `0x0042dd14` invokes the wrapper at `0x0042dd1e` after the queue
context initializer at `0x0042dd70`, then continues to a no-op callback and
control-two wrapper. It does not inspect the wrapper return. This closure
performs no runtime-context initialization and publishes no queue state. In
particular, the loaded `0x00604000` value is discarded. Queue creation and
publication remain separate providers, outside this leaf's responsibility.

## Differential checks and limits

The source and original getter both return `0x00604000`. The original and
source wrapper were run with incoming R7 values 0, 1, `0x13579bdf`,
`0xffffffff`, and `0x00604000`; each returned that exact value in R0, retained
R7, and restored SP. The stock ranges and hashes are verified in the fixture:

| Function | Range | Bytes | SHA-256 |
|---|---|---:|---|
| getter | `0x0042d88a..0x0042d890` | 6 | `a38decb7c6c890f46354bc3a4b166bd89e4dac78108f0a6eb1e6123e61ad8087` |
| wrapper | `0x0042dd68..0x0042dd70` | 8 | `86bf8be3cfef3a107d8691b1fb960ba63cc40d3ef6eb8ed906638e24001e1a84` |

Unicorn exercises only these instructions with synthetic RAM/ROM mapping. No
queue, scheduler wait, peripheral, or hardware service is executed here.
