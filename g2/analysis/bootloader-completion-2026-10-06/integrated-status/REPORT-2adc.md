# Bootloader source closure checkpoint

The immutable source-linked ELF `2adcc60aba10fed90231072a059b6e7922a10d646444278aba42d1cf9d9e2839` passes all seven modeled cases: normal/update2, malformed-update3, strict interrupted-update/reboot2. Its distinct observed original instruction-byte union is31,188; overlapping profile counts must not be added. See [same-image receipts](same-image-validation-2adc.json), [ELF/provider manifest](source-image-manifest-2adc.json), and [remaining bindings](remaining-providers.md). This is a bounded source test image, not a standalone complete payload or byte-identical rebuild.

The pinned ELF and filesystem seed are under `g2/build/bootloader-completion/source-image-compatible/snapshots/2adcc60aba10fed90231072a059b6e7922a10d646444278aba42d1cf9d9e2839/`. Old8cd9 and3234 receipts retain their old hashes; the newer source image is tested against its own hash.

## Newly integrated behavior

Native cache startup41e1e8/41e266 replaces two providers. It retains guard bits, configuration-byte packing, set/way masks, low-byte argument truncation and exact write/barrier order; [direct tests](cache-enable/REPORT.md) pass1,440 cases /296 original bytes. Native41d90e register-ID reads replace one provider:230 direct cases,30 bytes, raw unnamed40010000 region with exactly one32-bit access per valid ID. The numerical binding ledger decreases to40, including legitimate resident ROM and explicit unfinished runtime boundaries. The native cache code uses a separate relocated30000 source slot; no original executable bytes are retained there. A prior stock-address placement collided with harness hooks and is not a passing result.

INFO read4213e6 and41d28a ROM thunk are also native in this image; their separate dispatch tests cover8,064+4null+2thunk=8,070 fixtures. Mode0 feature record is16 bytes with byte-sized enums and trim version at12; mode1 device record is64 bytes, with memory-size words8–11 in bytes and word7 untouched. [Layout evidence](DEVICE-INFO-LAYOUT.md) remains authoritative over historical clock/wait names.

## Exact interrupted-update outcome

Before the modeled atomic MRAM page write, the original application page survives; after it, the generated test payload survives. Both phases preserve update flag55555555. A fresh synthetic reboot retries the update and reaches the authenticated application's reset-entry boundary with matching NOR/page/flag, file calls, task events, ordered peripheral writes and endpoint/exception records. Application instructions do not execute. No physical atomicity, partial programming, brownout or hardware recovery claim follows.

## Further source closure underway

Requests26/27/29 have172 isolated original/source cases /1,404 bytes and are being routed into a subsequent image. Request26 clock selection preserves side effects before invalid-frequency rejection; NULL config dereferences rather than returning an invented guard error. Request29 compares the requested Boolean byte directly against the existing mode byte, including mode2 transition, and ignores queue-reset return as stock does. Their clock-request/release/delay inputs remain synthetic in the isolated profile; the shared graph has native clock providers. Requests30/34 remain pending.

The source initializer sorter now passes98 direct inputs plus4 runner and5 comparator fixtures /1,042 observed original bytes, without a stock-order provider. Its8-byte record contract and actual four-entry initializer table are distinct from an exhaustive general qsort proof; heap fallback is not yet forced by the receipt. Actual callback bodies4301d6/43194c/415590 remain under analysis; allocator41fd70 has separate source. The sorter is not linked in this pinned image.

Mode publication41fadc now independently passes563 cases /664 original bytes through native41d92c register update; it is source-ready for a later image. Remaining NOR timing/XIP, platform startup41fa50/callees, non-NULL power configuration422ba8, mutex/ISR/task termination/deferred paths, full vectors/assets/data/layout and exact compiler reproduction remain explicit work. Twenty-three native units also [compile for Cortex-M55](native-closure-m55-2adc.json); that is not a whole-image target compiler or hardware test.

Resident ROM program0200ff20, delay40 and INFO read48 lie outside the OTA. Source wrappers can be recovered; ROM internals and physical timing/cache/IRQ/power-loss behavior require suitable external evidence. No hardware operations, commits, staging changes or IAR authentication were performed.
