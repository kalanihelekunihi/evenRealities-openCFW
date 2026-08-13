# Google liblc3 v1.1.3 source snapshot

This directory contains a byte-identical source snapshot of Google's
Apache-2.0 `liblc3` at tagged commit
`96a3af0beb5487aca3b98a4b992a539a1f6d80d1` (`v1.1.3`). It includes the
complete public/internal headers, implementation sources, generated coefficient
tables, root build metadata, README, and license.

The G2 stock image calls the public `lc3_frame_samples`, `lc3_frame_bytes`,
`lc3_setup_encoder`, and `lc3_encode` surfaces from
`platform\audio\service_audio.c`. Its encoder core, field layout, constants,
and downstream algorithm graph match this implementation family.

The source boundary is narrower than an exact private-checkout claim. Stock's
`FLT_MAX` SNS quantizer proves commit `bb85f7d…` or later. It excludes
`9f1e206…`, which inserts `ltpf_bypass` ahead of the encoder's `dt`, `sr`, and
`sr_pcm` bytes and changes analysis behavior. The only C change between tagged
`v1.1.3` and intermediate successor `1de85e2…` fixes the spelling of the
dead-stripped `lc3_frame_block_bytes` definition. Consequently the linked
binary cannot distinguish those two public states. This snapshot selects the
official tagged baseline; it does not assert that Even's private checkout was
that Git object.

Run `python3 verify_snapshot.py` to authenticate all selected bytes and the
version discriminators. Production integration remains separate: an OpenCFW
audio pipeline must review build flags, target floating-point behavior,
performance, buffer ownership, and LC3 interoperability before routing audio
through this source.
