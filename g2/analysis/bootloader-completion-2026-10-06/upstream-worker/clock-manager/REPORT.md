# Clock dispatchers and recovered providers 0 through 6

## Result

`clock_manager.c` reconstructs the stock `clock_request` and `clock_release`
dispatchers and class-0 bookkeeping provider. `clock_class_providers.c`
reconstructs classes 1 and 3, their user-bit operations, and the directly
called `0x0041d92c` register-update helper. `clock_class_provider4.c`
reconstructs class 4, its callback wait/cleanup and register leaves, and the
source `delay_us` conversion. `clock_class_provider2.c` reconstructs class 2,
its mode sampler, every mode-apply selector, and callback
finalization. `clock_class_provider5.c` reconstructs class-5 ownership,
callback, clkgen, and dual-switch paths. `clock_class_provider6.c`
reconstructs class-6 ownership and its PLL handle/configure/enable/disable/
lock path.

Incremental `make OUT=out/repro test` passes **128 source-versus-image cases**
and reaches **4,588 distinct stock instruction bytes**. The class-5 fixtures cover nested
class-2/3 requests, config failure, dual-switch ready and timeout polls,
callback completion, and final teardown. Class-6 fixtures cover nested
class-2/3 requests, valid and invalid PLL config, enable rejection, lock
success/timeout, existing ownership, and last-user teardown. All providers
execute as original instructions and compiled source; no provider entry is
intercepted.

Reproduce with `make OUT=out/repro test` from this directory. This builds in a
separate output directory without removing prior evidence. Source and image
hashes, raw instruction trace, and per-case state are in
`out/repro/comparison.json`. The reference image SHA-256 is
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

The shared mode-apply routine preserves its four-register ABI and 64-bit
`CONCAT44(local_10, status)` result: R0 carries status and R1 carries the local
value. Direct tests reach all 88 bytes of stock `0x41d3e4..0x41d43c`, including
selector 5 nested request success/failure, accepted/rejected values, selector
6 release, and invalid-selector result preservation. Additional class-5/6
cases cover zero-timeout callback cleanup, full-width clkgen config masking,
PLL divider bounds, and revision-gated power initialization.

## Dispatch and bitmap contract

Both dispatcher entries truncate clock ID and user ID to 8 bits. After
truncation, user IDs 0–56 and clock IDs 0–6 are valid; invalid user or class
returns status 6. The C dispatch API accepts raw `uint32_t` register values so
the compiler emits the required low-byte truncation even when high register
bits are nonzero.

The bitmap base is `0x20026e74`, read from literal `0x00422210`. It contains
seven 8-byte class rows, each with two 32-bit words. User IDs 0–31 occupy the
first word, IDs 32–56 occupy bits 0–24 of the second. This is an ownership bit
per class and user, not a multiplicity counter. Updates disable interrupts
with `critical_save` and restore the saved PRIMASK. Duplicate request and
absent release paths return without entering the critical section.

| Class | Request | Release | Behavior reconstructed |
|---:|---:|---:|---|
| 0 | `0x00421a30` | `0x00421a62` | Bitmap only |
| 1 | `0x00421a94` | `0x00421ad6` | Enable-word-gated bitmap request; bitmap-only release |
| 2 | `0x00421bd2` | `0x00421cce` | Reconstructed and differentially executed |
| 3 | `0x00421b08` | `0x00421b5c` | Enable-word gate, class-3 bitmap, register-15 update on first/last user |
| 4 | `0x00421d5e` | `0x00421e4a` | Reconstructed and differentially executed |
| 5 | `0x00421eba` | `0x00422040` | Reconstructed and differentially executed |
| 6 | `0x004220b2` | `0x00422220` | Reconstructed and differentially executed |

## Class 1

The enabled word is at `0x20000088`: the stock literal at `0x0042221c` points
to `0x2000007c`, and the request reads offset `+0x0c`. Request returns 7 when
the word is zero; when enabled, it sets user bit 1 under a saved PRIMASK if
needed. Release does not check the enabled word and clears the bit if present.
Both return 0 for successful or idempotent operations.

## Class 3 and register update helper

