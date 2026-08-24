# G2 health data-manager dependency boundary

The five retained-path anchors / 1,848 bytes expand to ten functions / 2,644
body bytes for `health_data_manager.c`. The complete physical object is
`[0x005597F0,0x0055A350)`, 2,912 bytes. One source-order parser missed by
Ghidra completes health-record validation, bounded aggregation, lookup, and
shared-storage update behavior. The endpoint is the hidden protobuf-health
dispatcher that begins the adjacent already closed service object.

The closure records 976 reachable instructions, 149 direct calls, eighteen
whole-image BL entry sites, no stored function pointer, no indirect call, and
no strict-interior ingress. All 136 external calls terminate at admitted
EasyLogger (120), bounded IAR/runtime memory primitives (6), or the already
closed first-party health mutex acquire/release wrappers (10). Those wrappers
in turn use exact source-owned CMSIS-FreeRTOS v10.5.1 mutex APIs; this object
has zero direct CMSIS-FreeRTOS or FreeRTOS edge.

No reusable calculation, DSP implementation, or new version discriminator is
embedded. The historical first-party producing commit remains unobservable.

The clean-room production implementation now owns all ten linked entries. It
recreates the exact type/slot map, retained type-name ABI, 1,488-byte manager
storage reset, 24-byte protobuf record conversion, single and counted record
saves, 257-byte highlight conversion, bounded five-highlight capacity, and the
stock null/type/capacity return policy. Host tests cover those behaviors and a
strict Thumb gate exposes exactly the ten reviewed entries.

Ten authenticated full-span redirects replace all 2,644 stock body bytes with
1,012 compiled Thumb bytes plus ten alignment bytes. Fifteen strict external
relocations bind only to earlier source-owned health lock/unlock and manager
leaves. Canonical Apple overlay/component/package identities are 183,574 /
3,706,970 / 4,485,464 bytes with SHA-256 `c3f1e141...92947`,
`f453571d...ef32d`, and `37a5607c...3b001`. Software routing and image
generation are closed. Live mutex scheduling, concurrent service traffic,
persistent health-schema interoperability, and display/device-data behavior
remain explicitly blocked because no authorized physical G2/EM9305 evidence
is available; no hardware validation or firmware-wide completeness is claimed.
