# Closed paths and next dependencies

217-object successor changes two installed bindings: revision-specific PCM2.1 +0x2c -> pcm21_boost_service, and initialized transition slot6 -> opencfw_spot_pcm22_transition6. Selector mask is 0x707c14f. The prior215 image already installed the PCM2.2 power updater; do not count it twice.

PCM2.1 boost (0x42ae9c..0x42aeec) runs critical-save -> trim restore -> optional switching control bits -> timer stop -> profile trim -> PRIMASK restore. It clears the switching flag and returns saved PRIMASK. The void outer wrapper must not interpret R0 as callback status.

PCM2.2 selector6 (0x428840..0x42891e) packs four low-voltage trim bytes, saves target VDDF/LDO, conditionally polls timer-ready and services the timer, updates cached TON/target/trim fields, writes VDDF and calls TON adjustment. The original reads some target fields before timer service and others afterward; this ordering is retained. Ready polling is bounded at60 calls to the delay helper with argument1; physical elapsed time is not established by synthetic readiness tests. The unavailable resident ROM delay40 implementation remains an explicit stub.

The installed updater fixture now reaches selectors0,2,3,6,24 with no callback return substitute. 17 valid fixtures cover550/758 updater bytes. The wider151-case oracle covers756/758 bytes but cuts unsupported callbacks; it is separate evidence. The two unvisited bytes at0x42aa1e are the default branch after classifier bucket tests0..4; not exercised, not silently marked covered.

Priority1: close source FP comparison controls/IOC/IDC semantics and validate across scalar QEMU and original-instruction fixtures. Preserve all mismatches; no FPSCR normalization. Priority2: select next actually reached unsupported transition (4/5/7 or9..13 etc), close its helper dependencies, then add an installed-call fixture and independently tested source. A mask increase alone is not completion.

No source-complete, whole-OTA-byte equality, ROM recovery, hardware transition or deployable address-layout conclusion follows from this checkpoint.
