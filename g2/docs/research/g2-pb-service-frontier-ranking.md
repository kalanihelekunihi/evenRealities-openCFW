# G2 `pb_service_*` reconstruction frontier

Status: authenticated retained-path/linked-body ranking; the first six
selected translation units are closed and the remaining queue is active.

The stock image retains 15 first-party `platform\protocols\pb_service_*`
paths. Correlation against the authenticated 64-shard corpus associates 119
discovered bodies / 40,844 body bytes with those paths. The ranking is a
tractability guide: a retained path is positive ownership evidence, but its
anchors are only a lower bound on a translation unit and pathless functions
may still exist.

The smallest anchored target is `pb_service_translate.c`: four bodies and
1,324 body bytes spanning the lower-bound interval
`[0x0059F53C,0x0059FA68)`. It is now fully bounded through its pool at
`0x0059FAE0`; see `g2-pb-service-translate-recovery.md`.
`pb_service_glasses_case.c` follows at 1,360 bytes and is now fully bounded
through its pool at `0x00510FD8`; see
`g2-pb-service-glasses-case-recovery.md`. `pb_service_ring.c` follows at
1,362 bytes and is now fully bounded through `0x005CE7C4`; see
`g2-pb-service-ring-recovery.md`. The next target is
`pb_service_conversate.c` at six anchors / 1,776 bytes; it is now fully
bounded through `0x005B22BC`, as documented in
`g2-pb-service-conversate-recovery.md`. Teleprompt follows at seven anchors /
1,854 bytes and is now fully bounded through `0x00588D74`; see
`g2-pb-service-teleprompt-recovery.md`. The exact 15-row census, path strings,
pointer-cell counts, boundaries, and ranking are pinned in
`tools/manifests/g2-pb-service-frontier.tsv` and reproduced by
`tools/analyze_g2_pb_service_frontier.py`.

This ranking does not assign production ownership. The intervening
`pb_service_even_ai.c` lower bound expanded to 25 functions / 8,956 physical
bytes and is closed in `g2-pb-service-even-ai-recovery.md`. Terminal expanded
to 13 functions / 2,800 physical bytes and is closed in
`g2-pb-service-terminal-recovery.md`. Device configuration is closed as three
functions / 2,932 physical bytes in
`g2-pb-service-dev-config-recovery.md`. The next fail-closed source-order,
pool, ingress, and message-ABI target is `pb_service_health.c`.
