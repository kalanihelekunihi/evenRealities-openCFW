# GX8002 NPU interrupt and configuration candidates

Nine more routines have unique fixed-byte object matches with decoded calls
to the known register primitives. `npu_dis_interrupt` did not match and has
no assigned stock address. The evidence comes from authenticated SDK objects
at the pinned NationalChip commit; those objects are never firmware payload.

All nine routines below are qualified and integrated:

| Routine | Package | Envelope | C bytes |
| --- | --- | ---: | ---: |
| set clock gate | 0xeba4 | 24 | 22 |
| set idle mode | 0xebbc | 24 | 22 |
| set idle cycle | 0xebd4 | 24 | 24 |
| set overtime threshold | 0xebec | 12 | 10 |
| enable interrupts | 0xebf8 | 120 | 120 |
| get interrupt status | 0xec7c | 120 | 118 |
| clear interrupts | 0xecf4 | 120 | 120 |
| clear without overflow | 0xed6c | 88 | 88 |
| clear overflow only | 0xedc4 | 40 | 40 |

The mask mapping is flags1,2,4,8,16,32,64 to register bits0,4,8,12,13,14,16,
in that order. Enable writes through set-bit at base+4; clear routines use
base+8. The no-overflow variant excludes flags16/32, and overflow-only uses
only those two. All other mask bits are ignored. Preserve separate primitive
calls and their repeated read/write sequence. Frames are12 bytes.

Configuration: clock gate uses set-bit12 for any nonzero argument, clear-bit12
for zero. Idle mode reverses polarity: zero sets bit4, nonzero clears it.
Idle-cycle preserves the register low16 bits and replaces its high16 with the
input low16; this is one get-value then one set-value call. Threshold writes
the full argument to base+20. Frames are4 bytes except idle-cycle's12.

Status reads base+12 once. It initially stores `(status&1) | (status bit4?2:0)`
to the output, then conditionally reads/ORs/writes output flags4,8,16,32,64
for status bits8,12,13,14,16. The observed final r0 is `status&0x10000`;
the reconstructed definition preserves that explicitly without asserting an
original private return type. Output is volatile to preserve the ordered
accesses, including where valid modeled aliasing or changing output values
are tested. Frame is8 bytes.

Next qualification must compare stock/source against independent mappings,
cover every low7 mask combination plus ignored high bits, model changing
register responses between primitive calls, helper clobbers and saved frames,
and test status/output aliasing and snapshot versus live-output behavior.
Do not combine the repeated operations into one MMIO write.

Builders:

```sh
python3 g2/tools/identify_gx8002_npu_interrupts.py
python3 g2/tools/build_gx8002_npu_interrupt_mask_candidate.py
python3 g2/tools/build_gx8002_npu_configuration_candidate.py
python3 g2/tools/build_gx8002_npu_interrupt_status_candidate.py
```

Evidence is in `gx8002-npu-interrupt-identification.json` and the matching
`*-linked-candidate.json` reports. These candidates still need verifiers and
regression tests before registration in the integrated build.

Configuration qualification now covers 71,824 stock/source/independent-model
cases and nine tests. All 436 integrated tests pass. The compiler reproduces
the stock payload; 78 C bytes plus six zero-fill bytes replace 84 retained
bytes. Clock/idle nonzero polarity, low-halfword preservation, threshold
address, helper clobbers, call traces and 4/12-byte frames are checked.

Interrupt-mask qualification covers 36,864 cases and nine tests. Each low
seven-bit flag combination is combined with zero, all, or the top ignored
high bits. Latched and independently changing read responses preserve each
individual RMW. The interpreter supports both stock three-register ADDU
and the candidate's saved computed pointer; caller clobbers expose loss of
saved state. All four 12-byte frames are checked.

Status qualification covers 6,144 cases and nine tests: every relevant-bit
combination with all ignored bits clear/set, separate or aliased output,
latched/changing output reads, caller clobbers, eight-byte frame, one status
snapshot, and observed r0. The output operations remain individually visible.

Reviewed reports: gx8002-npu-configuration-verification.json,
gx8002-npu-interrupt-mask-verification.json, and
gx8002-npu-interrupt-status-verification.json. All three are now registered and full integration passes 454 tests.
Physical MMIO semantics remain unqualified.

Interrupt integration replaces 486 C bytes and two bytes of zero fill across
five envelopes (488 bytes). These source instructions differ from stock;
behavior qualification and ownership checks passed before packaging.
