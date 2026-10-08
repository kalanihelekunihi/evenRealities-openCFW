# Apollo510 clock-mux low-power initialization child

## Identity and boundary

The locked input is `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`,
SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`,
loaded at `0x410000`, Thumb M33. Ghidra's verified function record is
`0x41acb2..0x41b04b` inclusive, 922 bytes; the half-open range is
`0x41acb2..0x41b04c`. The requested `0x41b040` lies inside the final marker
write. `verify_stock.py` authenticates this boundary against both the locked
hash and the function inventory.

The behavior is strongly consistent with the clock-mux reset portion of Apollo510
low-power initialization. The pinned HAL 5.1 replay (`5efc0228528a8adce5eae0d226fac85d2551eb3b`) contains
the named `am_hal_pwrctrl_low_power_init()` implementation in
`ambiqhal/mcu/apollo510/hal/am_hal_pwrctrl.c` (SHA-256
`84cc1da6a01dd46f29e0465074ad92602c4dd6d7a12f7f4596aef64a9a250586`). That
public function calls `am_hal_sysctrl_clkmuxrst_low_power_init()` at line 2454.
The replay has no definition for that helper. Its `apollo510.h` declares
`STIMER.HALSTATES` at `0x40008858`, including a 16-bit signature field and the
saved clock-source bits used by this stock body. The stock constant is
`0x5af0`; the header does not define its value. This supports a strong
family-level correspondence to the clock-mux helper called by the public low-power routine;
it does not prove producing-source identity or a full match to the public
`am_hal_pwrctrl_low_power_init()` body.

## Reconstructed behavior

[`reconstructed_low_power_init.c`](reconstructed_low_power_init.c) expresses
the stock decisions and ordered MMIO effects in readable C. It uses the pinned
Apollo510 CMSIS types for `STIMER.HALSTATES`, `CLKGEN.CLOCKENSTAT`,
`CLKGEN.MISC`, `MCUCTRL.PLLCTL0`, and `MCUCTRL.PLLMUXCTL`, with compile-time
offset checks. Unknown words remain raw addresses instead of guessed register
names. The adjacent word at `0x4000885c` and the word at `0x400200c0` are not
named by the copied HAL header.

The initial guard runs the main body only when the adjacent word's bit 1 is
clear and `STIMER.HALSTATES[31:16] == 0x5af0`. It operates on saved-state bits
0..5 (AUDADC clock-gen-off, HFRC dedicated, HFRC2, XTAL, external reference,
PLL), uses bit 6 for PLL reference selection, and finally rewrites HALSTATES
with the `0x5af0` signature whether or not the guard or saved-state tests pass.
The mapped HAL fields are register-layout evidence; the behavior is grounded
in the locked instructions.

### Incoming register carry

The function call at `0x41c7c0` does not establish an R5 argument. When the
initializer's factory-cache flag is clear, its path loads R5 at `0x41c606`
from literal `0x41cb5c` (`0x20027064`) and stores a value through it at
`0x41c60a`. If that path is skipped because the cache flag was already set,
the existing incoming R5 instead remains live. The intervening stock helper
preserves callee-saved R5. In the target body, `0x41ae1a` performs
`BFI R5, R0, #0, #4` with R0 equal to 10; the subsequent update therefore
receives `(incoming_R5 & ~0xf) | 10` (the literal-loaded path yields
`0x2002706a`). The C uses an explicit `r5_gpio_carry` machine-state field. It
does not call this a normal formal argument, assign it zero, or claim the carry
is defined by the C ABI. The test varies R1/R2/R5 entry-state fields; R3 has no
recovered side effect in this child. A caller-side wrapper must capture or
establish the actual R5 carry.

## Direct child call and argument contracts

The call-site trace in `stock-disassembly.txt` is bound to the image hash.
Arguments below are the concrete register/stack values set at each call; return
statuses are ignored by this parent unless stated otherwise.

