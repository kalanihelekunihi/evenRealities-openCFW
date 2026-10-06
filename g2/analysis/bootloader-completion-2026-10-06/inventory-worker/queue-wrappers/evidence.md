# Apollo bootloader queue-wrapper source evidence

Target: the stock locked G2 2.2.6.10 `ota_s200_bootloader.bin`, SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, loaded at `0x00410000`. Runtime/file offset is `address - 0x00410000`; wrapper ranges below are half-open.

## Recovered wrapper contracts

| Function | Runtime range | File offset / size | Raw Ghidra body SHA-256 |
|---|---:|---:|---|
| Context predicate (`FUN_0041602a`) | `[0x0041602A,0x00416058)` | `0x602A`, 46 B | `e9208bab7b82a1d6f0228d69b2707c5cfadd5cb45b7d24963defe8cabb00b32b` |
| Queue create | `[0x00416816,0x004168A2)` | `0x6816`, 140 B | `0529769ef0cd634c8a643a7c412f804d9c530fcc2e5b54a87b532b8ec3fb583a` |
| Queue put | `[0x004168A2,0x00416920)` | `0x68A2`, 126 B | `91e5690abdb827a51e097c4a062fe375df5157e3f2039d736b298b22e04868be` |
| Queue get | `[0x00416920,0x0041699A)` | `0x6920`, 122 B | `314c0a49b1cd6147c22638e354ac5e1fc82bf310547a5fb38a897f4f263c784e` |

`original-context-disassembly.txt` and `original-wrapper-disassembly.txt` are raw-instruction listings from `arm-none-eabi-objdump` over that pinned file. The separate original-instruction/source fixture records a 418-byte executed trace across the tested branches.

### Context predicate at `0x41602A`

The instructions read IPSR first. A nonzero exception number returns 1. In thread mode, the helper at `0x418B56` is called; its raw body returns 1 if the word at `0x20027150` is zero, 2 if that first word is nonzero and the word at `0x2002716C` is zero, otherwise 0. If its result is 1, the predicate returns 0 immediately. For results 0 or 2, it returns 1 when PRIMASK is nonzero, or when BASEPRI is nonzero; otherwise it returns 0. The meanings of those two pointed-to words are not assigned here.

This corrects the apparent Ghidra pseudocode control-flow inversion: in original bytes `cmp r0,#1; beq 0x416054` reaches the initialized-zero result. Treating helper result 1 as “nonblocking” would invert behavior.

### Queue creation at `0x416816`

- A nonzero context-predicate result, zero message count, or zero item size returns null.
- The six-word attributes layout is `name@+0`, `attr_bits@+4`, `cb_mem@+8`, `cb_size@+12`, `mq_mem@+16`, `mq_size@+20`. `name` and `attr_bits` are unused by this body.
- With non-null attributes, static storage is accepted only when `cb_mem != 0`, `cb_size >= 0x50` (80 bytes), `mq_mem != 0`, and `mq_size >= uint32(msg_count * msg_size)`.
- The product is the low 32 bits: original `MUL.W` has no preceding overflow rejection. Thus the wrapper can accept a wrapped product; it leaves validity/allocation consequences to the callee.
- Dynamic allocation is selected only when all four storage fields are zero. Any mixed/partial/undersized combination returns null.
- Static helper call at `0x419C9C`: `r0=count, r1=item_size, r2=mq_mem, r3=cb_mem, stack[0]=0`. Dynamic helper at `0x419D08`: `r0=count, r1=item_size, r2=0`. Both return a queue handle in `r0`.

### Queue put at `0x4168A2`; get at `0x416920`

Both use the scalar AAPCS argument pattern `r0=queue, r1=message, r2=priority/priority-output, r3=timeout`. `r2` is ignored. Their epilogues explicitly load the result into `r0`; Ghidra's `undefined8` signature is a false wide-return inference. Return values proven by the original MOVN instructions are `0` success, `-2` timeout result, `-3` resource/unavailable result, and `-4` parameter/context rejection.

- In the context-predicate-zero path, null queue/message returns `-4`; the queue core is called with raw timeout and a zero final argument. Core result exactly 1 maps to 0; otherwise timeout 0 maps to `-3`, nonzero timeout to `-2`.
- In the predicate-nonzero path, null queue/message or nonzero timeout returns `-4`. Put calls the ISR queue core with `(queue,message,&woken,0)`; get calls its ISR core with `(queue,message,&woken)`. Core result exactly 1 maps to 0; other results map to `-3`.
- After ISR success, nonzero `woken` writes `0x10000000` to SCB ICSR at `0xE000ED04` (PendSV set). The message-priority argument is not forwarded; put supplies a literal zero to the core.
- Timeout is forwarded as an unchanged 32-bit argument. This wrapper evidence does not prove its unit or a scheduler tick rate; the candidate deliberately names it `timeout`, not “ticks.”

## Candidate files and checks

- `queue_wrappers.c` / `.h`: architecture-correct readable C candidate, including real M-class reads of IPSR/PRIMASK/BASEPRI, exact attributes/return behavior, and deferred-switch write.
- `module.ld`: original internal helper/core call addresses separated from source. Those queue-kernel callees are explicit dependencies, not implemented or version-pinned in this worker.
- `verify_queue.py`: compares original bytes against compiled source while intercepting the runtime-mode and kernel-queue providers at their exact local addresses. It exercises context state results 0/1/2, masked contexts, dynamic/static/invalid/partial attrs, wrapped products, blocking and nonblocking send/receive outcomes, timeout zero/nonzero/`0xFFFFFFFF`, ignored priority output, and PendSV setting.
- Build: `make -f Makefile OUT=/tmp/queue-wrappers` succeeded for Cortex-M55.
- Validation: `/Users/kalani/.local/share/opencfw/venv/bin/python verify_queue.py --elf /tmp/queue-wrappers/queue_wrappers.elf --output /tmp/queue-wrappers/queue-comparison.json` passed **45 cases** after the final test expansion; `queue-comparison.json` is copied beside this report.

Limits: the fixture executes original wrapper/context instructions but supplies synthetic context-mode and kernel-queue results. It does not execute the queue kernel, prove scheduling or ISR wake semantics, establish timeout units, or exercise physical interrupt hardware. Nonzero IPSR could not be injected by this fixture; PRIMASK and BASEPRI nonblocking paths are covered.
