# CMSIS-FreeRTOS thread-flags source audit

Status: production source-owned; Apple and Linux profiles replayed  
Target: official G2 `s200_v2.2.6.10` Apollo application

## Result

The complete linked thread-flags dependency chain is now source-owned. Three
FreeRTOS-Kernel V10.5.1 notification routines and the two linked
CMSIS-FreeRTOS v10.5.1 wrappers replace their complete callable stock spans.
No inferred function interior, proprietary source, hardware access, or widened
flash-address claim is involved.

| Stock operation | Physical span | Bytes | SHA-256 |
|---|---:|---:|---|
| `xTaskGenericNotifyWait` | `[0x00455B84,0x00455C48)` | 196 | `3d55447f2a7a719bbc1752d7d1b07f19fee401f320ae4b61055cbec427515cc9` |
| `xTaskGenericNotify` | `[0x00455C48,0x00455DB8)` | 368 | `fbcc2f27349099a2dc37ef103fc959730f14c6e0ef387507cbcba22fd3fc0a63` |
| `xTaskGenericNotifyFromISR` | `[0x00455DC0,0x00455F5C)` | 412 | `53aaaae75cd8808438e70404f910072b52eb627d457b8eeda8961f1f4241c8e5` |
| `osThreadFlagsSet` | `[0x00449238,0x004492C2)` | 138 | `c9e8658cde4a293b9d193cc15a854564445a8f399ad838450ef48c12eb9b6e11` |
| `osThreadFlagsWait` | `[0x004492C2,0x00449376)` | 180 | `be6894be51ea1a3131610342eb0806c96d2ddc298e5642481d207263de96c4fe` |

The first FreeRTOS span contains 172 executable bytes followed by a 24-byte
literal pool; that pool is independently pinned to SHA-256
`1ec96cd94786c5816bd0b914c7711edba0a4e4100bd081d8ead515d32d0f6ba1`.
The eight bytes at `[0x00455DB8,0x00455DC0)` are retained stock
alignment/literal data rather than assigned to either adjacent function.
`xTaskGenericNotifyFromISR` ends at `0x00455F5C`; the separate
notification-state-clear leaf begins at `0x00455F5E`, and private
`prvAddCurrentTaskToDelayedList` does not begin until `0x00455FA8`.

## Dependency origin and generating commits

The kernel algorithms come from the authenticated FreeRTOS-Kernel tag
`V10.5.1`, peeled commit
`def7d2df2b0506d3d249334974f51e427c17a41c`, tree
`7496dfa815c3cea2f45a090c6e92d113f494b930`. The vendored `tasks.c` is
223,695 bytes with SHA-256
`14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463`.
The adaptations preserve the separately reconstructed 112-byte G2 TCB patch:
notification value/state remain at `+0x68/+0x6C`, priority at `+0x2C`, and the
state/event list items at `+0x04/+0x18`. The vendor patch's original private
commit and field name remain unobservable and are not attributed upstream.

The wrappers come from Arm CMSIS-FreeRTOS tag `v10.5.1`, annotated tag object
`34e6e4c403c17de35ec0acf29610e374dc938604`, peeled commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`, tree
`d3689a816acc77a3f0b7d35439d666ad8434b6ba`. Its exact 70,106-byte
`cmsis_os2.c` blob is `88dca1d881f1a960872572a8a0efd94cde19dcea`
(SHA-256 `8a0d60b56ad30c4f7957f64fa581158017b6812ec94b832d974c773ae4f2bc36`)
and was first introduced by commit
`13acfbef7be85119fc6bc56832c455d4547d92c7`. Reconstruction uses the tagged
commit because it also pins the package/header closure and declared CMSIS_5
5.9.0 dependency; `13acfbef…` is the narrower source-producing commit.

This remains a maintained-source pin, not proof that Even used that exact
checkout. Stock behavior requires the earlier `600ba38a…` wrapper changes but
lacks the re-notification repair introduced by
`bb8a350a84567e5a000020abfbd6ab45ea9f6b46`. The admitted wait wrapper
therefore deliberately preserves the pre-`bb8a350a` loop. Source-identical and
dead-code-only intervening history prevents a unique historical checkout
claim.

## Recovered behavior

`xTaskGenericNotify` and its ISR variant implement all five V10.5.1 actions:
no action, set bits, increment, overwrite, and no-overwrite. Both return the
previous value when requested and move a notification-waiting task to the
ready list. The task variant resets the next unblock time and yields for a
higher-priority task. The ISR variant instead uses the recovered interrupt
mask pair, inserts into the pending-ready list while the scheduler is
suspended, sets both the caller wake flag and `xYieldPending` for a higher
priority task, and never yields directly.

`xTaskGenericNotifyWait` preserves entry/exit bit clearing, notification-state
transitions, zero-timeout behavior, delayed-list placement, and the two
critical sections. `osThreadFlagsSet` uses two notify calls so its return value
is the post-set flag word and pends PendSV only when the ISR wake flag is set.
`osThreadFlagsWait` preserves ISR/parameter/resource/timeout statuses,
wait-any/wait-all, no-clear, elapsed-tick recomputation, and—importantly—the
absence of the later re-notification repair.

Hosted tests exercise every notify action, prior-value queries, received and
timed-out waits, simulated delayed wakeup, ready/pending-ready routing,
priority wakeups, ISR mask/validation behavior, CMSIS status mapping, PendSV,
and the legacy no-repair discriminator. The production test also pins every
source byte, stock span, relocation, placement, component, and package root.

## Production roots

| Profile | Overlay | Component | Package |
|---|---|---|---|
| Apple Clang 21 | 137,090 / `e64b90905ea80f06a381d27f314578e416d920ae6b0a814af6a13c16823467bb` | 3,660,486 / `9185ee131fcd2a40f6a3742cce0689b75a6c362e7a6f871ecf136f9125f99087` | 4,438,980 / `807f1bec20e8b45e5469a0ca83ca2178ce1d2877f44fccfeb226f5adc7bad069` |
| Linux Clang 22.1.8 | 138,970 / `af5e5cf9e4923ce2bcfc166e38a8fb321c1acf9596477cd8bca8e188e298c460` | 3,662,366 / `7575d99910e63a7e31f819c86c62b19e15bc1870e1515a73bd94cc34f30506a5` | 4,440,860 / `a062556a2c152fe6bebb82e5202b1230d91cb84bc0921ef7d4b53b72a8558385` |

The Apple component now accounts for 137,272 source-owned bytes, 97,410
generated patch-site bytes, 32 wrapper bytes, 182 source-owned in-place bytes,
and 3,425,772 opaque base bytes. This tranche adds 1,026 source bytes while
removing 1,294 complete stock bytes from opaque accounting.

CMSIS production ownership is now 35/38 linked public APIs and all 5/5 private
helpers. The only linked public wrappers still backed by stock bytes are
`osKernelInitialize`, `osKernelStart`, and `osThreadNew`.
