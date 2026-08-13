# CMSIS-FreeRTOS timer operations source-candidate audit

Status: production-integrated and dual-toolchain replayed  
Target: official G2 `s200_v2.2.6.10` Apollo-main application  
Scope: `osTimerStart`, `osTimerStop`, and `osTimerDelete`

## Result

Three more linked CMSIS-FreeRTOS timer wrappers are dependency-closed over
production source providers:

| Wrapper | Stock span | Bytes | SHA-256 | External callers |
|---|---|---:|---|---:|
| `osTimerStart` | `[0x00449498,0x004494D8)` | 64 | `db1c7749aa74828b87e3e52adb5aede0ec33854ae7a23f41becf56161727c71d` | 18 |
| `osTimerStop` | `[0x004494D8,0x00449522)` | 74 | `4aa92a7e2312a8f631872730fb5f653cf9d161ec48921258d0f52d82ccab8002` | 22 |
| `osTimerDelete` | `[0x0044953E,0x00449590)` | 82 | `ff0de25911fdae3e67d317f6db72bf1121d224a73d4599c63910b841bc31fef9` | 6 |

Together they cover 220 stock bytes and 46 external call sites. The selected
oracle is Arm CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`; its exact `cmsis_os2.c` blob was
first introduced by `13acfbef7be85119fc6bc56832c455d4547d92c7`.

## Dependency and behavior closure

- All three wrappers use source-owned private `IRQ_Context` and reject ISR
  context with `osErrorISR`.
- Start rejects null handles and zero periods, then submits FreeRTOS timer
  command 4 (`tmrCOMMAND_CHANGE_PERIOD`) with zero wait. Command failure maps
  to `osErrorResource`.
- Stop first calls the source-owned active-state provider, maps inactivity to
  `osErrorResource`, and submits command 3 (`tmrCOMMAND_STOP`). A command
  failure maps to generic `osError`, matching v10.5.1.
- Delete retrieves the callback context through the source-owned timer getter,
  submits command 5 (`tmrCOMMAND_DELETE`), and frees the untagged callback
  block only after successful deletion when bit zero marks dynamic allocation.
  Both timer command and heap-free providers are production source-owned.

No opaque fixed callee, TCB field, WSF seam, callback invocation, or timer
object-layout dereference is added by these wrappers. `osTimerNew` remains a
separate, larger constructor review because it owns the callback-record and
static-control-block layout decisions.

## Qualification

The source and host fixture are pinned at 3,795 bytes / SHA-256
`1a89eed70dc2fe894f4b96615b1b346e3e321199fd5d0318bb434c19fd90f443`
and 3,145 bytes / SHA-256
`17ac355249c2eb5b212e0a3505c2c2bf1ca27695e8138a8bea2f5f0156c14b7d`.
Host tests cover all validation, inactive, command-failure, callback-tag, and
free-after-success branches. Apple target sections are:

| Candidate | Bytes | Unrelocated SHA-256 | Relocations |
|---|---:|---|---:|
| `open_cfw_cmsis_timer_start` | 70 | `b02533265ea281d9aadba64ee44f85a29b07117988ecd7dc2126c488bff1a530` | 2 |
| `open_cfw_cmsis_timer_stop` | 78 | `8a1f722904cf138cf58da542aad91560e8105f7a7ace1f073754043175e8b226` | 3 |
| `open_cfw_cmsis_timer_delete` | 86 | `db4abb69f22056c19fc76d05c61bea417fad837095df8f260101901753ad6553` | 4 |

## Production boundary

All three complete stock entries now redirect to source. The overlay records
their source, Apache-2.0 license, upstream tag commit, source-producing commit,
stock hashes, relocations, and independent Apple/Linux linked placements. The
manifest accounts for the three source leaves plus two alignment regions.

| Toolchain | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple clang 21 | `132218` / `59e2a2aaed0515545eab80db53b352bd1f50b06876b551b3e29dbaaf5ef4fe36` | `3655614` / `16687c24bf48a394461752a8379cb58e22a7bdb488b0796279fcb551dfb4de47` | `4434108` / `4a21d9024780ea21ac13ca2b8e56dd99ad92b59cef3ce2154147114b45f8a0d4` |
| Homebrew clang 22.1.8 | `134086` / `4aecb0fa0462b57f0cd30a2a0acf010ea8a44b7e0f14d6fe365ec759810f7633` | `3657482` / `2d516c505067d9868602e9f162901b1ea131ca09342701dfdc275ace8dba8ec6` | `4435976` / `1105b43d10d965d0094e6a854479a65e10c7a69260b53f383342fde618ffe801` |

Both profiles were recorded once and then replayed through ordinary
fail-closed component and package builds. No signing, flashing, reset, boot,
or hardware operation was performed.

## Reproduction

```sh
make -C openCFW cmsis-freertos-timer-ops
```
