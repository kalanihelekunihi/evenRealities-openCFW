# AmbiqSuite ANCC profile source oracle

This directory admits the exact AmbiqSuite 2.5.1 Apple Notification Center
Service client source and header as a provenance and implementation oracle for
G2's retained `platform\\ble\\profiles\\ancc\\profile_ancc.c` object.

The stock object is not a pristine build of this file. It preserves the
distinctive Ambiq implementation—64 reverse-popped notification slots, the
19-byte eight-attribute request, the 512-byte fragmented parser, five-handle
128-bit service discovery, and the same command encoders—while adding G2
message dispatch, synchronization, whitelist policy, callbacks, and logging.
The source is admitted as an oracle and is not routed into production.

The implementation body is byte-identical across authenticated public
AmbiqSuite 2.2.0, 2.3.2, 2.4.2, and 2.5.1 imports and is independently present
in later 4.3.0 and 4.5.0 package copies. Consequently, this module identifies
its Ambiq origin but cannot reveal the private G2 generating commit. We select
2.5.1 because OpenCFW already authenticates the official 2.5.1 archive and the
public Git import is reproducible.

Both admitted files retain Ambiq's complete BSD-3-Clause-style per-file license
notice. Run `python3 verify_snapshot.py` to authenticate the snapshot.
