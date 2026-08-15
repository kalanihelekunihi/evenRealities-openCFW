# Software-TWI reduction correlation (owner-authorized, 2026-08)

## Decision

Under the "Owner-authorized full reduction (2026-08-14)" section of
[`../SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md), the forty-function family
`unknown_software_twi_provider_candidate` is reduced from the recovered
disassembly evidence to compilable C at
[`../../reconstructed/software_twi/`](../../reconstructed/software_twi/).  The
reconstruction is not vendor source and is never presented as such; every
file carries the provenance banner.  The ledger disposition for the forty
entries becomes `clean_room_reimplementation_owner_authorized` when the
integrator wave re-pins the ledger and verifier.  The boundary doc
[`../boundaries/SOFTWARE-TWI-PROVIDER-BOUNDARY.md`](../boundaries/SOFTWARE-TWI-PROVIDER-BOUNDARY.md)
and the 2026-08 attribution re-examination
[`../boundaries/unknown_software_twi_provider_candidate-ATTRIBUTION-2026-08.md`](../boundaries/unknown_software_twi_provider_candidate-ATTRIBUTION-2026-08.md)
remain the provenance record of why no upstream source could be admitted.

Stock image: application, load base `0x00027000`, SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

## Evidence extraction path

- The engine region `0x000552DC..0x000562DF` is absent from the Ghidra
  corpus (all forty ledger rows are `manual_provenance_supplement`).  Every
  body was disassembled from the byte-exact rebuilt image
  (`research/decompilation/rebuild/rebuilt-application.bin`) with GNU
  `arm-none-eabi-objdump` (binutils 2.34, `-M force-thumb`) during this
  reduction; the read-byte/start/stop/wait-ACK/write-byte roles were
  verified byte-identical across the four bus copies.
- Literal pools: each open/adapter body loads its fixed per-bus record
  (`0x20007400`/`0x20007470`/`0x200074E0`/`0x20007550`, stride `0x70`) from
  the literal word immediately past its end (outside the pinned extents).
- Callee attribution: all transaction/primitive callees are the family's own
  per-bus copies (the cross-instance folding noted by the census — i2c_2's
  write adapter calls the `0x0005613E` copy, i2c_3's calls `0x000561A0`,
  i2c_5's single-byte path tail-calls `0x000560DC` — is behaviorally
  transparent because the primitive copies are byte-identical and take the
  engine pointer as an argument).  The only external callee is the i2c_4
  open's `0x00078EE6`, a Nordic `nrf_gpio_cfg`-shaped six-argument wrapper
  (builds the PIN_CNF word `dir | input<<1 | pull<<2 | drive<<8 | sense<<16`
  and stores it at `base + 0x700 + pin*4`; `functions.csv` lists it as
  `FUN_00078ee6`, unattributed).
- The runtime vtable installer that writes the six GPIO/delay operations
  into the records is not flash-reachable from any family entry (verified by
  the census's exhaustive pointer scan); it is reached indirectly through
  the still-blocked generic registry.  Consequently the operation pointers
  and the `set_input` pull operand are runtime-installed values, not
  flash-recoverable constants; the reconstruction binds them explicitly.

## Recovered layout

Per-bus record (stock `0x20007400 + n*0x70`): `+0x00` device-name pointer
(installed at runtime from the `i2c_2`..`i2c_5` string table), `+0x04` open
flag byte, `+0x08` engine state, `+0x30` close-path pin-release op (owned by
the separately admitted R1 close wrappers), `+0x34` generic-registry
sub-record (blocked family; opaque here).  Engine state (`record + 0x08`):
`+0x00` delay context (udelay operand), `+0x04` SCL pin, `+0x08` SDA pin,
`+0x0C` drive-low(pin), `+0x10` release-high(pin), `+0x14` set-output(pin),
`+0x18` set-input(pin, pull), `+0x1C` pull operand byte, `+0x20` udelay(ctx),
`+0x24` read-pin(pin).  The reconstruction static-asserts these offsets for
the 32-bit target ABI.

Recovered board bindings: `i2c_2` SCL P1.13 / SDA P0.28 / delay 1, `i2c_3`
SCL P0.11 / SDA P0.12 / delay 5, `i2c_4` SCL P1.09 / SDA P0.31 / delay 1,
`i2c_5` SCL P1.14 / SDA P1.11 / delay 1 (boundary-doc table; pins are stored
as absolute nRF52840 GPIO numbers, P1.n = 32 + n).

Request blocks: read `+0x00` u8 address, `+0x02` register (u8 on i2c_2/3,
u16 on i2c_4/5), `+0x0C` buffer pointer, `+0x10` length (u8 on i2c_2/3/5,
u16 on i2c_4); write `+0x00` u8 address, `+0x02` register (u8 on i2c_2/3,
u16 on i2c_5, ignored on i2c_4), `+0x04` const buffer pointer, `+0x08` u16
length.  Narrow fields read only the low byte(s); the reconstruction models
the blocks with 16-bit fields and truncates exactly where stock truncates.

## Per-function contract and reconstruction decisions

| Stock extent | Bytes | Reconstructed symbol | Contract |
| --- | ---: | --- | --- |
| `0x00055330..<0x0005535C` | 44 | `software_twi_i2c_2_open` | idempotent via open flag; set_output(SCL/SDA), release_high(SCL/SDA), set flag, return 0 |
| `0x00055360..<0x0005538C` | 44 | `software_twi_i2c_3_open` | byte-identical body, own record |
| `0x00055390..<0x000553DE` | 78 | `software_twi_i2c_4_open` | shared sequence plus two gpio-configure calls `(pin, 1, 1, 0, 0, 0)` (SCL then SDA) before the flag store |
| `0x000553E4..<0x00055410` | 44 | `software_twi_i2c_5_open` | byte-identical body, own record |
| `0x0005547C..<0x000554AA` | 46 | `software_twi_i2c_2_read` | NULL request 4; not open 10; u8 register/count; transaction failure 12 |
| `0x000554B0..<0x000554DE` | 46 | `software_twi_i2c_3_read` | same shape, own record |
| `0x000554E4..<0x00055512` | 46 | `software_twi_i2c_4_read` | u16 register/count |
| `0x00055518..<0x00055542` | 42 | `software_twi_i2c_5_read` | u16 register, u8 count; merges NULL-request and not-open into 4 |
| `0x00055548..<0x000555F4` (+3 copies) | 172×4 | `software_twi_read_byte` | MSB-first sample; ACK (drive SDA low) or NACK (leave released) trailing pulse selected by flag; both tails converge on release_high(SDA) |
| `0x000557F8..<0x00055878` | 128 | `software_twi_read_transaction_reg8` | start / addr(W) / reg8 / repeated-start / addr\|1 / count-1 ACKed bytes + 1 NACKed byte / stop; NACK aborts with 11, no stop; count 0 still reads one byte |
| `0x00055878..<0x000558F8` | 128 | `software_twi_read_transaction_reg8` | second copy (i2c_3) |
| `0x000558F8..<0x00055988` | 144 | `software_twi_read_transaction_reg16` | reg16 MSB-first; u16 count (i2c_4) |
| `0x00055988..<0x00055A18` | 144 | `software_twi_read_transaction_reg16` | reg16; u8 count (i2c_5) |
| `0x00055A18..<0x00055A56` (+3 copies) | 62×4 | `software_twi_start` | set_output both, release both, udelay, SDA low, udelay, SCL low, udelay |
| `0x00055B10..<0x00055B3C` (+3 copies) | 44×4 | `software_twi_stop` | set_output both, SDA low, release SCL, udelay, release SDA |
| `0x00055BC0..<0x00055C08` (+3 copies) | 72×4 | `software_twi_wait_ack` | release SDA, set_input(SDA, pull), udelay, release SCL, udelay, sample; drive SCL low, set_output SDA, udelay; returns 1 on NACK (error polarity) |
| `0x00055DBC..<0x00055E3C` | 128 | `software_twi_i2c_2_write` | NULL 4; not open 8; length 1 → inline addr+reg8+data path; else multi-byte with u8-truncated count; failure 11 |
| `0x00055E40..<0x00055EC0` | 128 | `software_twi_i2c_3_write` | same shape, own record |
| `0x00055EC4..<0x00055F58` | 148 | `software_twi_i2c_4_write` | no register byte: addr + 1 data byte, or addr + N data bytes (u16 length loop) |
| `0x00055F5C..<0x00055F9E` | 66 | `software_twi_i2c_5_write` | length 1 → tail-call reg16 single-byte transaction; else reg16 multi-byte with u8 count |
| `0x00055FA4..<0x00055FF2` (+3 copies) | 78×4 | `software_twi_write_byte` | MSB-first; per bit drive/release SDA, udelay, release SCL, udelay, drive SCL low; releases SDA after bit 7 (in-loop ACK-window prep) |
| `0x000560DC..<0x0005613E` | 98 | `software_twi_write_transaction_reg16_byte` | start / addr(W) / reg16 MSB-first / one byte / stop; 11 on any NACK |
| `0x0005613E..<0x000561A0` | 98 | `software_twi_write_transaction_reg8` | start / addr(W) / reg8 / N bytes / stop; 11 on any NACK; count 0 writes no data |
| `0x000561A0..<0x00056202` | 98 | `software_twi_write_transaction_reg8` | second copy |
| `0x00056202..<0x00056274` | 114 | `software_twi_write_transaction_reg16` | reg16 MSB-first + N bytes |

The four close/shutdown wrappers at `0x000551E8..0x00055280` and the four
bus-binding wrappers at `0x00056508..0x00056562` remain outside this family
(admitted R1 adapters / R1 board configuration) and are not reconstructed
here.

## Divergences from the stock binary (all deliberate)

1. **Byte-identical copies folded.**  The four read-byte / start / stop /
   wait-ACK / write-byte copies are byte-identical generic bodies (the
   engine pointer is an argument), and the stock link itself folds calls
   across instances (i2c_2's write adapter calls the `0x0005613E` copy,
   i2c_3's calls `0x000561A0`, i2c_5's single-byte path tail-calls
   `0x000560DC`).  The reconstruction keeps one generic body per role;
   observably identical on every stock-reachable state.
2. **Explicit provider bindings.**  Stock calls the six GPIO/delay
   operations through runtime-installed record slots and calls the
   `0x00078EE6` gpio wrapper directly.  The reconstruction binds all of them
   through `software_twi_initialize` / `software_twi_providers`; an unbound
   mandatory provider returns the family's recovered bad-argument code 4
   from status-returning entries (`open`, transactions, adapters), returns
   the error polarity (1 = NACK) from `software_twi_wait_ack`, and no-ops
   the void cores (`start`, `stop`, `write_byte`) and zeroes
   `read_byte` — stock would fault on the NULL slot.
3. **Bad-argument handling.**  Stock dereferences the request buffer
   unchecked; the reconstruction returns 4 for a NULL buffer that would be
   dereferenced (a zero-count multi-byte write never touches the buffer in
   stock and still succeeds here).
4. **Loop-counter widths.**  Stock truncates the read/write loop counters to
   8 or 16 bits per bus copy; given the recovered count widths (u8, or u16
   on i2c_4) the truncation is unobservable, so the reconstruction uses full
   counters with the counts pre-truncated at the adapter boundary.  The
   signed `blt` comparison against the 32-bit `count - 1` in the read
   transactions is preserved exactly, including the count-0 wrap that still
   reads one NACKed byte.
5. **No libc in the freestanding unit.**  The module uses no `string.h`;
   record zeroing is a local loop, matching the r1 freestanding convention.

Preserved exactly: the status scheme {0, 4, 8, 10, 11, 12} including the
i2c_5 read adapter's merged 4; the operation order and udelay placement of
every primitive (start has three udelays, stop one, wait-ACK three,
write-byte three per bit, read-byte 21 total); the NACK error polarity of
wait-ACK; NACK aborts returning 11 without a STOP; the in-loop SDA release
after write-byte bit 7; the shared release_high(SDA) tail of read-byte;
16-bit register bytes MSB-first; per-bus request field widths and
truncations; the i2c_4 open's fixed `(pin, 1, 1, 0, 0, 0)` gpio-configure
arguments; and the recovered pin/delay board bindings.

## Host test mapping (`tests/test_reconstructed_software_twi.c`)

- `test_open`: recovered open op sequence per bus, idempotence, the i2c_4
  gpio-configure calls and arguments, record/pin/delay installation,
  accessor bounds.
- `test_open_unbound`: explicit failure (code 4) with no providers, with
  only gpio-configure missing, and with a single GPIO op missing.
- `test_start_stop`: exact op sequences including udelay placement and the
  per-bus delay context (1 vs 5); unbound no-op.
- `test_wait_ack`: ACK/NACK polarity, exact op sequence including the pull
  operand, unbound error polarity.
- `test_write_byte`: wire-decoded bit patterns for 0xA5/0x00/0xFF, per-bit
  op counts, the bit-7 SDA release, NULL engine.
- `test_read_byte`: sampled-byte recovery, ACK vs NACK trailing drives, the
  exact shared tail, udelay count, NULL engine.
- `test_read_transaction`: happy-path byte recovery and wire bytes
  (including repeated start and addr|1), NACK aborts at address and
  register with no STOP, the count-0 single-byte quirk, count-1, the
  16-bit register form, bad arguments.
- `test_write_transactions`: all three transaction forms on the wire, NACK
  positions (the NACKed byte is already driven), zero-count behavior, bad
  arguments.
- `test_read_adapters`: codes 4/10/12, the i2c_5 merged 4, register/count
  truncation per bus, NULL buffer, ignored dispatch arguments.
- `test_write_adapters`: codes 4/8/11, single-byte vs multi-byte paths, the
  length-0x101 count truncation, the i2c_4 no-register-byte flow, the i2c_5
  reg16 forms.

## Integration state

The module compiles under the r1 strict host flags and the freestanding
Cortex-M4 object flags (see the correlation banner in the sources); the
integrator wave wires `reconstructed/software_twi/software_twi.c` into
`SOURCES`, the test file into the runner, and re-pins the ledger/verifier
sites listed below.  On target nothing references the module yet: the stock
consumers arrive through the still-blocked generic registry, and the
runtime vtable installer (which would supply the Nordic-GPIO operation
bodies and the pull operand) belongs to that wave.  The boundary doc's
clean-room routing decision stands: OpenR1 prefers Nordic hardware TWIM
where electrically validated; this reconstruction exists so the recovered
behavior is compilable, testable, and diffable against owned hardware.  No
raw wire sender beyond the recovered per-bus interface is exposed, and no
close/shutdown path is recreated (that belongs to the admitted R1 close
adapters).

Known verifier/ledger pin sites for the integrator wave (this reduction
does not touch them):

- `tools/verify_openr1.py` (~line 9486): asserts all forty rows keep
  `source_disposition=investigate_before_implementing` and the census
  metadata keeps `local_implementation_authorized: False` — must be re-pinned
  to the owner-authorized disposition when the ledger flips.
- `tools/verify_openr1.py` (~line 3286): provider count of 40 for
  `unknown_software_twi_provider_candidate`.
- `tools/verify_openr1.py` (~line 2609): boundary-doc marker requirements
  (`implementation-blocked`, `no live GPIO or I2C sender`, ...).
- `tools/evidence/summarize_r1_software_twi_engines.py`: the immutable
  forty-function / 3,524-byte census with per-extent SHA-256 pins — these
  continue to pin the stock bytes and need no change for the reconstruction
  itself.
