# C-SKY mode table and callback bindings

Existing closure/ownership checked first: codec.tsv already labels all related mode/idle/TWS functions Inferred with historical verification references. Current source-dependency-next-ledger/SOURCE-OPPORTUNITIES still lists table/configuration bindings as a lead; no exact task-name/address reservation matched in current117task contracts. These scans are supporting evidence, not authoritative live ownership clearance. No new pseudocode/admission or function discovery claimed.

## Authenticated static data binding

Use canonical XIP image SHA49c9aed0126493220a3e48827c267d5e94f64d51d9ede0ccc3e84b8946744584 under conditional runtime base10203004. mode-table-byte-bindings-corrected.json records bytes/hashes. Both InitMode84-byte and ModeTick36-byte slices independently match codec.tsv hashes. Decoder is previously hash-pinned full-xip.objdump.txt.

Table at1020B1BC contains exactly the two words1020B1C4 and1020B204 used by decoded two-comparison selector. This is a two-entry bound from consumer instructions plus table words, not inferred from next unrelated data. Descriptor field offsets0/type,4/init,8/done,12/tick,16/buffer_init agree with pinned LVP_MODE_INFO.

| Descriptor | type | init | done | tick | buffer_init |
|---|---:|---|---|---|---|
|1020B1C4|0|10208634|10208624|1020861C|10208620|
|1020B204|1|10208670|1020864C|10026358|10208644|

The addresses above are exact data words at this mapping. Names IDLE/TWS and callback names remain source-backed associations: public enum defines0=IDLE/1=TWS, and historical symbols already assign matching callback names. No source build or producing checkout is authenticated by naming.

InitMode writes loop1 at2002E6E4 and index0 at2002E6E8; checks requested type against descriptor0 then1 and uses index1 only for second match, otherwise index0. Calls selected buffer_init(+16), then init(+4) withFFFF; returns descriptor type. ModeTick loads selected tick(+12), calls only if nonzero and returns loop word. InitMode code ends85E8 followed by16literal bytes; ModeTick ends8612 followed by2BKPT bytes and8literal bytes. Linear disassembly labels of literals are data, not executed instructions.

## Source/configuration alternatives

KWS pin8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5 lvp/lvp_mode.c:24–55 can produce this two-entry table if CONFIG_LVP_HAS_TWS_MODE enabled and its other optional modes disabled. AIoT pind4aa00943e22f9ddfa424f979fae3ee2a62f5c0b lvp/lvp_mode.c:19–25 also produces exactly these entries when TWS enabled. Thus table narrows compiled enabled mode set but DOES NOT discriminate KWS vs AIoT or exact revision. Callback source variants/other configuration need independent byte/config evidence. KWS lvp_mode_idle.c:44+ and lvp_mode_tws.c:389+ establish field naming/order; hashes in mode-source-provenance.json.

## Failed coordinate check preserved

mode-table-byte-bindings.json is a FAILED exploratory absolute-coordinate conversion, superseded by -corrected.json; its wrong function hashes were detected before interpretation. It is NOT target evidence. No old receipt was overwritten. Correct receipt relies only on canonical child bytes and matches known hashes. This correction must be retained in provenance, not silently mixed with complete-child/payload coordinates.

## Stop and limits

Two-descriptor static mode/callback binding is now constrained. Both public source families remain equivalent for this configuration; no further table-only inference can select producer. To discriminate, require independently authenticated callback source bytes/configuration or producing build manifest. Live index/loop values, successful callback initialization, runtime reachability, external memory mapping and physical execution are not inferred. Names existed previously; new result is exact descriptor-table consumer/field constraint. No additional download, original instruction execution, compilation, source/index/device/campaign mutation.
