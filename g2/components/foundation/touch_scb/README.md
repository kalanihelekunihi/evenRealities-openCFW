# Touch SCB read-array wrapper

This small callback-based component reconstructs the behavior of the 30-byte
`Cy_SCB_ReadArray` wrapper at decoded touch-image address `0x9250`. The FWPK
payload contains a 32-byte prefix; decoded image base is `0x3300`. Its body is
`[0x5F50, 0x5F6E)` within the decoded image, SHA-256
`c7729e5dfb38b7391112b5eeeb9e0a8b0fc0d2ad0bc2e1e9b53b353b401e5e49`.

The firmware-shaped API masks the RX FIFO status callback result with `0x1ff`,
clamps requested count to that available count, calls the supplied
`read_array_no_check` callback exactly once even for a zero count, and returns
the clamped count. It does not name an MMIO address or claim a hardware FIFO
implementation; the callback boundary represents the observed read of the
SCB RX FIFO status and call to the separate 56-byte `Cy_SCB_ReadArrayNoCheck`
body. A provider would need to implement the actual device contract.

`touch_scb_read_array_checked` is an additional host/adapter convenience. It
validates required pointers and callbacks, accepts only element widths 1 or 2,
checks destination capacity in bytes, and returns an explicit error. Those
checks do not occur in the recovered firmware wrapper. The adapter reads the
status once to determine the clamped count, checks capacity, then invokes the
transfer callback only on success. A hardware status read may itself have
device-specific effects; those are the provider's responsibility.

## Evidence and limits

The source-level correspondence is Infineon's Apache-2.0 PDL 2.21.0
`Cy_SCB_ReadArray` at the pinned source URL:
<https://raw.githubusercontent.com/Infineon/mtb-pdl-cat2/35f1714623cfea682d5e285af80d50416b4c7bbc/drivers/source/cy_scb_common.c>
(lines 99–113 as inspected for this task). The separate exact comparison of
`Cy_SCB_ReadArrayNoCheck` covers 56 bytes at decoded image `[0x5F18, 0x5F50)`;
this component's 30-byte wrapper range is adjacent and does not overlap it.
The neighbor has source-level behavioral correspondence, not a compiler byte
match. Its original instructions and the six bounded emulator cases are
recorded in
[`../../../analysis/shortcut-batch-2026-10-05/touch-upstream/results.json`](../../../analysis/shortcut-batch-2026-10-05/touch-upstream/results.json).

No firmware link provider, device build, or MMIO/FIFO implementation is part
of this component. The six original-code tests intercept the 56-byte callee
entry, so they verify only the wrapper's clamp, arguments and return value.

The reconstruction is new MIT-licensed code. That license does not apply to
Infineon's upstream source or the official firmware. The upstream implementation
remains Apache-2.0; consult its license terms before copying any upstream code.

## Validation

Run the component tests from `g2/` with
`python3 -m unittest discover -s tests -t . -p 'test_touch_scb.py' -v`.
They compile and execute a host callback harness, compare the six original
wrapper cases against the saved original-code result, and additionally test
equal requested/available count, `UINT32_MAX` requested with availability 2,
adapter widths 1 and 2, capacity errors, unsupported width, missing callbacks,
and zero available data with zero output capacity. Host fixtures use real
pointers and an eight-byte output buffer for the halfword case.

The expanded original-code oracle is reproducible with
`~/.local/share/opencfw/venv/bin/python g2/components/foundation/touch_scb/validation/verify_original.py`.
Its `results.json` records eight original-wrapper cases, including the two
held-out inputs, exact wrapper/callee bytes and hashes, the source script hash,
and each executed original PC/instruction. The original 56-byte callee entry
is stubbed to record arguments and return a sentinel; this does not execute the
callee or test FIFO/MMIO effects. No firmware image is linked or changed.

## Register providers and callable simulator (2026-10-05)

`touch_scb_mmio.c` supplies actual volatile RX register accesses and
`touch_scb_tx.c` supplies TX. TX derives depth (8/16) from CTRL, reads used
entries at +0x208, selects byte/halfword source loads at +0x200 and writes
32-bit FIFO entries at +0x240. Raw TX preserves stock unsigned subtraction
when reported usage exceeds depth; checked TX rejects that condition. Callers
must supply mapped registers and serialize configuration and FIFO ownership.

`make touch-scb-simulator-test SCB_SIM_DIR=build/foundation/<new-directory>
SCB_SIM_PYTHON=<Unicorn-enabled-python>` compiles and links all three providers
plus the callable entry module. It compares eight RX and eleven TX inputs
against complete original wrapper/callee instruction sequences without callee
stubs, then checks five RX and nine TX adapter cases. Reports use exclusive
creation, record ELF/verifier/source hashes, and reject optimized Python.
The synthetic FIFO stimuli do not establish bus timing, interrupts, DMA,
concurrent access, startup or board wiring. This module has no reset vectors
and is not a bootable replacement firmware. Earlier evidence above remains
historical; use the new linked comparison for provider validation.

The adjacent `touch_scb_fifo.c/.h` checked RX trigger setter is also linked.
Five valid original/source comparisons cover both FIFO depths and upper-bit
preservation; four invalid source cases return errors rather than stock BKPT.
The separate original nine-case oracle is under
`g2/analysis/touch-mmio-cycle-2026-10-05/next-fifo/`. Final linked evidence is
`g2/build/foundation/touch-scb-trigger-final/comparison-reviewed.json` (232 observed
original bytes); including the original invalid breakpoint gives234 bytes.
No trigger-to-interrupt firing behavior is established by this evidence.