| Child address | Body range | Stock call contract |
|---|---|---|
| `0x41d1c0` | `0x41d1c0..0x41d210` (80 B) | Delay calls with R0 = 1, 5, 1500, 5, 1, 20 microsecond-unit arguments as passed to the child. No physical elapsed-time claim follows. |
| `0x41d246` | `0x41d246..0x41d28a` (68 B) | `(200, 0x40004030, 0x01000000, 0x01000000, 1)`; the fifth argument is at `[SP]`. This is a status-poll cut, not a proven timer measurement. |
| `0x41d3e4` | `0x41d3e4..0x41d676` (658 B) | Mode 2 with pointer `SP+1`; later mode 4 with pointer `SP`. R2/R3 are not explicitly initialized at the call sites; the recovered child branches for modes 2 and 4 do not consume them. |
| `0x41d90e` | `0x41d90e..0x41d92c` (30 B) | `(15, &local_pin_config)`; return status ignored. |
| `0x41d92c` | `0x41d92c..0x41d9aa` (126 B) | First `(15, (incoming_R5 & ~0xf) | 10)`, later `(15, local_pin_config)`; update statuses ignored. Current source mapping exists at `g2/components/bootloader/clock_manager/clock_class_providers.c`. |
| `0x41ca5c` | `0x41ca5c..0x41caa2` (70 B) | No arguments; return ignored. |
| `0x41bf84` | `0x41bf84..0x41c0be` (314 B) | Selectors 30, 31, 32, 33, 26, 27; all return statuses ignored. Current source mapping exists in `platform_control/power_domains.c`. |
| `0x41e348` | `0x41e348..0x41e442` (250 B) | `(NULL, 1)` whole-cache invalidate path; return ignored. Current source mapping exists in `g2/components/foundation/cache_maintenance/cache_maintenance.c`. |
| `0x41c17a` | `0x41c17a..0x41c2d8` (350 B) | Selectors 30, 31, 32, 33, 26, 27; all return statuses ignored. Current source mapping exists in `platform_control/power_domains.c`. |
| `0x41caa2` | `0x41caa2..0x41cae2` (64 B) | No arguments; return ignored. |

Current source candidates are present for delay `0x41d1c0` in
`g2/components/bootloader/clock_manager/clock_class_provider4.c`, status poll
`0x41d246` in `g2/components/bootloader/nor_mspi_init/status_poll.c`, mode
apply `0x41d3e4` in `clock_class_provider2.c`, register update `0x41d92c` in
`clock_class_providers.c`, PLL power helpers `0x41ca5c`/`0x41caa2` as static
functions in `clock_class_provider6.c`, and cache invalidate `0x41e348` in
`g2/components/foundation/cache_maintenance/cache_maintenance.c`. The read
leaf at `0x41d90e` is reconstructed in this owned directory from its locked
instructions because no corresponding source body was located. The mapping
for `0x41bf84`/`0x41c17a` is
`g2/components/bootloader/platform_control/power_domains.c`. Public HAL
5.1.0 contains `am_hal_pwrctrl_low_power_init()`, but the local replay has no
definition of its called private
`am_hal_sysctrl_clkmuxrst_low_power_init()`.

## Validation and limits

Run:

```sh
python3 g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-clockmux/verify_stock.py
BASE=g2/analysis/bootloader-completion-2026-10-06
INC=$BASE/upstream-worker/ambiqhal-apollo510/ambiqhal/CMSIS/AmbiqMicro/Include
CMS=$BASE/upstream-worker/ambiqhal-apollo510/cmsis-5-590/CMSIS/Core/Include
clang --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -std=c11 -O1 \
  -Wall -Wextra -Werror -ffreestanding -fno-builtin -I "$INC" -I "$CMS" \
  -c "$BASE/inventory-worker/startup-clockmux/reconstructed_low_power_init.c" -o /tmp/clockmux.o
clang --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -std=c11 -O1 \
  -Wall -Wextra -Werror -ffreestanding -fno-builtin \
  -c "$BASE/inventory-worker/startup-clockmux/stubs.c" -o /tmp/clockmux-stubs.o
arm-none-eabi-ld -T "$BASE/inventory-worker/startup-clockmux/module.ld" \
  /tmp/clockmux.o /tmp/clockmux-stubs.o -o /tmp/clockmux.elf
/Users/kalani/.local/share/opencfw/venv/bin/python \
  "$BASE/inventory-worker/startup-clockmux/verify_native.py" /tmp/clockmux.elf \
  "$BASE/inventory-worker/startup-clockmux/native-comparison.json"
```

