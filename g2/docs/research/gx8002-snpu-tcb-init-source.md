# GX8002 task descriptor initialization candidate

Stock package 0xee60 / runtime 0x102058d4 initializes ten records with a
144-byte stride. For each record it writes eight control/address pairs at
relative offsets 0x20/0x24 with a 12-byte stride. Controls are 0x10080+i;
addresses are the low 28 bits of state+record*144+0x2c+i*12. It then writes
0x10088 at relative0x80 and 0x4100ff at relative0x10. This is 180 writes.
The SDK snpu.o identifies the routine as snpu_tcb_init. The stock state base
is 0x20027350.

The candidate expresses the iteration, address arithmetic, and writes in C.
It compiles to 108 bytes against the original 124-byte envelope, but remains
UNQUALIFIED and UNREGISTERED. No whole-state ownership is claimed. In
particular, full descriptor control-word semantics still need investigation;
these recovered numeric values alone do not prove all data is understood.

Next: compare decoded original/candidate write traces and untouched words,
check 28-bit address truncation and loop boundaries, ABI preservation, literal
pool and envelope boundaries, and add mutation tests. Do not admit this based
only on compilation or linked size. Files use snpu_tcb_init / snpu-tcb-init.

## Target qualification

verify_gx8002_snpu_tcb_init.py rebuilds the candidate on macOS, authenticates
the stock image via the builder, and decodes both original and new code.
An independent sparse write model checks all 180 ordered stores in each of
67 full-width state/register patterns. It includes every untouched word in
the 0x5a0-byte record array and sixteen-byte guards on either side. Both
routines are leaf routines with unchanged SP and callee-saved registers.
The source is108 bytes in the original124-byte envelope.

Eight tests cover qualification counts, untouched memory, complete link
chains, wrong base opcode, address-mask corruption, loop count, out-of-range
stores and callee-save corruption. The fixed linked address does not exercise
all possible address-mask bits; no relocated-address generality is claimed.
The report qualifies this fixed shipped layout only. The offset-only external
view still does not claim ownership of complete driver state or model data.

Reviewed report: gx8002-snpu-tcb-init-verification.json. Both decoded traces
match the independent model. The initializer is now registered and integrated. All 542 native macOS
integration tests pass; package verification is recorded in the integration
build report and source-only goal checkpoint.
