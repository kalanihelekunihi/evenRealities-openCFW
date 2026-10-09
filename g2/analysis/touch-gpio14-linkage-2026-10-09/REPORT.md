# Original-address-constrained GPIO linkage

All five linked sections match the complete original bytes: SetHSIOM60,
Write32, SetDrivemode58, SetInterruptEdge36 and Pin_Init188 bytes (374 total).
This resolves the prior Pin_Init raw-relocation boundary and supports the
SetHSIOM full code/literal section accounting. It does not rewrite the raw
object mismatch or historical code-only symbol extents.

The14-byte Pin_Init section-length difference is accounted independently of
relocation resolution: original Thumb instructions tile174bytes through
0x8F92, then2alignment bytes precede three referenced literal words at
0x8F94–0x8FA0 (12bytes). `Pin_Init-instruction-accounting.json` retains every
original instruction and the alignment bytes. Linking alone would not justify
enlarging its extent; both this tiling and the original PC-relative references
support the188-byte compiler section. Independent classification review remains
required. The predeclared174-versus188 raw outcome remains preserved.

`SELECTION.md` and `link.ld` declared fixed addresses before linking. Four
original Thumb BL instructions independently identify the exact helper targets;
their offsets correspond to the four R_ARM_THM_CALL relocations in the unchanged
object. Original PC-relative LDRs reference SetHSIOM literals0x8E5C/0x8E60,
and Pin_Init literals0x8F94/0x8F98/0x8F9C. Those references justify extending
compiler-section accounting beyond historical code endpoints, rather than
choosing a longer extent just because it matches.

`link.py` validates call targets, literal addresses and authenticated original
touch hash before invoking the authenticated14.2 linker. `results.json` records
actual argv/exit/diagnostics, object/linker/script/ELF hashes, original instruction
bytes/literal values and complete linked section equality. The original object,
source, flags and relocation addends are unchanged. No address search or manual
byte patch occurred. Network-disabled nonprivileged Docker uses only read-only
tool/object mounts and this task's output mount.

This is an exact selected-source linkage comparator, not original firmware
execution, a unique producing compiler, complete touch build, physical behavior,
campaign admission or a gate pass. Independent linkage and code/data review
remain pending. No production, Git, device or shared campaign state changed.

Additive review update: `coverage-audit-parallel-2026-10-09/GPIO-LINKAGE-REVIEW.md`
independently confirms all374distinct bytes, four original-BL relocation targets
and Pin_Init174code/2alignment/12literal accounting. The cumulative selected
comparators through this batch are1134unique bytes in11functions across3PDL
translation units; repeated dependency sections are not counted again. This
does not promote the packets to campaign admission or whole-image coverage.
