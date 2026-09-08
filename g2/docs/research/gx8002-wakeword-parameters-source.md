# Wakeword parameter source reconstruction

Two writable parameter records are defined as C initializers using the exact
`LVP_KWS_PARAM` type extracted from authenticated NationalChip commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`, `include/lvp_param.h`.
The type retains its conditional fields; the recovered build leaves cascade,
hybrid and level-decoder fields disabled. Size and every field offset have
compile-time assertions. The native macOS compiler reproduces all 176 stock
bytes, including unused string and label slots, without binary-derived source
arrays. Stock is used only for comparison.

The records describe hey_even (threshold567, event100) and hi_even
(threshold460, event101), both major keywords. Both have two label indices54;
the vocabulary meaning of that index and neural-model weights remain separate
work. This reconstructs the parameter representation, not the full model.

The next reset/init candidate also defines the 164-byte activation BSS object
in C, at its recovered linker address. Its functions reproduce the original
20- and8-byte payloads. It is not yet admitted: reset's retained memset service
and nested-call/clear-range behavior need qualification. The memset lineage is
now identified as a zextb instruction followed by the pinned SDK's158-byte
fast implementation, which is only a comparison oracle for future C recovery.

Integration passed314 tests. The native macOS package rebuilt and passed
artifact verification with the parameter header notice included. The table's
176 bytes now have source ownership; codec and package hashes are unchanged
because the typed definitions reproduce the former retained bytes exactly.
Reset/init remains a separate candidate. The full source-only goal is active.
