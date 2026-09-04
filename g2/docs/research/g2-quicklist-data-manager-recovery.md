# G2 Quicklist data-manager recovery

The authenticated G2 Apollo image contains three Quicklist storage functions
at `[0x0058D51C,0x0058D668)`, `[0x0058D668,0x0058D9C0)`, and
`[0x0058DA28,0x0058DACA)`. The object has four direct external entry sites,
no stored entry pointers, no strict interior ingress, and a 1,480-byte physical
envelope. Its retained path is
`app\\gui\\quicklist\\quicklist_data_manager.c`.

The clean-room implementation defines the exact 232-byte input and resident
record layouts and the 0x1238-byte state layout. It implements bounded record
copying, 200-byte text truncation and termination, 20-record capacity checks,
packet reset/continuation behavior, validity marking, completion status, and
the existing epoch-time seam. Native tests exercise successful initialization,
multi-record assembly, overflow, null arguments, and truncation.

The three stock entries are replaced by complete-span guarded branches to
separately compiled C leaves in both supported toolchain profiles. This is a
software closure. No hardware operation is needed to establish the record
state machine; end-to-end UI and device qualification remain blocked by
unavailable physical evidence.
