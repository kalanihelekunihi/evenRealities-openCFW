# G2 FreeRTOS task-name/mask production-readiness audit

Status: historical promotion audit; recommendation implemented in production
Scope: official G2 package `2.2.6.10`, Apollo-main application; offline
analysis and subsequent source/component/package validation only, with no
signing, flashing, serial, debugger, or hardware access

## Subsequent production status

The promotion ranking below is historical: the complete interrupt-mask pair
and `pcTaskGetName` are now production source.
The exact MIT-licensed FreeRTOS-Kernel V10.5.1 Clang-syntax adaptation
`runtime_freertos_interrupt_mask.S` has SHA-256
`28f16b37970b5529fe63cf250365b955b0c65fe2a016efda1ba718ee3b768de5`.
It installs byte-exact fixed copies at `[0x005FA0A4,0x005FA0BA)`
(`f6bd0708e653c8e8880e33e298f9dc8ede1305c9386ea4ca5ff554d4022dc323`)
and `[0x005FA0BA,0x005FA0C8)`
(`97532a7902b38e1551198dd647d0fcdc3a6f19315b6491058a813c7643e0028a`),
plus current Apple leaves at `[0x007AFF08,0x007AFF1E)` and
`[0x007AFF1E,0x007AFF2C)`, with Linux counterparts at
`[0x007B054C,0x007B0562)` and `[0x007B0562,0x007B0570)`. The promoted getter
is a 38-byte relocated leaf at `[0x007B0030,0x007B0056)` on Apple and
`[0x007B0650,0x007B0676)` on Linux, with Apple relocated SHA-256
`88edbdea558812d213013a8d319a09c63dafa86ec91a7640f427c72c77552da1`.
Its sole relocation binds directly to the source-owned set-mask leaf.

The complete generated getter-entry replacement hashes to
`bab8b15cc5c97baa2336a66e065fd3c653e116d106a278a0cae74e172f83c0ee`.
The original task-name promotion's overlay/provider/package pins were
114,562/3,637,958/4,416,140 bytes with SHA-256 values
`188a9b26fce7b7899e3c0eebd698552edc6a453396b9b05107841c63d488e8ee`,
`6830ed33f567b4ac8b4c401612b83b56caa38d107bb9b1fc5d210dce9add9214`,
and
`624e18cea8e36c954809f2d36b8b539275e7fa8ba9f305a166ed9e83b7a86d43`.
Its 554,360-byte flash plan had SHA-256
`4b1ce318c286cb7a0a83c144b149c61581ca658080c229bd7474cf84ed472b35`.

## Decision

The smallest safe atomic source promotion, now implemented, was:

1. `pcTaskGetName`;
2. `ulSetInterruptMask`.

`vClearInterruptMask` is not required in that same increment.
`pcTaskGetName` calls the set leaf only on its fatal `configASSERT` path,
discards the returned old mask, performs the configured invalid write, and
never returns. It has no restore call or normal-path interrupt-mask operation.

This result is narrower than promoting all three functions, but it does not
split an active save/restore transaction. The twelve existing
`vClearInterruptMask` callers belong to other routines. They can continue to
call the authenticated official leaf while the two-function increment is
introduced.

The optional broader increment remains sound: promote the complete 36-byte
mask pair alongside `pcTaskGetName`. That is useful for reducing retained
provider bytes, but it is not an atomicity requirement for the task-name
getter.

## Exact source boundaries

All three functions are unequivocal FreeRTOS-Kernel V10.5.1 source:

| Function | Official range | Bytes | SHA-256 |
|---|---|---:|---|
| `pcTaskGetName` | `[0x00454F16,0x00454F38)` | 34 | `a25ace28ece3ca37f11da7e73945acb28f1f99d906203613e9856d2070c07817` |
| `ulSetInterruptMask` | `[0x005FA0A4,0x005FA0BA)` | 22 | `f6bd0708e653c8e8880e33e298f9dc8ede1305c9386ea4ca5ff554d4022dc323` |
| `vClearInterruptMask` | `[0x005FA0BA,0x005FA0C8)` | 14 | `97532a7902b38e1551198dd647d0fcdc3a6f19315b6491058a813c7643e0028a` |

The task getter is the released `tasks.c` algorithm with recovered
`pxCurrentTCB` word `0x20074A20`, `pcTaskName` offset `+0x34`, and the G2
fail-stop assertion. Its only outgoing call is the `BL` at `0x00454F26` to
`0x005FA0A4`.

The set leaf returns the prior `BASEPRI` in `r0`, installs shifted mask
`0x30`, and executes DSB/ISB. The clear leaf accepts a saved mask in `r0`,
restores `BASEPRI`, and executes the same barriers. Neither leaf has a
literal, relocation, private state, or outgoing call.

The historical research-candidate files remain production-excluded; production
uses the reviewed files under `components/apollo_main/core_overlay`:

| Candidate | SHA-256 | Role |
|---|---|---|
| `research/candidates/freertos_pc_task_get_name.c` | `cd80886bfec8eb99df0a07ca721685f387a44c079c1da8139fa944e99ff8a278` | Released getter with fixed current-TCB seam and explicit set-leaf relocation |
| `research/candidates/freertos_interrupt_mask_pair.S` | `710a2b348df985a981a5c1f6829a849e1c3635b599549c7847df7151370ed2a6` | Clang-syntax MIT adaptation of the exact released Cortex-M55 pair |

The existing target tests prove that the assembly candidate emits the exact
36 official bytes under both Cortex-M55 and current overlay-compatible
profiles, with no undefined symbols, relocations, private data, or extra
code.

## Complete entry and caller topology

The installed application was scanned at every halfword for direct Thumb-2
`BL` and `B.W` encodings and narrow `B`, `Bcc`, `CBZ`, and `CBNZ`
encodings. Every byte offset was scanned for possible even or odd/Thumb entry
and interior address values.

