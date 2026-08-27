# G2 bootloader EasyLogger control source closure

The authenticated G2 S200 bootloader span `[0x0041733C,0x004176CE)` contains ten complete EasyLogger control entries. Their 914 stock bytes are replaced by ten strict source redirects backed by `runtime_easylogger_control_41733c.c`, an MIT adaptation of EasyLogger commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` with the recovered G2 logger-state ABI and absolute port seams.

The maintained C covers initialization/idempotence, startup, output and color enables, per-level format configuration, global filter level, lock/unlock transition bookkeeping, tag-level reset, and tag-level lookup. The host fixture exercises initialization, setters/assert metadata, lock transitions, and tag filtering. The Cortex-M55 build pins every function body and every retained relocation under Apple Clang 21 and Linux Clang 22.

Production evidence:

- source: 15,772 bytes, SHA-256 `d3fd7593a5d80a952bd6ce92f20897c45291afcd00d8ce0c0a6e5028d3e8dd24`;
- stock span: 914 bytes across ten authenticated functions;
- exact test: `tests/test_runtime_bootloader_easylogger_control_41733c_4176ce.py`;
- production config: `components/bootloader/core_overlay/overlay.json`.

No device, debugger, serial endpoint, signer, flasher, reset, or boot operation was used. Live mutex, scheduling, transport, and logging validation remains blocked by unavailable authorized responsive G2 hardware.
