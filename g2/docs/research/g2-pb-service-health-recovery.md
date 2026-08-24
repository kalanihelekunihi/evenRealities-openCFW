# G2 `pb_service_health.c` recovery

Status: complete linked-object census, clean-room production implementation,
and fail-closed route verification. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

Eight exact-named functions and five owned alignment/literal regions occupy
`[0x0055A558,0x0055B2A4)`. The bodies contribute 3,092 bytes with SHA-256
`13f8aad04ac998d93e5ce8c836cdbaa7633fbe0ab128a9a6395e2fe7665bb6dc`;
the 312 gap/pool bytes have SHA-256
`c2d3d3d79212fe12b139f420b07a3ad907f1ae391290b68a9a1ee0177d289d87`.
The complete 3,404-byte object has SHA-256
`9020db98fd11e16ce082853f8556a94795330c4f1f178ab6765685c1438ff1ab`.
An unrelated Thumb function begins at `0x0055B2A4`.

The seven original corpus anchors omit `PB_RxHealthMultHighlight`. Its real
body is `[0x0055AF14,0x0055B058)`: a valid Thumb prologue-to-return region,
called at its exact start, followed by the next source-order transmit body,
and named by its own retained assertion record. Promoting it produces the
complete alternating RX/TX inventory: single data, multiple data, single
highlight, and multiple highlight. Eight exterior calls enter the eight exact
starts and the bodies contain 180 calls. Direct and `B.W` strict-interior
ingress are zero. The sole all-byte address collision at `0x00643337` is an
unaligned instruction/data window encoding `0x0055B1FF`, not a stored entry
pointer.

## Message behavior

All four receive wrappers return 2 for null input, zero when their matching
health-data-manager helper succeeds, and 1 when it fails. Their helper calls
are pinned at `0x0055A656`, `0x0055A960`, `0x0055ACA2`, and `0x0055AFBC`.

The four transmit wrappers reject null input with 2, clear the shared
0x31C-byte message at `0x200F5DC4`, encode into the 256-byte buffer at
`0x2037C6A0`, and transmit on route 1 / service `0x0E`. They return zero on
success and `0x2B` on nanopb encoding failure. The envelopes are:

- command 1 / tag 3: single health data, carrying data type, goal, current
  value, average, duration, and trend;
- command 2 / tag 4: multiple health-data samples;
- command 3 / tag 5: a single highlight;
- command 4 / tag 6: multiple highlights.

The multi-highlight encoder reads a 16-bit count and expands each compact
input record into its nanopb output stride. No independent count bound is
visible in stock. Production closes that unsafe precondition by rejecting more
than three records with the existing encode-failure status; three is the exact
capacity of the retained `0x31C`-byte message layout.

Eight 20-byte assertion records at `[0x00781E80,0x00781F20)` pin the retained
path, all eight function names, and source lines 109, 132, 213, 237, 313,
336, 374, and 398. The historical source tree and license remain unavailable,
so source-only functions are not inferred.

Production now routes the eight stock entries plus one bounded source-owned
nanopb buffer callback. The nine leaves contribute 940 compiled Thumb bytes
and eight alignment bytes; eight full-span redirects replace all 3,092 stock
body bytes while retaining the authenticated descriptor/assertion pools.
Twenty strict relocations terminate at the already source-owned health-data
manager, generic message encoder, BLE protobuf sender, or the new callback.
Host tests exercise all status/envelope paths and the count safety correction.

Canonical Apple overlay/component/package identities are 184,522 / 3,707,918
/ 4,486,412 bytes with SHA-256 `f2e2771d...6a43`, `a2c628bb...aafc`, and
`34e82939...8936`. Software behavior and complete-image generation are
closed. Live service scheduling, BLE delivery, phone/schema interoperability,
and persisted device-data validation remain blocked by unavailable authorized
G2/EM9305 physical evidence. The next retained protobuf-service frontier is
`pb_service_setting.c`; firmware-wide completeness is not claimed.
