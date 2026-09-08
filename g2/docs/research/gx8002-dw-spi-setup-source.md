# DW SPI setup reconstruction

The full 116-byte stock function at package 0xf71c / runtime 0x10206190
matches the authenticated NationalChip SDK object after relocation. See
[gx8002-dw-spi-setup-attribution.json](gx8002-dw-spi-setup-attribution.json).
The object remains a comparison oracle, never a firmware provider.

The C candidate uses authenticated `spi_device` definitions and a recovered
16-byte controller-state layout. It clears mode, supplies an 8-bit word default,
uses the existing controller state or claims the fixed state at 0x20027ae0,
and returns -12 if that fixed state already has an owner. These initial device
writes happen even when allocation fails. A zero requested speed becomes
10 MHz. The clock helper is called with module 14, and speed is read again
after the helper returns. The divider is the least even integer sufficient
for the clock/speed ratio, with unsigned 32-bit arithmetic. Control combines
format bits, live mode bits, and bit 31. State stores and final device binding
preserve the recovered order. The helper must not change speed to zero;
invalid pointers, concurrency, and division-by-zero behavior remain outside
this candidate's contract pending further recovery.

The native macOS C-SKY build currently emits 120 bytes, exceeding the original
116-byte slot. It is unregistered and unqualified. No payload bytes have been
changed by this candidate. Next work must resolve placement without deleting
behavior, and compare decoded stock/source transactions and ABI across default,
allocation-failure, preallocated-state, and clock/divider boundaries. The helper
body and hardware clock behavior require composition/physical qualification.

An independent transaction model now specifies byte/halfword/word accesses,
helper invocation, final binding, and error returns. Six model tests pass on
macOS Python 3.9. Divider expectations use rational ceiling and even rounding,
separate from the C quotient/multiply expression. In particular, clock
0xffffffff with speed 1 wraps the rounded divisor to zero; this stock behavior
is recorded rather than replaced with saturation. These tests validate the
model's boundary examples, not decoded C execution or hardware. A target
interpreter comparing both stock and candidate against this model is still
required. `-Oz` produced the same size as `-Os`; the builder retains `-Os`.

Decoded stock and C now pass 17,280 cases against the independent model,
including helper caller-register clobbers and preservation of the leaf's caller
state through its 12-byte frame. Five target tests exercise correct cases and
mutations of default speed, module number, divider destination, and a preserved
register. Combined with the six model tests, all 11 pass with
`PYTHONPATH=tools python3 -m unittest tests.test_gx8002_dw_spi_setup tests.test_gx8002_dw_spi_setup_model`
from g2. The report remains `source_admitted: false` because the 120-byte
candidate does not fit. Stack push/pop is modeled as the decoded fixed frame;
helper internals, aliasing device/state objects, asynchronous mutation, and
physical hardware are not established by this proof.
