# Independent review 2563

**Result: PASS_SCOPED.**

Candidate `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-power-profile-init-original-reads-2562/001` binds to the pinned flash and decoded-ITCM images. Receipt, three candidate artifacts, image hashes and literal/body pins match. An isolated copy of the replay passed all six cases.

This composition runs the original initializer and its public/internal read, source-adjust, copy-wrapper and ITCM routines without intercepting firmware calls; only `0x41CC04` is controlled. Three guard states and two runtime callback returns check the guard-clear source at `0x42002000 + 4*(offset+640)`, the guard-set source at `0x42006000 + 4*offset`, exact read arguments, 20/5/1-word source-backed transfers, the complete 112-byte state image, dispatch installation, status and register/frame preservation.

Source buffers are deterministic fixture data, not authenticated factory contents. The read-error paths are not exercised in this packet; prior controlled-read evidence is separate. This does not prove physical source mapping or data, runtime callback effects, installation ownership, other profile branches, or behavior under concurrent changes. Private evidence only; accepted:false and no canonical admission.
