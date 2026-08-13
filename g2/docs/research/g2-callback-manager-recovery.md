# G2 generic callback-manager recovery

The retained `platform\service\callback_mgr\callback_manager.c` object closes
as eight functions / 1,240 body bytes inside the 1,360-byte physical interval
`[0x005100A0,0x005105F0)`. Four path-anchored bodies expand with node deletion,
deinitialization, membership testing, and notification. Ghidra found seven of
eight; the 106-byte `CALLBACK_MGR_Deinit` body is restored from raw source
order. A 118-byte literal pool before notify and two-byte trailing alignment
account for all noncode bytes.

The manager stores a head pointer, byte-sized callback count, and caller-owned
type string. Register treats an existing callback as success; otherwise it
allocates and prepends an eight-byte function/next node. Unregister handles
head and interior deletion. Deinit frees the complete list. Notify walks only
registered nodes and uses the object's sole dynamic call site to invoke each
non-null callback with two arguments.

All 72 external direct calls terminate at 70 already admitted EasyLogger
operations and the two production-source-owned synchronized heap wrappers over
the admitted TLSF interval. There is no direct CMSIS-FreeRTOS call and no
embedded third-party definition. Exact public searches for retained symbols
and diagnostics returned no source candidate, so no new version discriminator
or private generating commit is recoverable. The object is not yet
production-routed, but its complete ABI now closes the provider behind the
BLE-status, charge, message-count, and ring-battery facades.
