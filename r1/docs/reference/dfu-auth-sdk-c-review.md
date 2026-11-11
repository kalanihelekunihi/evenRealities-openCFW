# DFU authorization through typed Nordic C APIs

`r1/src/application/runtime/native_dfu_ble_event.c` replaces its handwritten
value-get and authorization-reply SVC wrappers with the pinned SDK C APIs
`sd_ble_gatts_value_get` and `sd_ble_gatts_rw_authorize_reply`. The local
normal-function SVC override is removed. Compile-time checks bind the eight-byte
value record, its length/offset/data-pointer fields, the sixteen-byte reply
record and the CCCD handle offset to the recovered layout. Known callers supply
16-bit connection and attribute handles. SDK SVC instructions remain; arbitrary
high-bit raw helper inputs are not part of this typed contract.

The existing outer frame adapter remains necessary. Its CCCD bytes retain
caller history when a read writes nothing, including a successful non-writing
read. The new calls do not initialize those bytes. Indication availability is
checked by the actual SDK helper. The reply record retains its type, update bit
and serialized 0x1fd denial status. Only full-word service result 17 retries;
other results leave the loop. Dispatch afterward depends on the serialized
reply status, as in stock, rather than adding a new service-error gate.
Connection state is reloaded for every reply attempt.

Fresh REA code windows at 0x7cdc8 and 0x52154 match the preserved application.
Normal product objects pass **6746 stock/previous/new cases (20238 executions)**:

- **5002 authorization cases** cover every low CCCD byte, partial/non-writing
  reads, retained bytes, high-bit value-get errors, altered returned lengths,
  repeated busy replies, non-busy high-bit reply errors, explicit reply-buffer
  mutations, live connection changes and both modeled interrupt-mask settings.
  An independent oracle checks service 173/176 arguments, original pointer
  aliases, byte records, retry counts, dispatch and returned status.
- **1744 integrated cases** link the actual backend, SDK indication helper and
  shared owner allocation. Of these, 304 reach the actual control dispatcher,
  exercising supported enter-DFU requests as well as invalid-name and unsupported
  command responses. Actual backend HVX requests use service 174 with checked
  payloads, returned lengths and error/event sequences.
- Within that integrated matrix, **28 staged DFU requests** continue through the
  actual HVC observer and finalizer. Twelve reach modeled shutdown after checked
  GPREGRET clear/set services 61/60; sixteen exercise service failures and the
  resulting event path. Callback/service effects and shutdown are modeled.

The fixture uses the real 28-byte context and one linked 12-byte asynchronous
owner allocation. It seeds that allocation; it does not execute SDK asynchronous
initialization. Core cases use an explicit control-dispatch model, while the
integrated cases execute the actual backend and HVC path. Both reconstructed
variants are prohibited from entering stock code. Private helper frames and
incidental caller-clobbered outputs are excluded. The tests retain original
frame aliases without equating every private frame or exception snapshot.

Five compiled defects are detected: wrong get service, wrong reply service,
truncated get status, lost busy retry and shifted value pointer. The normal
implementation is rerun afterward. All three other observer function bodies
remain byte-identical. The normal build compiles **801 units (719 application,
82 bootloader)** without failures or duplicate strong symbols; imports remain
95 application and 22 bootloader linker metadata symbols. Strict GNU bootloader
linking and the R1 manifest check pass. All 798 other nongenerated prior object
hashes are unchanged; generated boot vectors/crypto retain identical allocated
bytes and relocations. The global check retains the unrelated unlisted G2
resident-ROM assembly file. Source-plan selections are unchanged.

[The evidence receipt](dfu-auth-sdk-c-review.json) records exact input, header,
object and test hashes. This does not establish physical BLE/SoftDevice dispatch,
actual GPREGRET writes, reset/DFU transfer, asynchronous behavior, complete fault
state or a full application final link. Remaining frame assembly is not claimed
to be portable ISO C or removable from this evidence.
