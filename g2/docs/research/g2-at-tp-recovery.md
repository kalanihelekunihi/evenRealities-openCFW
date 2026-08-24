# G2 eAT touch-panel command recovery

Status: complete linked-object census, fail-closed behavioral analysis, and
production-routed clean-room C; hardware behavior is explicitly blocked by
unavailable authorized physical evidence. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path `platform\service\eAT\at_tp.c` owns a small
configuration-print helper, exact-named `_atTpTest`, one alignment halfword,
and a literal pool in `[0x005A5984,0x005A5D94)`. The two bodies contribute 898
bytes with concatenated SHA-256
`23d47d710882ff10a69e14e9e27b450fbe04ad838295a3c07965934c8f6509e0`.
The 142 non-code bytes have SHA-256
`9a346273272f4bc2feadfb900fead304af2b893fd18a5ca908d408894e18025f`.
The complete 1,040-byte object has SHA-256
`d6b869880ca7b842b74efd388baeee07790680c4bc40a20ea0a08bc8cdf7659d`.
The previous command object's pool ends at `0x005A5984`; the next unrelated
body begins at `0x005A5D94`.

The sixteen-byte record `[0x006C93A0,0x006C93B0)` registers `AT^TP` with odd
Thumb pointer `0x005A5999`. That is the only stored entry. The main handler
calls the print helper twice. The two bodies contain 70 direct calls. There is
no exterior direct call, other stored entry/interior value, direct
strict-interior target, or `B.W` entry/interior target.

## Command behavior

The handler logs two input parameters and recognizes eight operations:

- `1` reads five 16-bit difference values and prints them; `0` invokes the
  corresponding stop/control provider.
- `debug1` and `debug0` set or clear byte `0x20075017`.
- `bsln_read` reads and reports the 16-bit proximity baseline.
- `bsln_set` sends the baseline-save sequence and emits the retained success
  response.
- `gesture_cfg_read` reads the two-byte gesture configuration and prints its
  long-press threshold through the local helper.
- `gesture_cfg_set,<threshold_ms>` parses exactly one unsigned value, requires
  1-65,535, writes it through provider `0x0055B840`, delays 100 ms, reads it
  back through `0x0055B92A`, and rejects write, readback, or comparison
  failures separately. A verified value is printed and acknowledged.

Successful dispatch reaches retained `AT^TP+OK`; validation and provider
failures return zero with their distinct retained diagnostics. The analyzer
pins the bodies, alignment/pool bytes, command registration, exact symbol and
path, every subcommand/format, provider sites, threshold bounds, debug global,
and complete ingress topology.

## Production closure

`components/apollo_main/core_overlay/at_tp.c` is the independently authored
production implementation. Two selector-isolated Thumb leaves contribute
1,548 bytes plus two alignment bytes and use eighteen strict relocations. Two
guarded `B.W` replacements cover the entire 1,040-byte stock object, including
its alignment and literal pool; the stored command pointer continues to enter
the authenticated stock address, which now redirects to source-owned code.

Host tests cover every subcommand, both configuration bounds, malformed and
null input, provider failures, readback mismatch, successful verification, and
the stock unknown-command acknowledgement. The decimal parser is bounded and
fail-closed. The canonical Apple overlay/component/package identities are
188,812 / 3,712,208 / 4,490,702 bytes with SHA-256
`a4c7927efe625a95e3bd928e5bb75b32c057837577dd9b9bf0cc3a5c19a42183`,
`026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a`,
and `03d4b3f7813ce41814ae821ccbdaa3a1f2802fe4a459cf20351487a18332e783`.

No hardware was accessed or flashed. Live Cypress-controller I/O, proximity
baseline persistence, gesture-threshold write/readback timing, debug sampling,
and physical gesture behavior require an authorized G2 with its touch panel.
That evidence is unavailable in this workspace, so hardware validation is
explicitly blocked and functional completeness is not declared.
