# System interface independent review

[Verification](SYSTEM-INTERFACE-VERIFICATION.json), [read-only parser](system_verify.py), [input receipts](../touch-pdl14-system-interface-2026-10-09/results.json).

Integration passes review. The header bytes match acquisition SHA 5eb47d11872c01221d27a5b8be87327fc564aafdd1fb6fde2eea2421161ecf99 and the independently acquired official CY8CPROTO-040T header. The receipt pins official CY8CKIT-040T commit d1bf634023bf92d083ad0e32083987f67b4a64e6; this review checks local preserved provenance/content, without a second acquisition. Its operative additions are declarations: ISR function-pointer type, uint32 delay globals except uint8 cy_delayFreqMhz, and 48-element vector declarations. No executable implementation, guessed global value or runtime stub is introduced.

All three actual argv lists retain -DCY8C4046FNI_T412, Cortex-M0+/Thumb/-Og and the prior source/tool paths. /interface precedes /headers; dependency receipts confirm the official header is consumed and /headers/system_cat2.h is not. All consumed input and output hashes match disk. The separately acquired BSP defaults to CY8C4046LQI-T452 (bsp.mk lines44–45), but that BSP makefile/device macro is not imported. Family-header compatibility is not proof of original producer BSP identity.

The same twelve target rows survive (comparison ignores ordering and the original failure-status field). Independent ELF parsing verifies nine emitted sections' hashes, lengths, recorded mismatch positions and relocation offset/type/symbol; three absent sections are genuinely absent. Original census results still preserve all twelve compile failures and diagnostics (receipt SHA dc10f27ffb3c3ef23adf8f445f4758bbf8a3dfd73764400b9f4beaa441c0d045). New success supersedes the missing-declaration blocker without erasing that evidence.

Finite accounting: 54 selected = 23 reviewed + 31 unresolved. After the previously reviewed nine full extents, 16 old boundaries plus nine newly compiled boundaries yield 25; two old absent plus three new absent yield five; one inline contract remains. No new exact section is admitted here. The system-interface REPORT.md still describes the earlier 34 boundaries/nine awaiting review and 1260-byte aggregate; that paragraph is stale relative to the completed independent extent review. Updated bounded totals are 2320 comparator bytes/23 functions, with 25 boundaries, five absent and one inline. This is bookkeeping chronology, not evidence that these31are closed.

Justified next checks, without duplicate builds:

- Cy_SysTick_Enable: existing24-byte relocation-free section matches historical20 instruction bytes. Review the appended four-byte literal and original PC-relative references against the authenticated target.
- Cy_SysTick_SetClockSource: existing24-byte relocation-free section matches historical18 instruction bytes. Review alignment and appended literal references. Both are static extent opportunities, not runtime blockers.
- For emitted delay/vector routines, bind preserved ARM relocations to authenticated target call/global addresses; do not guess cy_delay globals, __RAM_VECTOR_TABLE, __Vectors, or callback-array storage. Empty symbol names in SysTick relocation receipts denote section symbols and need section-index/addend interpretation rather than invented unnamed dependencies.
- For DelayCycles, EnterCriticalSection and ExitCriticalSection, locate their genuine assembly/inline emission contracts; missing .text.name sections do not imply unavailable source or absent firmware.

Only audit outputs were written. No builds, firmware/source changes, Git mutations or device access occurred.
