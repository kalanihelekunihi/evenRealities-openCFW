# G2 ALS dependency boundary

Status: software-complete and production-routed. Authenticated against G2
2.2.6.10; live physical validation is blocked by unavailable evidence.

The retained `driver\sensor\als\als.c` anchors nine functions / 2,114 bytes,
but the adjacent source-order and internal-call graph expands the candidate
object to 38 functions / 3,858 body bytes / 1,461 instructions in
`[0x004AD9B8,0x004AEA40)`, 4,232 physical bytes. This corrects the tentative
start at `0x004ADAB8`: the preceding seven pathless state/callback helpers begin
exactly where the already closed `charger_common.c` object ends.

The 189 direct calls comprise 50 internal and 139 external edges. Every
external reusable edge is already bounded:

- 105 EasyLogger calls use the admitted `a596b264…` baseline.
- one call is exact CMSIS-FreeRTOS v10.5.1 `osDelay` at `d213f261…`.
- four calls are bounded IAR/runtime `memset` and unsigned division seams.
- 23 calls terminate at closed first-party time, sync, settings, heading,
  device-role, and system-policy providers.
- six calls reach the local TI OPT3007 field/register adapter: two field writes
  at `0x0051357C`, two field reads at `0x005135D2`, the already closed register
  map constructor at `0x005135E0`, and one register read at `0x00513748`.

The OPT3007 adapter is private G2 code constructed from TI's public SBOS864
register specification, not a copied public software library. Its exact
19-triple schema is already recovered, and no public code repository or commit
exists to admit. Thus this object adds no third-party family or unresolved
utility provenance; it composes the existing clean-room TI-spec boundary.

The complete audit pins all 38 function intervals, 374 literal/padding bytes,
21 retained-path references, 60 direct entry sites, and the following
zero-anchor `cb_charge.c` boundary. One stored Thumb callback targets
`0x004AE73C`. The sole indirect call dispatches through the already bounded
display-driver interface. The apparent branch at `0x004AE09C` begins halfway
through a real 32-bit instruction and is explicitly rejected as an unaligned
pseudo-`BL`; there is no executable strict-interior ingress.

The clean-room `components/apollo_main/core_overlay/als.c` implementation
recreates all 38 functions and compiles each independently under the reviewed
Cortex-M55 profile. Thirty-eight guarded redirects replace all 3,858 stock
function bytes. The appended closure contains 2,216 Thumb text bytes, 48 bytes
of authenticated brightness-curve read-only data, 30 alignment bytes, and 82
strict relocations; only the 374-byte stock literal/alignment closure remains
official. Host oracles cover sampling, pitch filtering, OPT3007 conversion and
initialization, curve/scale learning, brightness sync, manual lockout, timer
transitions, and open/close behavior.

Canonical identities are overlay 257,980 bytes / `09f0371422…c94fbb`, Apollo
component 3,781,376 bytes / `96447430fe…39130`, package 4,559,870 bytes /
`a7d64172ab…5e305`, and flash plan 2,943,327 bytes / `74c7bc32a7…39b9`
with 4,239 placed, two unresolved, five container-only, and six protected
regions. No firmware was signed or flashed. The authorized right temple is
nonresponsive, the authorized left temple must remain stock, and no responsive
authorized ALS path, calibrated lux reference, or golden OPT3007 trace is
available; physical validation is explicitly blocked rather than claimed.

Reproduce with `make als-closure`.
