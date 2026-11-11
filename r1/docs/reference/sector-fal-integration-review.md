# R1 sector/FAL integration and header R6 correction

The later [save-frame review](flash-read-frame-review.md) closes the retained
counterexample for its bounded native-chain matrix at controlled adapter
placement. This document records the earlier discovery and R6 repair.

The sector stepper now restores native R6 = 0 before its first header-provider
call, then resumes the C PREPARE stage afterward. The prior adapter exposed
its internal `0x80000001` stage in R6. This matters beyond ordinary C argument
passing: FAL saves callee-saved registers into stack bytes that a subsequent
partial TSL read can consume. The adapter grows from 88 to 100 bytes; all C
policy workers remain byte unchanged.

REA observes native FAL read at `0x631e8` through `0x63293` (172 bytes). Its
32-byte entry save includes R6. The locked application SHA-256 remains
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

[Machine-readable evidence](sector-fal-integration-review.json) separates
three kinds of comparison:

- The 12,302 direct stock/C sector cases pass again, now asserting native R6
  as well as SP at header-provider entry. Outcomes remain 11,856 returns,
  206 assertions and 240 bounded 16-read prefixes.
- 1,920 wider source-chain cases execute the actual C read adapter, TSL/status
  control, FAL partition read and partition/cache lookup. They compare the
  corrected stepper against the original reconstructed sector assembly using
  those same C providers at identical helper addresses. All return and match,
  including partial/non-writing final driver outcomes, FAL wrapping bounds,
  missing devices, diagnostics, views and shared access order. The final flash
  driver, printf and path getter are modeled.
- The previous stepper fails that wider comparison. A retained case captures
  `0x80000001` rather than zero in the header-call R6 and in the source helper's
  later nested read-buffer residue. Removing the new R6 reset or shifting the
  provider SP is rejected by the direct probe.

Full native-chain equality is **not established**. A stock/source counterexample
is retained without normalizing its stack-derived values. With a valid seeded
header, no driver writes, partition bound zero and database sector size 80,
both versions return error 2, but sector +16 is `0x44444445` in stock versus
`0x2` in the current C chain. Sector +36 also differs. The native read-adapter
and FAL prologues overwrite the future read buffer differently from the
currently compiled C helpers. Restoring header R6 repairs the stepper's added
leakage; it does not resolve those existing helper-frame/placement differences.
The next full-chain qualification must reconcile those frames rather than
substitute initialized bytes or claim equivalent metadata.

All other 574 object hashes, the manifest, function-name owner and import sets
are unchanged. All 575 R1 units compile without failures or duplicate strong
symbols; imports remain 175 application and 34 bootloader. `make sources-check`
passes. Five qualification variants compile, with no exact region selected.
The canonical plan remains at 3,881 source-built application bytes, 642,279
binary pull-through bytes and 248 resource bytes. The hybrid application still
equals stock, with source completeness false.

Source-chain agreement is evidence for this correction, not native firmware
equivalence. Physical flash, startup, concurrency, arbitrary corruption, full
source linking and byte-identical source rebuilding remain unproven. No G2
gate advances; the overall goal remains active.
