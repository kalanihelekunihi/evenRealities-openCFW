# Touch saved-record bootstrap and default recovery

New independent source: [config_bootstrap_offline](../../components/touch/config_bootstrap_offline/README.md). This additive module composes preserved EEPROM/history/read/initialization source. No production payload, accepted checkpoint, shared state, index, device or commit changed. Locked wrapper/runtime hashes and recovered addresses are in provenance.json; original instructions are in original-disassembly.txt.

## Record validation and call flow

Bootstrap0x395c calls app_init0x34d8, then app_read0x3520(address0,record0x200009d0,size8). Readiness0x200008c4 only means library setup. Saved record is little-endian magicu32=0x45564e55 (`55 4e 56 45`),baselineu16+4,parameteru16+6. **Both read success and matching magic are required**. Baseline has no range validation; every nonzero parameter, including65535, is accepted. Parameterzero becomes1000 **in RAM only**: no write occurs, storedzero remains and normalizes again nextboot.

Failed read or bad magic invokes first-use logging intent, app_erase0x35b0, delay0xa2f0(argument10), then app_write0x3568 of defaults `{magic,0,1000}`. Init/erase/write upper failures abort with their corresponding logger call. Logger0x3ee0 is actually a return-zero leaf; these tests observe invocation/format identities, not emitted messages.

Read/write adapters first reject nullbuffer or raw32-bit `(address+size)>256` with4, then unreadyflag with1. Read maps EEPROM0 or093e0004 to0,other statuses to2; write/erase map the same success set to0,other statuses to3. These raw statuses and overflow behavior are reconstruction, not a recommended safe API contract.

## What erase actually does

Installed factory configuration is capacity256,extended,wear2,redundant1,blocking1,row=sector128:8 main wear rows0xe400..0xe800 and8 mirror rows0xe800..0xec00. Erase API0x8ae0 zeroes scratch128, derives lastsequence, advances one main row, sets sequence+1 and CRC, then programs this same versioned empty row into every main/mirror row. Header address/length and body remainzero. It does **not** produce an all-zero physical region. Installed provider's erase-required callback returnsfalse, so its program callback is used; physical programming behavior remains SROM's responsibility.

First primary and mirror requests both execute even if primary reports an upper error, then initial error aborts. After initial success, contextlast advances; remaining rows continue despite errors, retaining the first nonzero status. Default128 geometry lets stock write/erase wrappers directly call their respective gates; the independently reconstructed equivalent gate is reused. Generic sector>row read-modify-write is outside this new module.

Delay executes actual software loops in both original and reconstructed code. Reset-copied scale0x20000874=24000 gives argument10 a240000 cycle-loop argument. SystemInit/calibration is not executed. No physical elapsed duration or milliseconds is claimed.

## Original-instruction evidence

ELF SHA **8ea0d46091f797e062b2f1917ea9130ee35cab520896f049d40b072cfac47bd6**.

| Suite | Result | Compared/boundary |
| --- | --- | --- |
| Full bootstrap |218 cases PASS|Record,readyflag,context,complete storage,ordered SROM requests/app calls/log intentions,SP,PRIMASK; no function-entry cuts|
| Fresh initialization and persistent readback |216 cases PASS|Original/native fresh init+app read from post-bootstrap snapshots|
| Second boot |4 cases PASS|Original/native recovery with previous synthetic storage and faults removed|
| Negative controls |3 rejected|Wrong magic acceptance, ignored failed read with usable returned payload, ignored default-write failure|

Full suite crosses zero/erased/valid/wrongmagic/corrupt/mirror-recovery storage,parameters0/1000/65535,PRIMASK0/1,success/loaderror/programerror/torn16/torn64/selectiveerasebaseerror; two invalid initializer cases complete218. Outcomes:126 defaults-initialized calls,72 loaded-record calls,18 write-failure calls and2 init-failure calls. Bootstrap visits146/156 instructionbytes: unvisited0x39c4..0x39cd is erase-failure logging. Erase API visits208/272 instructionbytes; simple-mode branch and upper provider-error exits are not covered by these factory bootstrap fixtures. No forced entry-return stubs were used to manufacture those branches.

SROM command responses and full/torn guest writes are **synthetic external effects**, not verified physical failure models. Guest memory/stack are fixture resources. The test executes original reset copy/zero slices, not full hardware boot. Native C is semantic reconstruction, not a new exact-stock-byte claim. Build receipt records source/tool hashes; scripts are reusable offline, not production build integration.

## Failure distinctions useful to apps/CFW

- Zero storage plus synthetic all-program failures: bootstrap reports defaults initialized and RAM hasdefaults, but fresh persistent read returns0 with eight zero bytes. Library status0 alone cannot establish UNVE validity.
- Selective failure of both base history copies0xe400/0xe800 during erase: subsequent default write returns appstatus3 through actual history checksum handling, yet fresh initialization/readback returns0 and a valid defaultrecord. The next fault-free boot accepts it. Immediate write status and later readability differ because history scan/selection changes; neither is a durability proof.
- Erased storage plus load failures: RAM defaults are prepared, but fresh readstatus2 returnszero bytes; next fault-free boot performs default recovery.
- Valid magic,paramzero: RAMparameter1000, fresh storedparameter0, nextboot normalizes RAM again without writing.

Accordingly, configuration consumers should distinguish initialization readiness, read status, record magic, RAM values and independently observed persistent contents. The fixtures justify those distinctions; they do not establish hardware failure frequency, storage durability, atomicity or flash safety. No speculative patch was applied.

## SDK follow-up and next concrete leads

Existing exact attribution includes EraseRow100 and EraseAPI276 in the32 selected functions/2864-byte total; this batch validates independent composed bootstrap semantics rather than recounting those bytes as new matches. A bounded follow-up confirms both unmatched wrapper literals reserve512 scratchbytes (stock0x85d0/8988=`fffffe00`), matching EEPROM2.60's non-ECT maximum-row setting0x200. Thus default-path closure is not blocked on that allocation; remaining compiled-layout mismatch is still unresolved, and producingrevision is not unique.

Actionable static work remains: compare unmatched sector>row wrappers/merge/extended-write compiler layouts against pinned source, and trace the source producer/consumer of baseline and parameter to establish calibration behavior. Sector>row is not selected by proven factory configuration and should not displace app-facing sensor/calibration understanding. Actual0xe400..0xec00 capture and resident SROM implementation or physical trace are needed only for hardware persistence/timing conclusions, not to continue bounded static analysis. Global dependency exhaustion is not established.

All110 locked inputs,291 previously sealed files and4 accepted checkpoints freshly hash-match; see preservation.json. Existing sealed modules and reports are untouched.
