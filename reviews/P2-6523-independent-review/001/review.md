# Independent review 6523

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet files and source span 0x43057C..0x430610 hash-match the pinned image. GNU Thumb decoding confirms the unsigned index guard (`R4 >= 8`), fresh table/handle reads, and per-entry stride of 16. The handle-create call is stored and reloaded; a zero result routes to return status 1, while D92C child failures route to the same return. The full-scan C63A result is ignored, followed by the 0x430470 call, then a fresh global handle create/store/guard and diagnostic branch. The diagnostic stack arguments occupy SP+0 and SP+4 and overwrite saved R2/R3; POP returns R1 from SP+0, R2 from SP+4, and restores R4-R6/PC.

The R6 return caveat is supported: R6 is loaded with the handle-table base before the new-handle attempt and can remain that value on a path reaching the shared return without the later assignment to 1. The status-1 failure branches bypass that common return. No additional result normalization is shown.

This review covers only the packet body and pinned inputs. It does not assign external child semantics or admit canonical coverage. No canonical files or gates changed.
