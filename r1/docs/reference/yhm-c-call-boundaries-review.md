# YHM native helper boundaries preserved in C compilation

The R1 YHM transport acquire, release and completion helpers now carry noinline
attributes. These are the only source changes: request policy, volatile state
accesses, signatures and returned words are unchanged. Stock read/write routines
call those helpers as distinct native entries; the previous C compiler inlined
them into larger transaction bodies.

The new relocatable objects explicitly call release and acquire with Thumb call
relocations, then tail-branch to completion. Both transaction bodies shrink from
80 to 56 bytes under the normal profile. An executable-section audit confirms
that all six other transport functions, including the accepted byte providers,
retain identical section bytes. No new assembly or alternate implementation is
introduced. The attributes preserve the stock C call graph and make future
compiler/placement comparison more direct; smaller size alone is not byte proof.

All 13,848 paired stock/C regression cases pass: transactions 7,680, public write
3,840, completion 1,152 and callback management 1,176. These execute actual native/C
lifecycle, registry and completion code while modeling external device methods
and final callback targets. They retain the scopes and limitations of their
[transaction](yhm-c-transactions-review.md),
[completion](yhm-c-completion-review.md) and
[callback](yhm-c-callback-registration-review.md) reviews.

Official qualification compiles all five Clang and four supported GCC 9 profiles.
It rediscovers only existing accepted providers; no additional span qualifies.
The canonical source plan is unchanged. A fresh full hybrid build with that
plan and the changed C source succeeds and remains byte-for-byte equal to the
locked 646,408-byte application, SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Source-built accounting stays 3,821 bytes, resources 248 and unclassified binary
pull-through 642,339. Source completeness remains explicitly false.

The normal report `build/sources-goal-r1-yhm-boundaries/report.json` compiles all
571 R1 units without failures or duplicate strong symbols. Both import sets
remain unchanged: 197 application and 34 bootloader. `make sources-check` passes.
[Machine evidence](yhm-c-call-boundaries-review.json) binds exact source delta,
section/relocation audit, regressions, qualifications, normal build and hybrid
output. The hybrid is `build/hybrid-goal-r1-yhm-boundaries`.

Private frames/caller-clobbered registers/flags, concrete callback behavior,
concurrency, electrical bus/IRQ operation, complete source-only linking/byte
coverage and G2 corpus gates remain outstanding.
