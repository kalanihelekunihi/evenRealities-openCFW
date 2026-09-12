# G2 display-state and string-helper closure

Status date: 2026-09-11
Scope: reviewed clean-room C for the 11 retained trailing functions in
`0x0048D540..0x0048D558` and `0x0048D558..0x0048D866` (Apollo main
application, component `apollo_main`), work item AM-040
Mode: reviewed source, host differential tests, freestanding
target-profile compile check; no flashing, signing, or hardware
operation

## Result

11 functions (766 spans bytes: 762 function bytes plus the 4-byte
strtoul table-delta literal) are recovered as reviewed MIT C in
`components/apollo_main/core_overlay/runtime_string_helpers.c`
(strcpy, strtoul) and
`components/apollo_main/core_overlay/runtime_peripheral_state_helpers.c`
(the nine-function state cluster):

| Stock span | Bytes | Port symbol | Identity |
| --- | ---: | --- | --- |
| `0x0048D540..0x0048D558` | 24 | `open_cfw_libc_strcpy` | strcpy (NUL-inclusive byte loop, returns dst) |
| `0x0048D558..0x0048D570` | 16 | `open_cfw_state_init_params` | 3-word init: 0x20071E30, 0x2005F154, 0x400 |
| `0x0048D570..0x0048D588` | 24 | `open_cfw_state_nibble_to_mode` | nibble map: 1-2->4, 6->0, else 7 |
| `0x0048D588..0x0048D620` | 152 | `open_cfw_state_mode_switch` | register-state transition driver |
| `0x0048D620..0x0048D654` | 52 | `open_cfw_state_flag_get` | dirty/nibble/sign/bit30 flag getter |
| `0x0048D654..0x0048D670` | 28 | `open_cfw_state_sample_vote` | triple-sample vote (2nd if first two agree) |
| `0x0048D670..0x0048D6DC` | 108 | `open_cfw_state_sample_retry` | retry loop with IRQ guard |
| `0x0048D6DC..0x0048D6E6` | 10 | `open_cfw_state_flag_or` | mask register OR-set |
| `0x0048D6E6..0x0048D6F0` | 10 | `open_cfw_state_latch_store` | latch store, value fetch |
| `0x0048D6F0..0x0048D704` | 20 | `open_cfw_state_value_get` | masked value get (uxtb selector) |
| `0x0048D724..0x0048D866` | 322 | `open_cfw_libc_strtoul` | strtoul over locale hooks + SRAM table |

No upstream family is claimed for any of the eleven. The string pair
is libc-shaped (IAR DLib census confirmation belongs to the iar-dlib
family work); the state nine are a first-party peripheral-state
cluster whose exact peripheral block stays open (register block rooted
at 0x40008800, SRAM state at 0x20074F7A/0x20000318, driven from the
0x004563xx driver through the still-stock channel setters
0x004C44BC/0x004C4530).

## Identity method

Every port was written from the stock instruction stream decoded with
capstone on macOS, not from Ghidra RMI decompilation alone:

- strtoul: Ghidra renders the table computation as
  `iVar2 + 0x48d804` / `(char)iVar4 + 0x28`, hiding a PC-relative
  delta. The disassembly shows `ldr r6,[pc]` loading 0x00263A2C from
  0x0048D7DC, `add r6,pc`, `adds r6,#0x14`: T = 0x006F1208, the C
  library digit table in shared SRAM. The digit is
  `(found - lowbyte(T+0x28)) & 0xFF`, which equals the memchr index
  because the firmware table satisfies (T+0x28)&0xFF == 0x30; the port
  reproduces this exact computation. Threshold byte is `T[base]`;
  overflow follows the stock extra/tie-break/rsb-negate structure.
  Ghidra's two "ranges" for this function exclude the 4-byte delta
  literal, but the recorded body hash covers the full 322-byte span.
- Mode switch: transition matrix on bits 0xC0000000, channel calls
  with `(mode&0xFF, 0x32)`, full-word register store, `strb` dirty
  byte, previous-word return; the asymmetric pop passes the untouched
  fourth argument back in r1, which both known callers discard.
