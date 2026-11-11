# Radio negotiation, notification and regulator SDK C calls

Five handwritten SVC wrappers now call the pinned Nordic APIs:

- `native_gatt_observer.c`: MTU request/reply and data-length update.
- `native_bae8_send.c`: GATTS notification.
- `native_system_settings.c`: DC/DC regulator mode.

The local normal-function SVC overrides are removed. The SDK owns the service
numbers and architectural ABI; the forwarding functions use ordinary C and
retain their existing names. SDK-generated SVC/return instructions remain.
The settings record-frame adapters remain because their partial-read behavior
requires existing RAM bytes; this change does not initialize those bytes.

SDK connection/MTU arguments are uint16_t, and the regulator API takes uint8_t.
Known GATT observer calls use 16-bit connection/MTU fields, and the settings
caller supplies a normalized Boolean mode. The actual BAE8 context lookup rejects
full-word handles >=20 before the notification helper. Narrowing after that
existing gate does not turn an invalid handle into a valid one. Arbitrary
high-bit direct helper calls outside these typed SDK contracts are excluded;
this review does not assert raw R0 identity for those inputs.

Fresh REA windows for the stock data-length, BAE8 send and settings entries
match the preserved application. Tests use normal product objects:

- **1300 paired boundary cases** check service IDs 165/181/144/174/63, arguments,
  full-width statuses, returned limit/length writes through original pointers,
  memory guards, callee-saved registers, SP, masks and eight-byte alignment.
- **4800 stock/previous/new data-length cases** check request layouts and actual
  service-written limits. Both octet and time error branches use the returned
  fields; exact log markers, IDs, arguments and ordering match stock. This
  exercises 14400 routine executions with modeled SVC handling and logging.
  The stock routine's incidental void-return R0 is excluded; the C status return
  is checked independently.
- **5184 paired notification cases** execute the actual sender, full-word context
  lookup and SDK connection-state index. They compare returned lengths/statuses,
  flags, HVX parameters and output guards, including invalid handles 20/65536 and
  the UINT16_MAX sentinel. The actual priority-2 observer table and cold service,
  storage and pool allocations also match their preserved evidence.
- Existing GATT regressions pass: 1536 direct paired link resets, 2560 integrated
  disconnect invocations, 6144 direct paired initializations, eight null cases
  and 1280 initialization/disconnect/reinitialization sequences. The selected
  24-byte link helper remains exact, including its exposed register/flag effects.

Five compiled defect controls are detected: wrong reply service, wrong requested
MTU, lost limits pointer, discarded notification status and wrong regulator mode.
The normal boundary fixture is rerun afterward. SVC instructions execute; service
effects are modeled. Notification flag/log providers, zero-fill and service
outputs remain models, and the table check does not execute every observer.

The normal build compiles all **801 units (719 application, 82 bootloader)**
without failures or duplicate strong symbols. Imports remain 95 application and
22 bootloader metadata symbols. Strict GNU bootloader linking passes. All 796
other nongenerated prior object hashes remain unchanged; generated boot objects
retain identical allocated bytes/relocations. The other 14 function bodies in
these three units remain byte-identical. R1 manifest checks pass; the global
check retains the unrelated unlisted G2 resident-ROM assembly file. No source-plan
selections are changed.

[Machine evidence](radio-sdk-c-review.json) binds compiler dependencies, REA,
objects and probes. Physical negotiation/notification, regulator operation,
controller exceptions, timing, asynchronous execution and complete application
final linking remain unverified. Private frames, incidental caller-clobbered
outputs and APSR are excluded except for the explicitly exact link helper.