Static original-instruction checks pass for the locked hash, function size/end,
literal MMIO map, direct child call targets, the R5 load/use chain, and key
guard/epilogue instruction sites. `stock-disassembly.txt` is the bounded
original listing and `stock-check.json` records the static receipt.
`native-comparison.json` records 112 dynamic comparisons: original stock bytes
at `0x41acb2` in Unicorn 2.1.4 Cortex-M33 mode against the linked C leaf. The
test compares child call order and defined arguments (including the status
poll stack argument and R5-derived pin update), ordered MMIO writes, final
mapped MMIO words, and PRIMASK preservation. Fixtures vary saved state, R1/R2
carry, R5 carry, and the power-register read value. It caught and corrected a
wrong final GPIO condition and compiler-combined PLL stores before passing.
The earlier `native-comparison.json` receipt has 112 cases with direct child
cuts and remains preserved. `native-chain-with-power-comparison.json` is the
9-case source-child receipt; `native-chain-cache-expanded.json` supersedes it
for review with 13 cases and explicit cache fixtures. `build_native_chain.sh`
compiles the root-owned carry wrapper/body and links current source children
for delay, poll, mode helper, getter, updater, PLL power init/restore, cache
invalidation, and the power-domain enter/leave functions. Both chain receipts
compare R0/R1/R2, R4-R11, SP, PRIMASK, child-call events, ordered MMIO/system
writes, and final mapped MMIO state.
Power-domain enter/leave calls execute source with selectors 30, 31, 32, 33,
26, and 27; power-domain source calls descriptor copy, critical save/restore,
status polling, hooks, and register updates. The test-only services for
selectors 20, 23, and 29 are asserted unreachable in these fixtures.

The expanded cache fixtures exercise the caller's `(NULL, 1)` whole-invalidate
call with CCR cache enable both set and clear, and CCSIDR geometries of 1x1,
3x2, 2x3, and 4x4 sets/ways. With cache enabled, recorded writes to
`0xe000ef74` match the exact way/set values and count; with it disabled, no
maintenance-register writes occur. System writes in `0xe000e000..0xe000efff`
are recorded and compared, alongside R0/R1/R2, R4-R11, SP, and PRIMASK.
Control-to-status acknowledgement is synthesized on writes to
`0x40021004`/`0x4002100c` identically for stock and source. Both status-poll
bodies execute against those status values; ROM cycle-wait at `0x40` is
controlled. These fixtures do not claim physical status timing, hardware
acknowledgement, or cache coherency.

The mode helper is entered on the full stock 658-byte function; these
clockmux cases reach 254 unique bytes, at `0x41d3e4..0x41d3f9`,
`0x41d438..0x41d43b`, `0x41d452..0x41d4d7`, `0x41d4f2..0x41d4f3`, and
`0x41d586..0x41d5e1`. These are the selector-2/4 paths exercised here; the
other selector paths of that 658-byte function are outside this chain's proof.
Provider2's independent report covers all selectors at the helper ABI.

To rebuild and run the source-child chain and standalone getter comparison:

```sh
g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-clockmux/build_native_chain.sh
/Users/kalani/.local/share/opencfw/venv/bin/python \
  g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-clockmux/verify_native_chain.py \
  /tmp/clockmux-chain/clockmux-native-chain.elf \
  g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-clockmux/native-chain-cache-expanded.json
clang --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -std=c11 -O2 \
  -ffunction-sections -fdata-sections -ffreestanding -fno-builtin \
  -Wall -Wextra -Werror -c \
  g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-clockmux/power_register_read.c \
  -o /tmp/power-register-read.o
arm-none-eabi-ld \
  -T g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-clockmux/power-read.ld \
  /tmp/power-register-read.o -o /tmp/power-read.elf
/Users/kalani/.local/share/opencfw/venv/bin/python \
  g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-clockmux/verify_power_read.py \
  /tmp/power-read.elf \
  g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-clockmux/power-read-comparison.json
```

The 10-case standalone getter comparison in `power-read-comparison.json`
exercises IDs 0, 15, 223, 224, 255, and `UINT32_MAX`, null/non-null outputs,
MMIO values, and PRIMASK against stock `0x41d90e..0x41d92c` (30 bytes).
These are bounded behavioral comparisons, not byte-identity evidence or
complete firmware source closure. No physical timing, electrical, or
clock-stability behavior is claimed. The HAL replay's missing private
clock-mux helper remains an exact source-availability gap; its absence does
not block this instruction-derived leaf and child comparison. The candidate
has not been integrated into a firmware component or compared for byte
identity.
