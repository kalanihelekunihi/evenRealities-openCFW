# G2 bootloader MSPI command-queue pause source candidate

The complete 134-byte body at `[0x00423FB8,0x0042403E)` is the AmbiqSuite
5.1.0 static helper `mspi_cq_pause`. Its authenticated stock SHA-256 is
`ff20411c8e4283f16d82cb8373e95004d648e4c03d151ba89bf43ff7d58a2794`.
The exact semantic identity closes against the unmodified `am_hal_mspi.c` from
upstream commit `5efc0228528a8adce5eae0d226fac85d2551eb3b`, Git blob
`c12ef914660227aba3ebef3a0fb3ec749510c1bc`, under BSD-3-Clause.

## Call graph and ABI

Three direct calls reach the private helper at `0x004240D2`, `0x00425C60`,
and `0x00425CC8`. They correspond to the high-priority scheduler and the two
transfer paths visible in authenticated upstream source. No raw function
pointer to the entry appears in the bootloader payload.

The helper accepts an `am_hal_mspi_state_t *` in `r0` and reads the 32-bit
module at offset four without adding wrapper-side validation. The two far
literals are exact:

- `0x00424BD4` contains `100000`, the 100 ms
  `AM_HAL_MSPI_MAX_PAUSE_DELAY` loop bound.
- `0x00424BD8` contains `0x40060000`, the authenticated Apollo510
  `MSPI0_BASE` value.

The module selects a register bank with a `0x1000` stride. The helper writes
`0x00800000` to `CQSETCLEAR` (`+0x2B4`), then polls CQ enable at `+0x2A0`.
When enabled, it accepts only the designated pause condition formed by
`CQSTAT.CQPAUSED` at bit three and `CQPAUSE` bit seven. Each unsuccessful
iteration calls `am_hal_delay_us(1)` and consumes one of exactly 100,000 delay
slots; the next failed iteration returns status four. A disabled or paused
queue terminates polling and calls `am_hal_delay_us_status_check` with timeout
100,000, `DMASTAT` at `+0x104`, mask one, value zero, and the stock true
comparison flag.

## Providers and redistribution

The only outgoing calls are:

- body offset `0x2A` to the 92-byte `am_hal_delay_us` provider at
  `0x0041D1C0`;
- body offset `0x7C` to the 68-byte `am_hal_delay_us_status_check` provider at
  `0x0041D246`.

Both provider identities and typed ABIs derive from AmbiqSuite 5.1.0
`am_hal_utils.c`/`am_hal_utils.h` under BSD-3-Clause. The public upstream
source file is Git blob `13372860cfd972b02fba13be767d0015b5b58436`, size
12,173, SHA-256
`20a26a34ceb7835fa2a233bbbf2454f5f43e13aeb1ab43d51f5ff14a38f579a3`.
Their current target bodies remain retained official-package bytes; authority
to redistribute those corresponding official bytes is unresolved and is not
inferred from the upstream source license.

## Exact code generation

The isolated BSD-3-Clause candidate preserves the stock instruction and ABI
body while exposing callback-only MMIO and delay ports for host tests. Both
reviewed target profiles emit the same 134-byte section with unrelocated
SHA-256
`66e8cd3f9313756950f835406c64e621358d7f0bcc505cacd1666fb7a5a4339f`.
Each has exactly two `R_ARM_THM_CALL` relocations at offsets `0x2A` and
`0x7C`. Applying the typed target addresses yields the exact stock SHA-256
under both Apple Clang 21 and Homebrew Clang 22.1.8.

Host tests cover the already-disabled path, designated-pause path, bounded
delay-to-disable path, complete 100,000-delay timeout, module-derived MMIO
addresses, pause write, DMA status-check arguments, provider result
propagation, and timeout short-circuit behavior.

The next complete body is the 108-byte AmbiqSuite `program_dma` helper at
`[0x0042403E,0x004240AA)`, stock SHA-256
`d075d73aba138735bc9229bcf8672cb6a1c2fadec21985d2159043534ad130e1`.
It is not admitted by this wave. Physical CQ, DMA, MMIO, concurrency, and
cold-boot qualification is blocked by unavailable physical evidence. No hardware,
flashing, signing, or publishing operation was performed.

Wave 8 subsequently admits that exact `program_dma` body and advances the
current frontier to `0x004240AA` (`sched_hiprio`); see
`g2-bootloader-mspi-program-dma-42403e-4240aa-source-candidate.md`.
