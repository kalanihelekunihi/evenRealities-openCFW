# G2 bootloader late-wrapper source closure

Six late bootloader services are now source-owned MIT C: a mode-one adapter, normalized boolean status route, validated byte-copy and word-transfer wrappers, the critical word-transfer dispatcher, and an unreferenced platform-service initializer. The initializer retains its authenticated stored entry pointer at `0x00433448`.

The audit also corrects the `0x00430B10` function extent from `0x00430B38` to `0x00430B3C`. The old boundary cut through the four-byte `MSR PRIMASK` instruction and incorrectly classified its trailing halfword plus the final `POP` as mixed data. The corrected function is 44 bytes and the following mixed interval begins at `0x00430B3C`.

Apple clang 21 and Homebrew clang 22 reproduce the authenticated 12-, 34-, 40-, 40-, 44-, and 62-byte bodies exactly from mnemonic-only source. Portable tests cover constant mode arguments, boolean normalization/status mapping, rounded word counts, and platform routing order. Live platform and interrupt-mask validation is blocked by unavailable physical evidence.
