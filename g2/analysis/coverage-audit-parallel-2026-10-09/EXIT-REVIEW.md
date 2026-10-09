# Newlib exit independent review

The40-byte exit comparator passes. [Verification](EXIT-VERIFICATION.json), [parser](exit_verify.py), [owner report](../touch-newlib14-startup-exit-2026-10-09/REPORT.md). No build/execution repeated.

All three exact-revision source acquisitions and actual consumed source/vendor inputs verify by hash. Compile/preprocessing/object hashes verify under the documented Cortex-M0+/Thumb/-Os/nano contract. License provenance reuses previously reviewed exact-pin newlib notices/COPYING.NEWLIB; mirror acquisition and generated installed headers do not establish the complete vendor source/build configuration.

The linked .text is exactly40stock bytes at[0xA9AC,0xA9D4), with both full hashes and input linker-script/object hashes verified. Nonrelocated source bytes remain identical. ELF symbol binding independently confirms undefined weak __call_exitprocs. GNU-link output at the weak-call field is00e000bf(branch plus NOP), and the actual original literal is0. Stock LDR0xA9ACreferences0xA9CC; LDR0xA9BCreferences0xA9D0, whose value0x20000F54is the stdio-handler slot. Original BL0xA9C8binds _exit0xAA40/Thumb0xAA41. No executable halt body or guessed handler contents are supplied. Exit ends exactly at the proven memset start; the historical54-byte row would overlap14memset bytes and remains preserved as historical evidence.

Source and local stock bytes support preserving the exit status, skipping the absent weak provider, conditionally invoking the loaded stdio callback, and passing status to _exit. This is a local static provider match, not executed cleanup composition. No real atexit procedures, live stdio-handler contents, callback effects, _exit source attribution or physical halt behavior are established. The provider's comments about standard stream cleanup do not prove this firmware performs that cleanup.

New distinct dependency increment40bytes; no54-entry census increment. The focused arithmetic/memory/exit provider subtotal becomes822bytes (unsigned/hook280+signed468+memcpy18+memset16+exit40); this is not the global dependency total.

Constructor remains open: independently reproduced37nonrelocated mismatches in its68-byte emitted comparison window. That window is not a promoted firmware extent. Source under consumed nano configuration omits _init; authentic archive/member and generated build-configuration evidence is the next static discriminator. Do not add a macro merely to fit target bytes. Halt0xAA40and init stub0xAA44still need genuine libgloss/crt/source contracts; actual initialization-array and stdio-handler contents/runtime invocation remain separate state evidence.

No canonical/admission/index/source/device change; only assigned audit outputs written.
