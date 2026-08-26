# G2 product RTOS hooks and Ambiq HAL lineage recovery

Status: authenticated linked-object and provider-version closure;
production-routed from clean-room C. The G2 `2.2.6.10` object retained as
`product\s200\app\config\rtos.c` is completely bounded. Its CMSIS-FreeRTOS
and Apollo510 HAL seams are source-identified. No device or flash state was
changed.

## Result

The physical object is `[0x0046D67C,0x0046D8A0)`: 548 bytes, SHA-256
`49cb456135815b5738f5b0a9f96aca18a7a8e30a35846df4a3cbb6e0c714aa86`.
Thirteen functions account for 512 bytes and hash together to
`ce8de3e8b2dddc2c8b4d2c569faa6f376cfbe944f2ffb92769e770b45955fd33`.
Two pool/alignment intervals account for the remaining 36 bytes, SHA-256
`30c31ea87943083be2ccacf0e5d1b6faead2e94072b58f0cc9311dd290e8ddeb`.

Only the 88-byte `task_vote_init` body carries the retained path. Twelve
adjacent bodies are admitted by their shared 32-slot vote state, internal and
external calls, exact FreeRTOS hook ABI, Ambiq example ancestry, and retained
fatal strings. All thirteen were already recognized as functions by the
baseline Ghidra pass; none required recursive decoding.

Whole-image ingress is closed at 19 direct entry sites, 13 of them external,
and 24 in-image body calls, six internal and 18 external. There are no stored
function pointers, strict-interior BL decodes, or unmapped object targets. The
preceding LVGL font-manager tail/pool `[0x0046D584,0x0046D67C)` and following
list utility `[0x0046D8A0,0x0046D8E0)` are independently pinned outside the
object. The authoritative inventory is
`tools/manifests/g2-product-rtos-function-map.tsv`.

## Recovered behavior

The first-party portion is a 32-entry task-vote policy. Each eight-byte entry
holds a task handle and active byte. A 32-bit active count follows at offset
`0x100`, with an initialization byte at `0x104`; the complete state is cleared
as `0x108` bytes. The acquire/release paths save and disable PRIMASK, update
the selected slot and count, and restore interrupt state. Convenience wrappers
apply those operations to `osThreadGetId()`.

The application hooks are now closed rather than merely named seams:

- `am_freertos_sleep` feeds the watchdog, chooses deep sleep only when the
  active vote count is zero, otherwise requests normal sleep, and returns zero;
- `am_freertos_wakeup` feeds the watchdog after tickless wake;
- `vApplicationIdleHook` feeds the watchdog on each idle invocation;
- `vApplicationMallocFailedHook` logs and loops forever; and
- `vApplicationStackOverflowHook` logs the task name and repeatedly executes
  `BKPT`.

This confirms `configUSE_IDLE_HOOK=1`, `configUSE_TICK_HOOK=0`,
`configUSE_MALLOC_FAILED_HOOK=1`, and stack-overflow checking greater than one
(normally `2`), consistent with the broader FreeRTOS configuration audit.

## CMSIS-FreeRTOS and utility seams

The two current-task calls land on the already production source-owned
eight-byte `osThreadGetId` wrapper from ARM CMSIS-FreeRTOS v10.5.1, commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. Three critical-section calls
land on the already source-owned PRIMASK save/disable primitive at
`0x00473940`; restoration is emitted inline. Five diagnostic calls terminate
at admitted EasyLogger 2.2.99 seams. The sole `memset` call is the known IAR
DLIB family boundary and supplies no new discriminator beyond the EWARM 9.20+
floor and leading 9.60.2 archive candidate.

No CMSIS-FreeRTOS, EasyLogger, or IAR definition is embedded in this object.

## Apollo510 HAL version discriminator

The provider relationship identifies more than the previously recorded
"current HAL" family. The complete stock `am_hal_sysctrl_sleep` body is
`[0x0044AB42,0x0044B068)`: 1,318 bytes, SHA-256
`012c052f6ab7e829129ed966a94cfb1541605b2d05185115c1dfd06cbb9d2898`.
It contains two `WFI` instructions, at `0x0044ADF8` and `0x0044AF9A`.

Official Ambiq Apollo510 history provides a decisive alternative:

| SDK source | Public commit | `am_hal_sysctrl_sleep` | Assessment |
|---|---|---:|---|
| 5.0.0, `release_sdk5p0p0-5f68a8286b` | `392042e33b0db6c0241e5e49b2efa47bbb1fe871` | one `WFI` | excluded |
| 5.1.0, `release_sdk5p1p0-366b80e084` | `5efc0228528a8adce5eae0d226fac85d2551eb3b` | two `WFI` operations, adding internal-timer wake/re-entry | selected source-equivalent replay |

Thus stock uses the 5.1.0-lineage retry behavior, not the public 5.0.0
implementation. The selected public reproduction commit is the same official
5.1.0 commit already used by OpenCFW's authenticated Apollo510 source closure.
The source identities, Git blobs, SHA-256 values, and discriminator are in
`tools/manifests/ambiqsuite-apollo510-rtos-provider-source.tsv`.

The exact private generating commit is still not observable. The firmware's
embedded build time is `2025-04-28T13:29:15Z`, while the public 5.1.0 import is
dated 2025-08-14. Stock therefore used a private/pre-release 5.1.0-lineage
snapshot, and the public commit is a faithful source oracle rather than a
chronologically possible generating checkout.

The three watchdog feeds call the G2 wrapper at `0x004B29F8`, which selects
zero and reaches stock `am_hal_wdt_restart` at
`[0x0052A3DA,0x0052A3EE)`. That 20-byte leaf writes the Apollo510 restart key
`0xB2` and returns success. Its source is behaviorally identical in the 5.0.0
and 5.1.0 files, so it corroborates Ambiq origin but does not select a version.

## Limits and reproduction

The private producing commit remains unavailable, but it is no longer a
software dependency: `components/apollo_main/core_overlay/product_rtos.c`
implements all 13 entries. Thirteen guarded redirects replace all 512 stock
function bytes with 444 compiled bytes plus 14 alignment bytes and 19 strict
relocations. The 36-byte stock literal/alignment pool remains authenticated.
Host execution covers initialization, null and duplicate votes, slot
exhaustion/reactivation, exact IRQ save/restore pairing, current-task wrappers,
deep-versus-normal sleep selection, watchdog hooks, and both fatal paths.

The remaining gate is physical only. Apollo510 sleep-state, watchdog, tickless,
and fatal-hook behavior requires an authorized responsive G2 and trace/reset
evidence. That evidence is unavailable in this workspace, so physical
validation is explicitly blocked; no image was signed, flashed, or installed.

Run:

```sh
make product-rtos-closure
```

This authenticates the image, function/provider/source ledgers, adjacent
boundaries, source-owned CMSIS/IRQ seams, Ambiq HAL discriminator, focused
tests, and aggregate retained-path frontier.
