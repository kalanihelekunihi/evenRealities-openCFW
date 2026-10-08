# Touch integrity/history and complete command7 closure

Independent `history.c` closes original helpers0x7fa4/8058/814c/8680. ELF SHA `216bca061ebbfb01e4e112149ec0d7dfa457e1e87cb311a12b6800aa5ed9971c` passes1,148 helper,1,728 full extended-write and800 complete command7 comparisons. All execute actual stock versus source-derived native functions without function-entry cuts. SROM return codes and full/torn row effects are synthetic. Callback then deferred invocation is sequential, not an IRQ/task/host-delivery proof. Four incorrect history/provider mutants are rejected.

## Behavior recovered

- DefineLast scans main then redundant planes, selects strictly greater unsigned sequence only whenCRCvalid; ties retain earlier/main selection. SequenceFFFFFFFF outranks small wrapped values. Redundant selection returns093e0004.
- Integrity checks current main, then mirror without moving the last pointer. Otherwise rescans; even successful rescanning retains093e0001. Only output sequenceword0 is written.
- Historic copy validates previous wear-block row and copies its historic half through installed provider slot5. Invalid row with both stored checksum and sequencezero is accepted withoutcopy; erasedFF is different. Valid mirror status093e0004; providercopyerror093e0002.
- Merge replays bounded older payload intersections and fresh scratch into the destination historic half. PriorCRCfailure can suppress fresh replay. Copycallback status is ignored. LastCRCstatus returned; zero logicalrows maps093e0003 (not directly exercised by thissuite).
- Installed copycallback0x4860 returns uint32zero. The earlier void-return reconstruction excluded this value; this independently owned source corrects it without modifying previous sealed evidence.

The actual128-byte CRC spans bytes1..124, excluding byte0 and tail125..127. Provider reads borrow synchronous RAM; no heap ownership transfer. Context layout is in `provider.h`; valid bounded geometry/provider and payload headers remain preconditions.

## Complete command7 evidence

`command7-results.json` records800 native/stock cases over5 initial storage patterns,initialized/simple flags,5 synthetic flash effects,4 parameters and2PRIMASKvalues. Compared ACK, upperstorage status, orderedSROMrequests/payloads, context/config/gesture/I2C state, storage andPRIMASK. All actual helper/flash/critical instructions execute. Acceptednonzero parameter ACK070017; rejectedzero ACK07ff17. There are300 uninitialized upperstatus1,300 initialized upperstatus0 and200 rejected/no-persistence fixtures. Underlying flashdrivererrors are discarded by stock adapters; accepting ACK/status does not certify durability.

Fifty additional **stock-only** readbacks of syntheticcommand7 storage show25 requested configurations,43 statuszero and7badchecksum. These are constructed fixture counts, not device successrates or native-read equivalence. Blank extended storage plus injected load/program failure retainszero configuration with acceptedACK/deferredstatus0/readstatus0. Phonecommands6/8 queryRAM, notpersistent readback.

The1,728 extendedsuite has1,264 statuszero and464badchecksum. A blank-row, address63,size49 fixture returnsbadchecksum evenwithsyntheticSROMsuccess, because history validation is a separate operation; do not attributeallbadchecksumreturns toflashfailure. No physicalstorage snapshot or SROMimplementation is available.

Source has subsequently been copied into isolated `g2/components/touch/eeprom_offline`, with fresh validation kept in the read-closure directory. This analysis image was not installed into any accepted checkpoint or production payload. True extended read0x82e0 (620bytes) is the next dependency, and its new reconstruction is separate work. No firmware-byte equality/source-complete/hardware claim.
