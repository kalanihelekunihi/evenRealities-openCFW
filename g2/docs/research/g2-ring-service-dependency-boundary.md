# G2 Ring service dependency boundary

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Status: production-routed clean-room C with hardware validation blocked by
unavailable authorized physical evidence.

The object `[0x00472244,0x00472C7C)` contains eighteen functions / 2,412 body
bytes / 2,616 physical bytes. Twenty-seven direct entries and two stored
function pointers close ingress. Its 121 external calls resolve to 76 admitted
EasyLogger, two exact CMSIS-FreeRTOS tick, eight bounded IAR, one admitted
nanopb, zero Packetcraft Cordio, and 34 first-party calls. The five targets
previously grouped as Cordio are retained-path-identified input-manager,
thread-ring, and device-manager policy plus adjacent first-party helpers. It
embeds no vendor body and adds no version or producing-commit discriminator.
Ring state and product policy remain first-party work.

The eighteen recovered functions now compile from selector-isolated
`components/apollo_main/core_overlay/ring_service.c`. Eighteen guarded `B.W`
redirects replace all 2,412 authenticated stock body bytes with 952 compiled
Thumb bytes plus eighteen generated alignment bytes. Thirty-eight strict
relocations terminate at reviewed source-owned seams or redirected sibling
entries. The authenticated 204-byte tail pool remains stock; the closure
analyzer's 216-byte outer-pool measurement also includes the twelve-byte
non-instruction gap inside the first replacement span.

The source implements heartbeat, touch-report timing and enablement, status
and pair frames, thread message/event wrappers, owner and touch-error callbacks,
PHY requests, HID command validation, bounded touch update/deduplication,
battery reports, wear lifecycle/duration reports, and command dispatch for
`0x61`, `0x85`, `0x8a`, `0x8b`, `0x8c`, `0x94`, and `0x96`. Host oracles and
strict Cortex-M55 selector builds cover all eighteen leaves.

The production aggregate is 255,686 overlay bytes, 3,779,082 component bytes,
and 4,557,576 package bytes with SHA-256 values
`2def566dbf70594c89471066a7cd17f6d1fa94196f65ff48237385396e9cfd19`,
`7228edb650fe39bda63480691fe94ed59d0807ca5e30846d35ec08e134e08350`,
and `c146ea7977a5521aa1df24a1a285768d7e2396fab96f117315a5baa2dcb65998`.
The 2,879,088-byte deployment plan has 4,057 placed regions, two explicitly
unresolved physical-evidence regions, five container-only regions, and six
partitions; its SHA-256 is
`80d2f655555786d495d9df72b85013dee8e0076554b0d2deb82159a5c876e292`.

No hardware was accessed. The authorized right temple is nonresponsive, the
authorized left temple must remain stock, and no responsive authorized pair or
golden Ring transport capture is available. Paired-G2 transport, callback
timing, live touch/wear/battery behavior, and peer interoperability therefore
remain explicitly hardware-blocked. This closes the service object's software
gap only; `thread_ring.c` and wider firmware gaps remain open.

Reproduce with `make ring-service-closure`.
