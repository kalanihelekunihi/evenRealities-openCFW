# OpenCFW change scan — 2026-10-07 22:16 UTC

Compared with saved 21:29 UTC scan. Read-only project inspection; only this report and snapshot.json were written. No tests, generators, staging, shared campaign changes or firmware changes. Concurrent work can advance after this snapshot.

## Source changes

Scoped bootloader/foundation C/header/assembly inventory increased from415 to421 (332 bootloader,89 foundation). All415 baseline file hashes remain unchanged; six new files, no removals. New directory g2/components/bootloader/initializer_callbacks/pcm22_hot_native/ contains four C files and two headers, plus README.md. These include reused initialized-data and startup-event variants, so six files must not be counted as six newly reconstructed functions. Exact paths, hashes and sizes are in snapshot.json.

The completed220-object checkpoint e5972f996f4ffc9a08ac54ba8e92e07cbc1745425db32b1eb78a9c9dea67b7ff adds reconstructed selectors5,11,12,21:514,568,318,344 original body bytes, totaling1744. Its report explains LP/HP switching, TON adjustment, trim boost/restore, cache handling and deferred continuation publication. Existing direct comparison receipts cover579 selector5 and796 selector11/12/21 cases. Independently hashed candidate ELF matches all seven integration receipt identities:2 normal/update,3 malformed-input,2 interrupted-update; all report PASS. Existing report also documents290 full-FPSCR QEMU comparisons and exact frozen-object relink/component-object reproduction. These checks were inspected, not rerun in this scan. Native updater normal/targeted coverage remains756/758 body bytes; three synthetic above-four temperature mutations are separate prefix tests, not normal completed coverage.

## Work in progress, not a completed checkpoint

New isolated222-object candidate e5c70f86f09717487f2e85f76b507ed9d79a374f1baa90eda9d4b7f40a4bd143 is independently hashed. Its owned pcm22-deferred21-rollback-integrated directory has115 bounded scheduling comparisons for deferred body429da4..429df6, post callback42a036..42a04a and existing hook41cdfa..41ce10;145 direct rollback selector22 comparisons for429e00..429f68; and four bounded native mode-chain comparisons. Receipts match this candidate identity. Newly recovered bodies total462 original bytes (82+20+360); existing wrapper is reused.

Concrete new understanding: completion rereads current major state independently for CORE temperature coefficient, CORE trim and VDDC trim, then clears continuation byte200271bc. It is not an atomic claim/cancel operation. Synthetic cancellation after entry does not stop remaining writes; republished flag is subsequently cleared. The mode controller invokes the post hook on success and on failed HP readiness/switch, then failure rolls back through selector22. Main tested chain is synchronous under a saved interrupt mask; injected scheduling tests do not establish hardware race behavior.

Only the two normal/update integration cases have a final PASS receipt at scan time. Malformed-input and interrupted-update receipts are absent; no complete seven-case validation, final component delivery or completed promotion is inferred. Intermediate221-object44b51b73 checkpoint is retained separately. New analysis C exists outside the canonical delivered component inventory and is not confused with the six delivered files above.

## Git visibility and limits

All six new source/header files return git check-ignore status1: not ignored. Their directory remains untracked, so a tracked-only browser can omit them. .gitignore line15 build/ hides offline ELF/build receipts; this is the actual visibility distinction. No configured core.excludesfile, .git/info/exclude file, or nested g2/components ignore was found. One documented Git worktree; HEAD remains9d6b94bdd. Shared offline ELF remains129a6b2f38f145f33e791874f52d722fb1715d5fff5c957a285644312f34a6f9. Git status before scan outputs:6205 staged additions,25 staged modifications,4 added-and-modified,799 individually enumerated untracked paths. These span unrelated campaign work and are not firmware progress counts.

There is real additional C reconstruction and executable validation evidence. Whole-firmware source completeness, byte-identical official OTA rebuilding, physical scheduling/peripherals/ROM behavior and hardware safety remain unproved. The isolated three-slot images are offline validation layouts, not deployable Apollo firmware.

Next concrete step is finishing the222 candidate’s remaining five integration cases and affected regressions/relink before treating it as a completed checkpoint. Preserve the validated220 predecessor and separate synthetic scheduling limits.
