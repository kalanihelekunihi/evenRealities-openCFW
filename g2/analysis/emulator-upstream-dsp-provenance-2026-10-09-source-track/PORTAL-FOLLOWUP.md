# Official portal follow-up and deduplication

The supported in-app browser loaded the exact official sharing link and displayed NationalChip branding with `链接已失效 该链接已被取消或超过有效期`: link invalid, cancelled or expired. This is the actual current availability boundary, superseding the earlier shell-only uncertainty. No login or agreement was encountered, no account was created, and no access block was bypassed. The portal does not expose a downloadable archive or hash in this state. Contacting the sender is suggested by the portal; no contact was made.

Deduplication against the owner evidence found an already acquired exact-name candidate:
`g2/analysis/bootloader-completion-2026-10-06/upstream-worker/downloaded-sdks/csky-elfabiv2-tools-x86_64-minilibc-20190929.tar.gz`.
Independent read-only hashing confirms 105,910,950 bytes and SHA-256 `df33d1e101d9b0c1d4cc68286bb97a98e3a3095cf321f9e253f0ddf805d8d9f9`, matching SDK-INSPECTION.md. Thus no new duplicate archive was downloaded or copied. The existing report records enclosing distribution V3.10.15, GCC 6.3.0 and a matching Readme MD5. The official document identifies the same distribution/filename, but the expired portal cannot bind its former bytes to the local archive.

Static tar enumeration found no regular-file member whose basename contains COPYING, LICENSE or EULA. SDK-INSPECTION.md likewise records no standalone EULA in the supplied Readme. This does not establish absence of licenses embedded in manuals or program source; it means the bundle-wide and per-component license inventory remains unresolved. GCC provenance alone does not license every bundled debugger, runtime or vendor component. No unverified compiler executable or installer was run.

Machine-readable verification: PORTAL-DEDUP-VERIFICATION.json. The existing archive and owner evidence remain unchanged.

## Why Pigweed registration remains a proposal

A Git submodule registration requires changing `.gitmodules` plus a root-index gitlink. The explicit source-track delegation says: “Write only your own new ... directory and isolated new downloads” and “do not change .gitmodules or root Git index.” Those limits apply even though a targeted git add could technically avoid unrelated staged files. Concurrent staged R1 work is an additional reason for careful ownership, not a claim that selective staging is impossible. The result is therefore an exact URL/path/pin proposal in REPORT.md, not a completed registration. The pinned Apache-2.0 schemas are already acquired and usable as provenance references without that mutation. The owner can register the proposed module under a separately authorized scope.