The enabled word is `0x2000008c` (the same literal pointer plus `0x10`). A
new request loads value 3 from stock data at `0x0043414c`, replaces its low
nibble with `0xa`, calls the update helper for register ID 15, then sets the
class-3 user bit. A repeated request skips those writes. Release clears the
user bit; it scans both class-3 bitmap words and writes baseline value 3 from
`0x00434150` only when no user remains. The providers ignore the helper's
status and return 0 after the bitmap update.

The directly called helper at `0x0041d92c` returns 5 for ID >= `0xe0`, 7 for
disallowed mode combinations, and 0 after a register update. It uses two
seven-word mode tables, now source constants verified against stock data at
`0x00433460` and `0x0043347c`. The raw update sequence is: save/disable
PRIMASK; write `0x73` to `0x40010400`; write the supplied value at
`0x40010000 + 4*ID`; write zero to `0x40010400`; restore PRIMASK. Class 3
therefore targets `0x4001003c` with values 10 (request) and 3 (last release).
No clock frequency or physical hardware effect is inferred from these raw
values.

## Class 2 radio mode path

The class-2 request/release pair uses bitmap row 2 at
`0x20026e74 + 16`, enabled word `0x20000080`, selector byte `0x2000007c`,
active byte `0x2002719b`, and callback pointer slot `0x20027040`. It samples
mode bits 8 and 0 of `0x4002012c`. Selector/mode conflicts return status 3;
disabled requests return 7. The selected mode-apply operations write the
observed register block at `0x40020128`/`0x4002012c` using the source words at
`0xc0007000`, `0x20000090`, and `0x20000094`, plus the immediate
`0x0fff8c00` used by stock. Class 2 itself calls only mode-apply selectors 2,
3, and 4; all selectors of stock `0x41d3e4` are source-reconstructed and
differentially tested through the direct helper ABI.

The callback finalizer preserves the 150-count local timeout behavior,
adopts the pointed-to count while active, calls `delay_us(10)`, and clears the
active byte and pointer under saved PRIMASK. Differential fixtures cover
disabled/enabled requests, both mode conflicts, mode 2 and 3 selection,
existing-user callback adoption, last-user mode 4, idempotent release, and
both PRIMASK states. The harness advances callback state only through its
synthetic ROM-cycle-wait hook.

## Class 5 clkgen and dual-switch path

Class 5 uses bitmap row 5 and timeout state byte `0x2002719d` with pointer
slot `0x20027048`. On first ownership it sets initialization byte
`0x2002719f`, updates the class-5 bit, and, when enabled by byte
`0x20000551` and word `0x20027034`, acquires class 2 or 3 for user `0x36`
according to byte `0x20026ff8`. Failure rolls the class-5 user bit back and
releases nested ownership as in stock.

The recovered dual-switch helper at `0x426c8c` sets/clears bit 5 at
`0x40004044`; enabling waits for bit 24 at `0x40004030` with a 100-iteration
`delay_us(1)` poll and returns status 4 on timeout. The class provider ignores
that wait status, then applies the 8-byte config at `0x20026ff8` to registers
`0x4000404c`, `0x40004048`, and `0x40004050`. Last release clears the config
enable, releases nested user `0x36`, and disables the dual switch. Callback
wait uses a 50-count timeout and the shared ROM-bounded delay path.

## Class 6 system PLL path

Class 6 uses bitmap row 6, feature byte `0x2002719a`, initialization byte
`0x200271a0`, config at `0x20027004`, and a handle pointer at `0x2002703c`.
For new ownership, it requests classes 2 and 3 for user `0x35` in the order
selected by the config's low byte; then it initializes the two-word context
at `0x20027010`, validates and applies the observed config fields to
`0x400204d8`, `0x400204dc`, and `0x400204e0`, and enables the PLL when status
bits `19..16` are all set in `0x40020060`. Last release disables and
deinitializes the handle and releases the retained nested class user.

The source helpers preserve the observed context magic `0x01504c30`, config
field bounds, power/isolation bit updates, and lock-wait timeout formula. The
lock result polls bit 0 at `0x400204e4`; tests cover immediate success and
synthetic timeout. The timeout uses the values in the locked routine without
inferring a physical frequency or elapsed hardware time.

## Class 4 and callback delay path