| Function | Direct `BL` callers | Caller-address SHA-256 | `B.W` | External interior | Narrow entry/interior |
|---|---:|---|---:|---:|---:|
| `pcTaskGetName` | 1 | `6b6b656546449e21e970d725927d278f881d1c0bf448fd732bf3759f73366ee4` | 0 | 0 | 0 |
| `ulSetInterruptMask` | 181 | `f0187e62c4c399694d4fdd8e64a2e238724f6fb0ec89a6520c3020156eb9c106` | 0 | 0 | 0 |
| `vClearInterruptMask` | 12 | `5047082ba3888cae8330f9276620611cdf412c86fee71d1cd0ffc97447fd2746` | 0 | 0 | 0 |

The sole task-name caller remains the EasyLogger helper call at
`0x0044AAEE`.

The complete clear-leaf caller list is:

```text
0x0043C9F2  0x00441A38  0x00441B02  0x00441E5C
0x0044210E  0x0044212E  0x00449D96  0x00449E3C
0x00455F54  0x00456420  0x0047ED6E  0x0057E0E6
```

The machine-readable analyzer emits all 181 set-leaf callers. There is no
observed direct or stored callback/table entry for any of the three
functions.

## Classification of the `0x0062FCDF` data-window match

A byte-granular scan finds the four bytes `ba a0 5f 00` starting at
`0x0062FCDF`, which form the apparent little-endian value `0x005FA0BA`.
This is a sliding-window false positive, not a stored clear-leaf pointer.

The exact authenticated 16-byte context is:

```text
address       bytes
0x0062FCD8   e6 db 03 80 2f 30 1d ba a0 5f 00 01 df 40 1f b4
```

The apparent word begins at both an odd address and address-mod-four `3`. It
is assembled across these two naturally aligned data words:

| Aligned address | Actual little-endian word |
|---:|---:|
| `0x0062FCDC` | `0xBA1D302F` |
| `0x0062FCE0` | `0x01005FA0` |

In other words, the apparent pointer is the last byte of the first word plus
the first three bytes of the second word. Neither aligned word is the clear
entry or any mask-leaf interior address. The wider context is a packed
non-code data run, and decoding it linearly as Thumb produces incoherent
coprocessor and stack operations rather than a reachable function. The
complete scan finds no naturally aligned stored entry/interior word and no
wide or narrow branch into either mask-leaf interior.

The analogous `pcTaskGetName` byte-window candidate at `0x004A56B7` is
classified the same way by its existing audit: it overlaps aligned SRAM words
`0x2000454E` and `0x2000454F`.

## Exact production redirects

For the smallest safe increment:

1. redirect the complete stock `pcTaskGetName` span
   `[0x00454F16,0x00454F38)` to
   `open_cfw_freertos_pc_task_get_name`;
2. leave its sole existing caller at `0x0044AAEE` targeting the stock entry,
   so the entry redirect transfers control to the appended source function;
3. redirect only the complete set-leaf span
   `[0x005FA0A4,0x005FA0BA)` to the source-owned
   `ulSetInterruptMask`;
4. leave all 181 existing set-leaf call instructions unchanged;
5. resolve the source getter's `ulSetInterruptMask` relocation to that
   source-owned function;
6. retain the fixed `pxCurrentTCB` word at `0x20074A20`.

The strict address-preservation constraint is:

> Do not patch at or beyond `0x005FA0BA`.

The set-leaf redirect and any NOP fill must be contained entirely inside
`[0x005FA0A4,0x005FA0BA)`. The original
`vClearInterruptMask` entry must remain exactly at even address
`0x005FA0BA`, and its complete official bytes through `0x005FA0C8` must
remain authenticated. This preserves all twelve direct callers without
changing their save/restore protocols.

If the broader pair is promoted instead, the generated pair may own
`[0x005FA0A4,0x005FA0C8)`, but both independently callable public entries
must still be preserved: set at pair offset `0`, clear at pair offset `22`.
A single entry redirect at `0x005FA0A4` that moves or hides the clear entry is
not sufficient.

## Why the two-function increment is atomic

The decision depends on call semantics, not adjacency:

- valid `pcTaskGetName` inputs do not call either mask leaf;
- the NULL-after-handle-selection assertion calls only
  `ulSetInterruptMask`;
- that fatal path discards the old mask and cannot reach a restore;
- therefore no `pcTaskGetName` execution can cross from a source-owned set
  leaf into the official clear leaf;
- other routines that do save and restore retain both official entry
  addresses until their own boundaries are promoted.

Promoting the set leaf alone is also ABI-safe for existing callers because
the source candidate is byte-exact: it continues to return the old
`BASEPRI` in `r0`. Callers that later pass that value to the retained clear
leaf observe the same protocol.

## Focused validation

Run:

```sh
PYTHONDONTWRITEBYTECODE=1 \
  python3 tools/analyze_g2_freertos_task_name_mask_closure.py

PYTHONDONTWRITEBYTECODE=1 \
  python3 tools/analyze_g2_freertos_task_name_mask_closure.py --json

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  tests.test_analyze_g2_freertos_task_name_mask_closure
```

The analyzer authenticates the package/application, all three exact bodies,
the task getter's outgoing assertion call, every direct caller and caller
digest, absence of wide/narrow/interior references, both known byte-window
false positives, aligned context words, candidate provenance, exact
redirects, and address-preservation constraints.

Focused result:

```text
Ran 4 tests in 7.121s

OK
```

This audit itself originally changed no production artifact. Its recommendation
has since been implemented and is pinned by the 7/7 production suite in
`tests/test_runtime_freertos_pc_task_get_name.py`.
