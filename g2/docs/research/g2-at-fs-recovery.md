# G2 eAT filesystem-command recovery

Status: complete linked-object census, clean-room production implementation,
dual-profile canonical admission, and fail-closed behavioral analysis. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path `platform\service\eAT\at_fs.c` owns four linked
bodies and one pool in `[0x005A5530,0x005A5720)`. The bodies contribute 416
bytes with concatenated SHA-256
`6dac5f046c2c46f179431deae73ae7cbf6e77fc391a53542aa17a6033b10795a`;
the 80-byte pool has SHA-256
`d5ee576a68ebf81d47bdf81cb4d1e2d55c659d08759d5e7ab3d4a0eb9c213200`.
The complete 496-byte object has SHA-256
`ec0c3d2a695770371c9d68c14b3b1c0c1ddbcd8ee1e4724dbceaeb90185740ce`.
The independent `AT^NUS` handler and pool end at `0x005A5530`; the next
unrelated command handler begins at `0x005A5720`.

Three sixteen-byte records in `[0x006C92B0,0x006C92E0)` register `AT^RM`,
`AT^LS`, and `AT^MKDIR`. Their odd Thumb pointers are the only stored entries.
The recursive listing helper is reached by two internal calls, one from itself
and one from the LS wrapper. The four bodies contain 33 direct calls. There is
no exterior direct call, other stored entry/interior value, direct
strict-interior target, or `B.W` entry/interior target.

## Command behavior

All filesystem operations gate on the word at `0x200746A8` equalling one.

- `AT^RM` invokes provider `0x0047498C` on the requested path. It returns zero
  and emits a retained error with the provider result on failure; otherwise it
  emits `RM+OK` and returns one.
- `AT^LS` recursively opens and enumerates the requested directory. It skips
  `.` and `..`, constructs child paths as `%s/%s`, prints directories as
  `D <path>`, and prints regular-file byte and integer-KiB lengths after an
  end seek. The wrapper emits `LS+OK` or `LS+ERR` and returns one.
- `AT^MKDIR` invokes provider `0x004CFC5C` with the filesystem object rooted at
  `0x20071AC8` and the requested path, then emits the retained failure or
  `MKDIR+OK` response.

Only `_atRM` survives as an exact function-name string. The helper and other
two handlers therefore use descriptive names. The analyzer pins all body and
pool bytes, command records, strings, readiness/global operands, direct-call
closure, and complete ingress topology.

No authenticated historical source or license is available. The independently
authored MIT implementation in `components/apollo_main/core_overlay/at_fs.c`
replaces the three AT command-record handler pointers through strict,
canonical Apple/Linux relocation contracts. The 416-byte stock-body area is
independently occupied by the LC3 provider on Apple, so the final LC3 suffix
replay rebases the command pointers instead of fabricating colliding entry
branches. Host runtime tests cover readiness gating,
remove success/failure, recursive traversal, dot-entry filtering, size output,
open failure, pacing, and mkdir results. The complete packages and build
receipts authenticate all redirects and routed text for both profiles.

The remaining physical qualification is blocked by unavailable physical
evidence. Required evidence is an authorized G2 mounted-storage trace covering
remove/list/mkdir plus readiness and provider faults. No hardware operation was
performed (`hardware_operations=[]`); this blocker is not a software gap.