- Retry loop: the tail word 0xF3808810 hand-decodes to
  `msr primask, r0` (MSR-with-Rn=r0, SYSm=PRIMASK), i.e. restore of
  the stashed IRQ state — not a bare enable. `lsls r0,r7,#0` then
  returns the status word (0 ok, 5 bad lane, 0x8000000 clamped).
- The first vote precedes the lane-range check, so even bad lanes
  consume one sample triple (pinned by test).
- The flag getter's `lsrs#31` negative check and `((reg>>30)&1)^1`
  result, and the value getter's `uxtb` selector narrowing, are
  reproduced exactly.

## What remains

- The locale/digit-table contents (0x006F1208), the channel setters,
  the sample/IRQ providers, and the errno cell stay retained stock
  callees referenced by absolute address (the admitted pattern for
  retained providers); their reconstruction belongs to their own
  items.
- The holder words at 0x0048D704..0x0048D720, the grid literal pool
  at 0x0048D3A0..0x0048D3C8, and three 2-byte pads stay retained data.
- The peripheral block identity (which driver owns 0x40008800+) is
  still open; behavior of these eleven does not depend on it.
- Overlay routing of all 64 AM-040 leaves is a separate step in the
  integrate script; flash-plan bytes stay `official_blob` until it
  lands.

Hardware qualification stays blocked by unavailable physical evidence;
no flashing, DFU, MMIO probing, signing, or publishing was performed.

## Verification performed

- `python3 -m unittest g2.tests.test_runtime_str_state_helpers` — 16
  tests pass on macOS: stock-body SHA-256 pins for all eleven spans,
  strcpy, strtoul decimal/sign/base-detect/invalid/empty/overflow/max
  (incl. uppercase hex via the case-folding class model and NULL
  out-params), param init words, the full nibble map, mode-switch
  transition matrix with channel-call pins, flag-getter branches,
  vote agree/disagree, retry spin/clamp/store/IRQ-restore order, and
  flag/latch/masked-get incl. the uxtb edge.
- Freestanding target-profile syntax check passes for both new
  translation units (same flags as the LVGL tranche).
- Two test-authoring errors found during development are recorded
  here, not hidden: the flag-getter bit30 expectations were initially
  inverted (stock returns bit30^1), and the bad-lane retry case
  initially pushed no samples (stock votes before the range check).

## Gap-data accounting 2026-09-12 (AM-040)

Every non-function byte of `0x0048C7B4..0x0048D866` (172 B) is now
identified: 86 B strlen leaf (another item, already routed), 6 B
`00 00` alignment pads (`0x48CA3A`, `0x48D4E6`, `0x48D53E`), the 40 B
grid literal pool (fully decoded in `lvgl-grid-engine-closure.md`;
8/10 words constant-folded, 2 format words pending per that audit),
the 8 B param pool at `0x48D568` (both words folded as
`OPEN_CFW_STATE_PARAM_FIRST`/`SECOND`; the third param is the `0x400`
immediate), and the 32 B holder table at `0x48D704` (word map in the
header comment of `runtime_peripheral_state_helpers.c`: MMIO
`0x40008800`/`20` + `0x40008900`/`04`/`08`, SRAM `0x20074F7A` /
`0x20000318`).

Live dependency: production state leaves dereference the
flash-resident holders fresh on every call
(`OPEN_CFW_STATE_HOLDER_WORD` over `0x0048D704..0x0048D720`), so 8
words of stock flash remain runtime inputs to routed leaves.
Follow-up: author a source-owned const table with a derivation note,
repoint the `HOLDER_*` defines, extend
`integrate_g2_apollo_am040_overlay.py` `prepare()` to map the data
symbol (it currently rejects defined non-function relocations), and
re-promote the nine state leaves once the LC3 LLD drift resolves.

Transparent note: `transparent-test` is 39/42 on the live tree; the
3 failures are committed-code drift between
`test_report_transparent_coverage_release_gate.py` and
`report_transparent_coverage.py` (another lane, untouched here).
