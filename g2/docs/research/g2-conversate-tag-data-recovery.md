# G2 conversate tag-data recovery

The nine retained-path anchors / 2,562 bytes expand to twelve functions /
2,726 body bytes / 2,876 physical bytes for `conversate_tag_data.c`. Three
restored helpers complete the tag-list allocation, insertion, deletion, and
lookup logic. The audit pins 1,043 instructions, 160 direct calls, eighteen
whole-image BL entries, no indirect calls, and no strict-interior ingress.

Despite owning structured tag data, the object has no nanopb, JSON, or other
serialization-library edge. All 155 external calls terminate at EasyLogger
(140), production-owned TLSF wrappers (8), or bounded IAR DLIB primitives (7).
It therefore reuses EasyLogger `a596b264…` and TLSF `deff9ab5…`, embeds no
third-party implementation, and adds no version discriminator. Remaining work
is first-party data-model recreation; the object is not production-routed.