Class 4 uses row 4 in the shared bitmap. Request checks the byte at
`0x20000550`: zero returns status 1, nonzero continues. If there are no
existing class-4 users, it sets bit 0 in word `0x40004044`. When config is
enabled by the word at `0x20027030`, the provider writes
`(*(uint32_t *)0x20026fec | 1)` to `0x40004020`. The last release clears only
bit 0 at `0x40004044`, preserving the other bits. Repeated request and
nonexistent release are idempotent.

The callback state words are byte `0x2002719c` (active), word `0x20027044`
(pointer slot), and byte `0x2002719e` (completion flag). The source preserves
the stock local timeout initialized to 1,000, adopts the pointed-to remaining
count if a callback is already active, publishes a pointer to its local count,
and calls cleanup before returning. The wait loop calls `delay_us(10)` and
decrements the timeout while both the active byte and count are nonzero. On
exit the helper saves PRIMASK, sets the completion flag, clears the active
byte and pointer slot, then restores PRIMASK.

The source `delay_us` conversion reads mode bits at `0x40021000`, converts the
input to float-scaled counts using 32, then selects a threshold: mode selector
2 uses the image constants 250.0 and 96.0 and threshold 24; other modes use
threshold 15. If adjusted count is positive, stock branches to ROM address
`0x40`; source calls its Thumb function pointer `0x41`. The ROM cycle-wait
routine is outside this bootloader. Differential tests execute the source and
stock conversion but intercept that ROM boundary, record the cycle argument,
and clear the synthetic active byte after two waits. This tests cleanup logic
without a wall-clock or hardware timing claim.

## Image identity

The function ranges and hashes are checked against the local authenticated
image and Ghidra `functions-000.jsonl`:

| Stock code | Range | Bytes | SHA-256 |
|---|---|---:|---|
| `clock_request` | `0x004222f0..0x00422364` | 116 | `53cfb358989e68ae979d2814964a3e779ae0f0eba76836f99d409393d0e78d51` |
| `clock_release` | `0x00422364..0x004223d8` | 116 | `6a131868a276083764d4714178857124ccb4209a5f3e7552d874aba7f7c1a54e` |
| class-0 request | `0x00421a30..0x00421a62` | 50 | `55df16968e7cebea48cb197fa9e91b0534c3420fd587d2e362ee3f14e5f2ad12` |
| class-0 release | `0x00421a62..0x00421a94` | 50 | `61afcf0355e0f2fdc9095ff5311cea9e3e52749acc277a981788ccd6f0833473` |
| class-1 request | `0x00421a94..0x00421ad6` | 66 | `0b01e6b1f407cd164536ca7c894b0cb48dcf7c2497814eb3187860633f189a4c` |
| class-1 release | `0x00421ad6..0x00421b08` | 50 | `9aea3a0a0c095098f5c43b3cb3b34fb1565983cda5769771928650d440ef58d5` |
| class-2 request | `0x00421bd2..0x00421cce` | 252 | `beaa4d231ad6eca158c9b2aac09a55b69258e213980ac1ce2cd704a33d1344f5` |
| class-2 release | `0x00421cce..0x00421d28` | 90 | `3dac14d8bed9201a8c8e9147d2216bb399ccb35b33642840d4ad49ad3a691c6e` |
| class-3 request | `0x00421b08..0x00421b5c` | 84 | `891c88359e96db91d98fd0b159621ca6da87bc784c0e3280f4a625dcc1aad579` |
| class-3 release | `0x00421b5c..0x00421ba4` | 72 | `0ec002b261917a95a5afe815494a62f850408c5de5b3a911e81fe3b1df23d06d` |
| class-4 request | `0x00421d5e..0x00421e4a` | 236 | `680cf0628b0c3ed785836da7faeb3fcecf7ab51a02c90ed91c2c5b18442ef899` |
| class-4 release | `0x00421e4a..0x00421e8c` | 66 | `f4f21abad8199cfea2524c7335d809b7f624100c1e34b693c08025ae1fb40a2a` |
| class-5 request | `0x00421eba..0x00422040` | 390 | `5d5e8bce49145dfddb318e0aff9baf61150e00e95f6fc7c804fde126dd11f68c` |
| class-5 release | `0x00422040..0x004220b2` | 114 | `fa335e0a8bf71ef86975470840768672bd90ad0eaac982abfc68e8c84de0bd17` |
| class-6 request | `0x004220b2..0x0042220e` | 348 | `701cc62514c5618aece1f206044e7815375082c6e4a9afa4eafd0e331f331e96` |
| class-6 release | `0x00422220..0x0042228e` | 110 | `f26f053665f5477df6aa97d2e596f08b7045112332919102a5b1dd72d219ea36` |
| clkgen config leaf | `0x00426ccc..0x00426d1e` | 82 | `c9ec02c292145c709613ed59045b804cbe0e697d86c83ed579bd2e3075a49b62` |
| PLL config leaf | `0x0042740c..0x00427522` | 278 | `61aad9e2393f589de90e10cd74396e589ee4aa1547947732738abb105a1ba2af` |
| PLL lock wait | `0x00427522..0x00427588` | 102 | `978d2a48a7b3971bfb7e0d4f2006836aeacb4c137467dfead90d41377316be3e` |
| power-register helper | `0x0041d92c..0x0041d9aa` | 126 | `69608d49656b5685af08e567db6cb31852e5ee8d50767fc393d8bf31c6f2c114` |
| any-class-user helper | `0x004215ae..0x004215dc` | 46 | `11a6cf814c1a66760a988880dac541c55419e26aa1f4c7ef2de27b9a0d7e019f` |
| callback finish | `0x00421d28..0x00421d5e` | 54 | `4b8c76a46e4a846d4c3320718698134d79310d3b4c6a4dc3cb5b0602ab00ba20` |
| callback wait loop | `0x004216b2..0x004216d4` | 34 | `eb69fa2933ef30723f342fbc330927d681c6ca5d2ac077b77bf5e7ed1689a795` |
| `delay_us` | `0x0041d1c0..0x0041d210` | 80 | `c336d5c93475c6521bab00509a8ad8aaa1078b3bdc313ae43107777520af1895` |
| class-4 enable leaf | `0x00426c58..0x00426c72` | 26 | `92fca357b06260aa313efd81bb3c38360a6730eab3b08ae30034113f558e4036` |
| class-4 config leaf | `0x00426c72..0x00426c7e` | 12 | `2d973a6679b7557ee0db61ece3b5e87083256d7f60d653509001616459a23d5f` |
| bit query / update | `0x004215dc..0x004215fe` / `0x00421632..0x004216b2` | 34 / 128 | `8dc0a88874cc74f9148e7ae8b6e70f50b7cd1f732db5b74982a8abcccb1bd6f5` / `bc7fc361719841b4cd3b48adad0bb774fe817371892b0a9cbe4e8744c5ec2a8e` |
| `critical_save` | `0x0041b8ec..0x0041b8f4` | 8 | `720733fcf19a5635fcab0791fcc2b007294712bb27536443ff79490821c168cf` |

