# Clock dispatchers and recovered providers 0, 1, and 3

## Result

`clock_manager.c` reconstructs the stock `clock_request` and `clock_release`
dispatchers and class-0 bookkeeping provider. `clock_class_providers.c`
reconstructs classes 1 and 3, their user-bit operations, and the directly
called `0x0041d92c` register-update helper. Request/release providers for
classes 2, 4, 5, and 6 remain explicit link dependencies.

`make test` passes **58 source-versus-image cases** and reaches **894 distinct
stock instruction bytes**. The tests cover dispatcher ID/user truncation and
bounds, class-0/1/3 bit transitions and idempotency, class enable words,
PRIMASK values, class-3 last-user behavior, lower register-helper allow/deny
paths, and the helper's ID bounds. Classes 0, 1, and 3 plus their common
helpers run as stock and source; classes 2, 4, 5, and 6 are intercepted at the
stock provider entry and compared with test stubs.

Reproduce with `make clean && make test` from this directory. Results, source
and image hashes, raw instruction trace, and detailed per-case state are in
`out/comparison.json`. The reference image SHA-256 is
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

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
| 2 | `0x00421bd2` | `0x00421cce` | External provider cut |
| 3 | `0x00421b08` | `0x00421b5c` | Enable-word gate, class-3 bitmap, register-15 update on first/last user |
| 4 | `0x00421d5e` | `0x00421e4a` | External provider cut |
| 5 | `0x00421eba` | `0x00422040` | External provider cut |
| 6 | `0x004220b2` | `0x00422220` | External provider cut |

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
| class-3 request | `0x00421b08..0x00421b5c` | 84 | `891c88359e96db91d98fd0b159621ca6da87bc784c0e3280f4a625dcc1aad579` |
| class-3 release | `0x00421b5c..0x00421ba4` | 72 | `0ec002b261917a95a5afe815494a62f850408c5de5b3a911e81fe3b1df23d06d` |
| power-register helper | `0x0041d92c..0x0041d9aa` | 126 | `69608d49656b5685af08e567db6cb31852e5ee8d50767fc393d8bf31c6f2c114` |
| any-class-user helper | `0x004215ae..0x004215dc` | 46 | `11a6cf814c1a66760a988880dac541c55419e26aa1f4c7ef2de27b9a0d7e019f` |
| bit query / update | `0x004215dc..0x004215fe` / `0x00421632..0x004216b2` | 34 / 128 | `8dc0a88874cc74f9148e7ae8b6e70f50b7cd1f732db5b74982a8abcccb1bd6f5` / `bc7fc361719841b4cd3b48adad0bb774fe817371892b0a9cbe4e8744c5ec2a8e` |
| `critical_save` | `0x0041b8ec..0x0041b8f4` | 8 | `720733fcf19a5635fcab0791fcc2b007294712bb27536443ff79490821c168cf` |

| Stock data | Address | Size | SHA-256 |
|---|---:|---:|---|
| standard mode table | `0x00433460` | 28 | `b735c04032541cece197c93699f0753d37d7af5937bb6cdff15def90dbfe30fc` |
| alternate mode table | `0x0043347c` | 28 | `cc26c6f666de586a513054c9c0ccc99f0d76e213cd5f8a4638264390cb245804` |
| request/release values at `0x0043414c` / `0x00434150` | both contain `03 00 00 00` | 4 each | `9d9f290527a6be626a8f5985b26e19b237b44872b03631811df4416fc1713178` each |

## Remaining boundary and limits

The missing source providers are classes 2, 4, 5, and 6. The remaining
addresses are listed in `provider-cut-aliases.ld` as test-only aliases into
the locked image; those aliases do not constitute source implementations.
The bootloader timer's clock ID 7 return of status 6 is covered by the
dispatcher tests. Timer selector paths through class 4 still require that
class's implementation.

Unicorn runs the Cortex-M33 model offline. SRAM, enable words, and the power
register block are synthetic. There is no physical MMIO, interrupt delivery,
clock stability, silicon timing, or IAR byte-identity claim. Test stubs only
cover classes 2, 4, 5, and 6 with deterministic statuses.
