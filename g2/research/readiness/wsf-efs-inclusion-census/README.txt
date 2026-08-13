OpenCFW Lorelei Cordio wsf_efs.c inclusion census

Conclusion
----------
No defensible linked entry was found. The evidence favors `not linked / garbage-collected` for Cordio wsf_efs.c in the authenticated G2 image, so a broad compiler matrix was intentionally not started.

Source and consumer topology
----------------------------
AmbiqSuite 2.5.1 wsf_efs.c is 19,876 bytes, SHA-256 878125a6bb701d0875d58c05bfcb4ad770c9f95f8c09f69706959795bee7741a. AmbiqSuite 2.4.2 is byte-identical. An archive-wide source census found external WsfEfs API consumers only in wdxs_main.c, wdxs_ft.c, and wdxs_stream.c. The stock image has no wsf_efs.c/WsfEfs/wsfEfs markers, no WDXS markers, and none of the four exact WDX characteristic UUIDs. G2's numerous textual `EFS` markers belong to its separate Even File Service over LittleFS and are not Cordio Embedded File System evidence.

Structural probe
----------------
Three profiles (O1, O3, Os with sibling calls disabled) compiled all 17 public APIs in parallel, producing 51 function rows. All three closure ELFs linked with zero undefined symbols; only memcpy and memset were source-module imports. Parallel wall time was 1049263486 ns. No complete candidate function byte sequence occurred in stock.

A Thumb semantic census covered the authenticated executable/Cordio corpus at stock file offsets [0x40000,0x136000). Thirty deliberately broad partial hits were triaged. None combined handle bound 6, the 52-byte wsfEfsControl_t stride, and multiplication; none had WsfEfsInit's six 52-byte-spaced invalid-size stores. The only two multiply-plus-minus-one hits, 0x00507426 and 0x0050744C, use a 48-byte stride and unrelated control constants. Thus no candidate survives as an entry.

Limitations and recommendation
------------------------------
Absence cannot prove bytes do not exist under arbitrary downstream rewriting, and the generic `Unknown` fallback string occurs six times elsewhere. However, the missing sole consumer family and UUID service data, zero source/name markers, zero raw candidates, and zero complete semantic fingerprints make inclusion unlikely. Record this module as `upstream available, stock inclusion not evidenced / likely dead-stripped`; do not assign addresses or run the 13-profile matrix unless WDXS call/pointer evidence appears later.