The exercised source-versus-stock instruction footprint is recorded per case
in `out/repro/comparison.json`. In the class-5/6 paths, request/release hit
counts are 374/390 and 114/114 bytes for class 5, and 336/348 and 104/110
bytes for class 6. Direct mode-helper cases reach all 88 bytes of its range.
These are dynamic instruction footprints for the tested input cases.

| Stock data | Address | Size | SHA-256 |
|---|---:|---:|---|
| standard mode table | `0x00433460` | 28 | `b735c04032541cece197c93699f0753d37d7af5937bb6cdff15def90dbfe30fc` |
| alternate mode table | `0x0043347c` | 28 | `cc26c6f666de586a513054c9c0ccc99f0d76e213cd5f8a4638264390cb245804` |
| request/release values at `0x0043414c` / `0x00434150` | both contain `03 00 00 00` | 4 each | `9d9f290527a6be626a8f5985b26e19b237b44872b03631811df4416fc1713178` each |

## Remaining boundary and limits

All seven class providers now execute as source against their original
instructions in the standalone harness. The source mode-apply helper covers
selectors 0 through 6 and its invalid-selector path. The bootloader timer's clock ID
7 status 6 is covered by dispatcher tests. Delay and PLL polling use synthetic
register state and intercept the external ROM cycle-wait service at Thumb
address `0x41`.

Unicorn runs the Cortex-M33 model offline. SRAM, enable words, and register
blocks are synthetic. There is no physical MMIO, interrupt delivery, clock
stability, silicon timing, or IAR byte-identity claim. The ROM wait is
intercepted before any real-time behavior.
