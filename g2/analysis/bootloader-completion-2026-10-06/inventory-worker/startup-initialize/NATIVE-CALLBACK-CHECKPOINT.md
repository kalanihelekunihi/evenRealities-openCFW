# Native callback prerequisite checkpoint

**Final validated candidate75ee: all7 integration cases,31 affected regressions and400 native dispatcher comparisons PASS.687 frozen inputs/177 objects reconcile. Candidate remains unpromoted; production c6a3 is preserved.**

The promoted integrated image remains c6a3; the following are standalone prerequisites, not a new promoted integrated image.

- `startup_spot_handlers.c`: four compiled initialization callbacks replace raw-target invocation in the standalone `dispatch_native.c` candidate. Native dispatch comparison passes 400 fixtures across revisions 32..36, trim variants 0/1/2/3/ffffffff, patch-bit branches, OTP-selected/ready branches and ROM response words 0/ffffffff. The source machine loads only compiled source ELF segments. Four init callbacks, timer helper and INFO selector/dispatcher/thunk execute natively; only absent resident ROM48 is controlled. Compare ordered MMIO, status, 108-byte profile, flags, logical callback table (relocated source slot0 normalized to locked address) and cache. No SRAM-write hooks.
- `startup_ton_gate.c`: exact 41c838..41c860 (40 bytes), 112 direct original-instruction comparisons PASS. Writes bit16, bit0, then bit5 of 40020060 from argument bit0 in three separate read-modify-writes; returns uint8 argument. All body instructions visited.
- `verify_ton_native.py`: 124 TON hook comparisons PASS with the new gate native on both sides. Only delay is cut; source machine has no stock executable bytes and loads nine authenticated table data bytes at433f20. Existing 22-byte conditional-arm gap remains explicit.

These results remove four initializer callback body substitutes and the TON gate substitute from their respective standalone suites. They do not close the remaining SPOT event/hook callback frontier or initializer clock-mux register-carry dependencies. The main startup selected boundary41c4b4 remains unbound. No hardware, timing/drain, source-completeness or byte-identical claim.

Receipts: [dispatch](dispatch-native-comparison.json), [TON gate](ton-gate-comparison.json), [TON native hook chain](ton-native-comparison.json). Exact inputs and linked ELFs are preserved under `g2/build/bootloader-completion/startup-native-callback-analysis/input-hashes.json` with actual frozen copies. The build directory is ignored intentionally; readable source and receipts are outside it. No commits or campaign-state edits.

The400-case native chain visits dispatcher668/668, callbacks142/146+346/350+196/222+4/4 andtimer68/68 original bytes. The separate19-case callback suite remains the all722-byte coverage supplement;400 is not a claim of complete branch coverage by itself.

A temporary negative control changing gate bit5 to bit4 is rejected at seed0 / arg1: stock third write65569 versus mutant65553. The full unpromoted candidate75ee0b6b29683b59bf8b20035aedad25b4f347ea3c53df56bde04f11f5f9d900 also passes native dispatch400 and31 affected regression receipts. Its687 source/test inputs and177 objects are preserved as actual frozen copies under the matching snapshot. All7 integration cases remain pending as of this append; c6a3 remains promoted.

Normal integration2/2 and malformed integration3/3 now PASS on the same75ee candidate. The synthetic interruption/reboot pair is still running. The source/test/object hashes rechecked unchanged after31 regressions.

Final: all7 integration cases PASS on75ee, plus31 affected regressions and400 native dispatcher comparisons;687 inputs/177 objects and actual frozen copies recheck unchanged. [Exact receipt](../../integrated-status/same-image-validation-native-callback-75ee.json). The earlier pending statements above are preserved chronology; this final paragraph supersedes them. This is a validated unpromoted candidate; c6a3 production build remains unchanged.
