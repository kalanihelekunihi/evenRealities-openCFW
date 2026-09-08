# GX8002 NPU register and control recovery

The register primitives now have a fully defined portable C path and an
optional native path containing three explicit C-SKY instruction wrappers.
Both compile from `runtime_gx8002_npu_registers.c`. The native path fits the
original slots; the portable path remains a separately linked comparison
oracle and never contributes firmware bytes. Authenticated SDK objects supply
symbol identity only, not firmware payload.

The ISA documents low-six-bit shift/rotate counts and a zero result for counts
32..63. The C fallback preserves this without undefined shifts. Consequently
get-bit returns0, set-bit performs an unchanged read/write, and clear-bit
clears the whole word for those counts. Counts wrap modulo64. The native
wrappers use LSR, LSL and ROTL directly to preserve that behavior within the
small original slots. The three whole routines are conservatively accounted
as `compiled_assembly`, including their compiler-generated loads/stores.
Ordinary word read/write are `compiled_c`.

| Helper | Package | Envelope | Native bytes | Portable bytes |
| --- | --- | ---: | ---: | ---: |
| get bit | 0xeb4c | 12 | 10 | 26 |
| set bit | 0xeb58 | 16 | 12 | 28 |
| clear bit | 0xeb68 | 16 | 14 | 28 |
| read word | 0xeb78 | 4 | 4 | 4 |
| write word | 0xeb7c | 4 | 4 | 4 |

Stock, native and portable decoded implementations match an independent
register oracle in 86,296 cases. Counts cover all64 low-bit patterns and high
count bits; word values include all single-bit and inverted-single-bit
patterns. Twelve regression tests cover the boundary counts, rotate versus
shift, memory accesses and ABI. Each function performs the same ordered
32-bit access sequence as stock and uses no stack. This verifies documented
instruction semantics in a model, not physical MMIO or target timing.

Four C control wrappers are qualified separately and composed with the
decoded primitives in 2,412 cases; seven regression tests pass. Enable,
disable and status use bit0 at the supplied pointer; all-idle uses bit31 at
pointer+12. They retain four-byte frames and the `void *` interface used by
the recovered suspend caller. The status return values and ordered memory
accesses are checked through the primitive call. Primitive ABI verification
and conservative caller-saved register clobbers support the composition;
this is not whole-device hardware qualification.

```sh
python3 g2/tools/verify_gx8002_npu_registers.py
python3 g2/tools/verify_gx8002_npu_control.py
python3 -m unittest discover -s g2/tests -p test_gx8002_npu_registers.py
python3 -m unittest discover -s g2/tests -p test_gx8002_npu_control.py
```

Current reports: `gx8002-npu-register-linked-candidate.json`,
`gx8002-npu-register-verification.json`, `gx8002-npu-control-linked-candidate.json`,
and `gx8002-npu-control-verification.json`. Earlier object-only reports are
historical evidence of the oversized portable attempt. The ISA manual hash
is recorded; text sections LSL, LSR and ROTL begin at lines8772,8991,11887.

All nine routines are integrated; all 417 integration tests pass. The codec
now has 152 C-accounted functions and five explicitly accounted assembly routines.
No whole-firmware or hardware qualification is implied.
