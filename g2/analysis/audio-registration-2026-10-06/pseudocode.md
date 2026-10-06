# Registration and routing ownership

Faithful bounded manual reconstruction; address/hash spans are in original-provenance.json. Public C prefixes return NEW observation records; logging providers are explicit cuts.

```c
//43d0ce: actual byte getter
uint8_t flags(void) { return *(volatile uint8_t *)0x20004543; }
//Each original logging site, with genuine rereads
if (flags() & 2) { /*43d574 logging provider boundary*/ }
else if (flags() & 1) { /*43ce9e event logger boundary*/ }
else if (flags() & 4) { /*43ce9e event logger boundary*/ }
//Execution proceeds only when the preceding provider was not selected.
```

```c
//57ab78
mode=(uint8_t)mode;
if (mode>=2 || callback==0) { log_invalid(); return -1; }
row=0x20073c20+12*mode;
if (row.callback!=0) { log_replacing(); zero12(row); }
row.owner=owner;
row.mode=mode; //one byte; padding unchanged if row initially empty
row.callback=callback; //published last
log_registered();
return 0;
//57acd0: no mode<2 check
row=0x20073c20+12*(uint8_t)mode;
if (!row.callback) { log_empty(); return 0; }
if (row.owner!=owner) { log_mismatch(); return -1; }
log_removing();
zero12(row);
return 0;
```

For zero12, original43c0e4(length12) performs an8-byte STM at row+4 (+4 word then+8 word), then a word at row+0. Source emits corresponding ordered volatile word stores. Architectural atomicity/abort/interruption properties of the grouped original store versus scalar C stores are not equivalent or established. The observed replacement contains a temporarily cleared callback before the new callback is published; no cross-thread safety follows from this order.

Registration is an overwrite API, not an exclusive-acquire API. Owner identity restricts later unregistration; it does not stop another registration. An empty row unregisters successfully without clearing stale owner/mode fields. Low-byte conversion means mode256 aliases0. Mode2 unregistration addresses a third12-byte row outside the two-row registry; the offline fixture proves the unchecked addressing, not an actual invalid caller on hardware.

## Authenticated actual callers

- Codec init58f69a: clears20074890; variant0 registers owner10b/mode0/callback58f5e1 at58f6ea; variant1 registers owner10b/mode0/callback58f4e5 at58f736. Other variants do not register here, though later startup calls still run.
- PDM init58f7b0: registers owner10b/mode1/callback58f5e1 at58f7f2.
- Codec/PDM deinit58f74a/58f806: unregister owner10b for mode0/1; only successful unregister proceeds into later stop/config cleanup. Those lifecycle providers are static evidence, not executed here.
- Callback58f5e0: with byte20004551 zero, passes original mode/pointer/length to57b1f4; when nonzero it invokes57a940 encoding first, then passes stack output/written count to57b1f4. Mode0 and1 select different encoding configurations.
- Callback58f4e4: mode0 with option off passes borrowed PCM unchanged to57b1f4; option on uses two encoder configurations and stack buffers before that sink. Encoder and sink are outside this source batch.
- Sink57b1f4 uses12-byte records at20073c08, rolling-size threshold100001, allocate/open57afc6, file_write474682 with element size1, and close4745f4 after short write. `file_write` attribution is strong in apollo_main.tsv / g2-file-runtime-function-map.tsv; the actual initializer/lifetime/close/copy behavior is not reconstructed here.

These are production diagnostic/file-family routes. They do not prove the normal205-byte BLE audio stream installs a PCM callback. The known dispatch contract instead sends unregistered mode0 into its DSP/LC3/transport fallback. The caller list is the authenticated direct-caller corpus, not an exhaustive claim about indirect/runtime registrations.
