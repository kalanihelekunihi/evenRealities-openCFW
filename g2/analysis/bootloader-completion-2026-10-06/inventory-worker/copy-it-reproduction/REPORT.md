# Independent copy instrumentation reproduction

Environment: existing analysis Python/Unicorn2.1.4, M33/M7/A9 models. No hardware, new tool installation, original instruction patch, expected-answer hook or compiler activation.

The previously observed aligned copy failure is caused by the memory-write instrumentation configuration in this environment, not established firmware behavior. Three independent experiments separate it:

1. Hand-assembled two conditional-load/store tails and caller MOVS0:24 combinations pass. A full aligned-copy loop/remainder/caller:48 combinations pass without SRAM write hooks.
2. Authentic26-byte config wrapper, copy-helper span and one literal only:24 model/alignment combinations copy the expected20 bytes and return0, both with/without instruction tracing. A stop-hook supplement also passes.
3. Add a no-op `UC_HOOK_MEM_WRITE` over SRAM: the original aligned return becomes20000090 on all three models; other alignments also show corruption. The independently assembled aligned loop reproduces the same effect for4/8/12/20/24/28-byte remainders, while16/32 pass. Removing only that hook restores correct behavior. All original failures remain in `write-hook-result.json`, `aligned-write-hook-result.json` and the older `../startup-config-leaves/native-copy-a9.json`.

The no-op hook has no intended semantic effect. This A/B difference supports an emulator instrumentation defect for these instruction sequences. It does not establish which internal Unicorn component is faulty, nor hardware behavior across arbitrary copy lengths.

The new clock fixture needs only MMIO writes, so it registers that recorder only over40000000..400fffff. It compares SRAM after execution and executes the actual stock copy helper. This preserves the recorder's required behavior and removes no requested SRAM write-stream measurement. No copied bytes or return values are substituted.

Native startup wrapper verification now passes271 cases, including null and all8 source alignments (`clock-config-e104/startup-leaves-native-copy.json`). A scoped adapter also executes original startup descriptor copy entry4156ac with64 passing orchestration cases; the nine child API models of that suite remain explicit. These are separate supplements; the old frozen runners and their copy-model limitations remain preserved.

Sources/reproduction: `repro.S`, `aligned.S`, `run.py`, `run_aligned.py`, `run_aligned_write_hook.py`, `raw_repro.py`, `raw_stop_hook.py`, `raw_write_hook.py`. Compile the independent assembly with clang Cortex-M7 Thumb and link at10000, then run its script. Raw repro authenticates the locked bootloader and loads only its stated ranges. The adapter is `verify_startup_native_copy.py`; it changes recorder scope, not firmware bytes.
