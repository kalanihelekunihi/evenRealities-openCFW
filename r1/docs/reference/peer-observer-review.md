# R1 peer-manager observer connection

`native_peer_observer.c` compiles the unchanged pinned SDK `peer_manager.c`
and exports its private BLE callback through the compiler alias
`r1_sdk_peer_manager_event`. The reconstructed observer table can now resolve
that provider. The wrapper suppresses the SDK's own registration macro for this
compilation unit: the existing reconstructed table owns the stock record, so
the linked source no longer emits a second copy of that eight-byte registration.
The compiler alias and macro scope do not add an executable adapter.

REA/Ghidra stock reads disambiguate entry `0x53924` from other SDK callbacks
sharing the generic name `ble_evt_handler`. Its record is the fifth entry of
the 40-byte priority-one table at `0xc4570`, at `0xc4590` with null context.
The test links and invokes the actual reconstructed table and SDK callback;
the other four records match stock at the test bindings. Fifteen other exported
SDK symbol routes now point at the wrapper's current object, retaining their
prior statuses and runtime evidence scope.

The production object passed 3,300 paired stock/C event scenarios. These cover
initialized/uninitialized state, connected and other event IDs, connection and
flag-ID boundaries, zero through three subscribers, changing subscriber count
and handler entries during dispatch, exclusion writes and both PRIMASK settings.
Checks include the 20-byte configuration event, its context flag, live subscriber
reloads, exclusion decisions, IM/SM/GCM forwarding order, state/event bytes,
callee restoration, SP and interrupt masks. The callback runs through the actual
table's peer record. Four negative controls reject duplicate observer inventory,
reversed forwarding, inverted exclusion and a cached subscriber count.

Stock startup handlers were executed to check initial flag ID 24, false
initialization state, zero subscriber count and the zeroed 12-byte handler array.
Source section sizes and initializer bytes match these values. Address placement
in the fixture does not establish a final source link.

This remains a bounded C candidate. Initialization booleans and callback writes
are restricted to canonical 0/1 values. Subscriber event/context pointers are
normalized after checking their contents and validity. Their native depths are
36/40 bytes below caller SP; C depths are 48/49. Subscriber frame depths are
64/56, and native GCM tail dispatch has no frame whereas C retains 56 bytes.
These differences prevent an exact-frame or byte-identity claim. Flag APIs,
clearing and IM/SM/GCM providers are modeled. Void callback returns, unrelated
caller-clobbered values, live callee registers, private spills and APSR are
excluded. Physical radio, security, storage, arbitrary faults and concurrency
are unproven.

The full R1 build compiles/composes 590 units without known failures or duplicate
strong symbols. Application imports decrease from 159 to 158; bootloader imports
remain 34. The other 589 objects are unchanged. After the callback-name change
and removal of the duplicate observer section/relocation, all other allocated
sections and relocations in this SDK unit are unchanged.

Exact qualification selected no new regions. The canonical source plan and
hybrid application hash remain unchanged, with 4,269 source-built, 641,891
binary-pull-through and 248 resource bytes. Complete source linking, hardware
support and a byte-identical source rebuild remain unfinished.

The [receipt](peer-observer-review.json) records sources, compiler arguments,
hashes and evidence. Ignored reproduction inputs are under
`build/goal-r1-peer-observer/`; current reports are
`build/sources-goal-r1-peer-observer/report.json` and
`build/hybrid-goal-r1-peer-observer/build-report.json`.
