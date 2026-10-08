# Native idle/sleep reconstruction component copies

These isolated sources compile byte-for-byte to the six frozen object inputs of the separate214-object `badad5a92beec12dd1f5389033d51db87aa8d5bb77cb3410a7e465f2aa649b57` candidate. See `g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/idle-native-integrated/REPORT.md` and `component-copy-validation.json` for evidence.

Existing parent build recipes and `thread_creation/scheduler_bootstrap.c` are preserved. This directory's scheduler_bootstrap installs native `idle_entry` through a compiler pointer; it is an alternative bootstrap, not an additional definition to link alongside the old bootstrap. The owned candidate linker supplies cleanup/reschedule/suspend/resume, buck override and delay providers. Power-state and boost calls remain controlled original-address contracts in this214-object candidate. Generic helper names are local reconstruction interfaces, not a public app ABI.

The candidate uses a third offline64KiB code slot and is not a deployable Apollo memory layout. Timer registers, kernel addresses and profile fields are locked-image-specific. Counter values are STIMER counts; scheduler values are ticks. No assumed milliseconds, real wake timing, concurrent scheduler proof or complete-source/byte-identical bundle claim.
