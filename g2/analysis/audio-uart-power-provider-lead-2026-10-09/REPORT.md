# UART peripheral-power provider: concrete next boundary

Static follow-up of the sealed UART wrapper reaches enable0x47F5B8 and disable0x47F7AE, through descriptor lookup0x47EF18. The prior source-backed descriptor provider already covers these table records; no duplicate source implementation or fresh instruction-test claim is made here.

Authenticated raw image19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701 loaded0x438000, table0x6BECB0, rows11..14 (UART modules0..3):

| Domain | Enable register | Enable mask | Status register | Status mask |
| --- | --- | --- | --- | --- |
| 11 | 0x40021004 | 0x200 | 0x40021008 | 0x1E00 |
| 12 | 0x40021004 | 0x400 | 0x40021008 | 0x1E00 |
| 13 | 0x40021004 | 0x800 | 0x40021008 | 0x1E00 |
| 14 | 0x40021004 | 0x1000 | 0x40021008 | 0x1E00 |

Individual enable bits share the same group status mask. Do not infer an individual UART power acknowledgement from one status bit.

Enable statically returns immediately if its enable bit is set. Otherwise it runs pre-wrapper0x48032C, optional grouped-domain callback0x480312, saves IRQ mask0x473940, sets enable bit, restores interrupts, invokes post-wrapper0x480342, then polls0x480826 and checks group status. Domain20/23/29 special paths are irrelevant to UART11..14 and can be excluded from a bounded UART-specific test.

Disable returns immediately if the enable bit is already clear. Otherwise pre-wrapper, saved IRQ mask, clear bit, IRQ restore, eligibility/group-state predicate0x47F6F2; only nonzero predicate reaches its poll and grouped callback. Post-wrapper follows. Real register side effects and polling latency remain external to static evidence.

Next useful bounded source closure: predicate0x47F6F2, pre/post wrappers0x48032C/0x480342, group callback0x480312 and actual masked poll0x480826, composing existing descriptor and interrupt-mask sources. This is an actionable source lead, not an external-input blocker. Missing scheduler/device traces still prevent physical shutdown/completion claims. Clock dispatch is already recovered separately and need not be reinvestigated.

[Sealed UART wrapper comparisons](../audio-uart-power-config-2026-10-09/REPORT.md), [existing descriptor source evidence](../power-domain-descriptor-2026-10-06/REPORT.md). No source-exhaustion or whole-system completion claim; no device/production/shared-state edits.
