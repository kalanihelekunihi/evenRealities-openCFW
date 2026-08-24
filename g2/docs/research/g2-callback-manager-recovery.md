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

All 72 stock external direct calls terminate at 70 admitted EasyLogger
operations and the two production-source-owned synchronized heap wrappers over
the admitted TLSF interval. There is no direct CMSIS-FreeRTOS call and no
embedded third-party definition. Exact public searches for retained symbols
and diagnostics returned no source candidate, so no new version discriminator
or private generating commit is recoverable.

## Production source closure

`components/apollo_main/core_overlay/callback_manager.c` now supplies all eight
functions as selector-isolated freestanding Thumb C. The canonical Apple build
adds 408 compiled text bytes plus 14 alignment bytes with six strict
relocations. Allocation/free bind to the already source-owned synchronized
heap wrappers; internal manager calls bind through the eight exact stock-entry
redirects. Those redirects replace all 1,240 stock function bytes while the
118-byte diagnostic literal pool remains authenticated compatibility data.

Host coverage exercises null validation, allocation failure, duplicate-success
semantics, prepend ordering, head/interior removal, complete deinitialization,
and ordered two-argument dispatch. EasyLogger calls remain omitted as
non-controlling observability. The canonical artifacts are overlay
`a4c7927efe625a95e3bd928e5bb75b32c057837577dd9b9bf0cc3a5c19a42183`,
Apollo component
`026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a`,
complete package
`03d4b3f7813ce41814ae821ccbdaa3a1f2802fe4a459cf20351487a18332e783`,
and flash plan
`ef7a204c200024422defd2cb9e0064a5aa4278bb14533e4007bd0daf2db1e67f`.
This pure in-memory manager has no hardware-dependent validation tail, so its
software functional gap is closed without a physical-evidence blocker.
