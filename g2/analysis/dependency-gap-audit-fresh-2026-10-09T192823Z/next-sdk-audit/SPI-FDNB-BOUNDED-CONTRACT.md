# New SPI FDNB candidate: bounded independent contract

Source-derived plan only. Owner01a1228e owns stock binding; discovery owns API/provenance. No stock instruction execution, source compilation, duplicate probe, SDK extraction/redistribution, source/index/pin/Git/device change occurred. Use authenticated5.2Apollo510 am_hal_iom.c/hashcb8024be21b6b86171637d9bd33170e720a56944933635b0940939a2fdcc63f2 and its corresponding header; prior5.1source lacks these four named functions. Source availability does not prove stock includes them.

## Gate before fixtures

Bind an exact locked function/extent/hash and its interrupt-service branch, callees, literal/register dependencies. If no candidate body/caller exists, stop at a scoped static exclusion; do not construct source-only fixtures and call them original execution. Authenticate actual enum size, uint64alignment, bool layout and validation defines from stock/provider inputs. Firmware-model MMIO responses and callback fixtures are synthetic supplied inputs, not physical SPI/DMA/IRQ delivery. No resume/hand-over/provider stub can be called genuine transaction completion.

## Argument and layout discriminator

API(source) r0=handle,r1=transaction,r2=callback,r3=context under ordinary32bit ARM calling convention. Transaction includes peer union, instruction length/u64instruction, byte count,direction,TX/RXpointers,continue/repeat/priority, NEW eFdnbMode, then pause/status queue controls. Under ordinary4byte enums/pointers,8byte u64alignment: peer0,instrLen4,u64Instr8,numBytes16,direction20,TX24,RX28,continue32,repeat33,priority34,eFdnbMode36,pause40,status44,total48. Prior old pause/status are36/40,total48withtailpadding. Therefore unchanged sizeof48does NOT prove field compatibility. These offsets are conditional calculations, not an admitted stockABI: IAR short-enum/packing settings could alter them.

New FDNB state conditional layout: active0,enumMode4,RXptr8,TXptr12,RXleft16,TXleft20,DMAbytes24,savedINTEN28,savedDMATRIGEN32,callback36,context40,total44. Offset of this substructure inside private handle must be recovered separately; do not transplant5.2handle offsets into stock. Saved fields, callback slot and queue counts are mandatory comparison state, not just result length.

## Entry/state/queue source contract

When validation enabled: invalid handle,nulltransaction,wrongdirection,zero length and validate_transaction(true) can reject. SPI-only mode and eSeq!=RUNNING tests occur regardless of validation macro. Critical section begins before rejection of activeFDNB,bHP,nonzero pending count; STATUS masked(IDLEST|CMDACT)must equalIDLEST or returnsIN_USE. Exact status values/macros need authenticated header/stock decoding before oracle use.

Success savesINTEN/DMATRIGEN,zeroesTxnInt,sets pending1,disables priorDMA,clears interrupts,sets instruction/device/DCX/FULLDUP fields, marksactive and records callback/context. It sets eMode=TX_DMA_RX_IRQ only for that exact selector; every other selector falls backRX_DMA_TX_IRQ rather than rejection. TX-DMA path clearsTXleft/TXptr,setsDMAbytes/count/targetTX/directionM2P. RX-DMA path keepsTXleft/TXptr,sets targetRX/directionP2M and pre-fillsTXFIFO. Both enable FDNBinterruptmask and issueCMD. Critical state restores on all protected exits.

This hybrid function rejects existingHP/pendingqueue state rather than enqueueing an ordinary command. Pause/status transaction fields are not consumed directly in this function; no inferred support for normal queue gating follows. Stock ordinary nonblocking/full-duplex providers must be compared on actual bodies, not names or presence of FULLDUP register bit.

FIFOhelpers consume at most4bytes per word and require FIFO room/size>=4 even for a1..3byte tail. TX packs little-endian and zeroes unused high bytes; RX copies onlyremainingchunk and ignores high bytes. Pointer/counter and read/write order matter. ModeTX_DMA_RX_IRQ may drainRX on every service invocation; other mode fillsTX only onTHR.

## Completion/error source contract

Service accumulates ui32TxnInt. Active FDNB handler operates before normalHP/queue path. ERR dominates after initial FIFO service: status provider and reset_on_error execute,thenfinish,returnstatus. CMDCMP TX-DMA mode drainsagain: RXleft0finishesSUCCESS; remainingRXplusidle finishesFAIL; remainingRXnonidle remainsactive. RX-DMA mode withDMAbytes!=0 and noDCMP returnsSUCCESS but remainsactive, even afterCMDCMP. WithDCMP, TXleft0andidle finishesSUCCESS; remainingTXidle finishesFAIL; nonidle remainsactive.

finish savescallback/context into locals,clearsactive/mode/pointers/counters/callback/context,pending andTxnInt; disablesDMA,restores savedDMATRIGEN,clearsFULLDUP,restores savedINTEN; onlythen callscallback(context,status) ifnonNULL. An independent callback fixture should observe clearedstate/restoredregisters and exactlyonecall. No physical data movement/interrupt delivery is implied.

## Maximum12 directed fixture positions after stock gate

1.wronginterface reject;2.RUNNINGsequence reject;3.activeFDNB reject;4.HP reject;5.pendingqueue reject;6.nonidle/CMDACT status rejection;7.validTX_DMA_RX_IRQ start;8.validRX_DMA_TX_IRQ start with3byteTXtail and sufficientFIFO room;9.TXfill/RXdrain boundary withremaining3andFIFO room/size<4(no progress);10.TX-DMA CMDCMP,residualRX,idle →FAILcleanup;11.RX-DMA CMDCMPwithoutDCMP →successfulreturn butactive retained;12.activeerrorpluscompletion →error precedence/reset/cleanup.

These12positions are a frozen bounded proposal, not everyvalidation/completionbranch coverage. Pure completedSUCCESScleanup should be independently bound statically; if it is the actual differentiator, replace a redundant rejection position before freezing, recordingwhy. Do not add manualcontinued11→completion as an extraactualtransaction pass. Independent supplied-state snapshots can testeachbranch but must remain labelledsynthetic.

Eachfixture compares exactreturn, complete relevantstate, registerwrite/read order, callbackcount/context/status and criticalrestore; guards coverfullbuffers/state capacities and source retention before valuecomparison. FIFOPOP/PUSH/DMA/MMIO areexplicitmodels; callbackcalls testsoftwareorder only. Stoponunknowncallee/ABI/MMIO semantics ratherthanrepairingregisters orsubstitutingproviders. Null/validationbranches may be omitted only when actualcompiledefines establishabsence,not to fitfixturecounts.

## Stop and result categories

No addressboundnewstocktarget: stopstaticcandidate, nofixtureexecution. Verifiedoldproviderwithoutnewstate/interruptmode: scopedsoftwareexclusion, not completeSDKversionidentity. Matchingnewbranches: finitebehaviorcontract, not authenticsourceproducer orphysicaltransfer. Newprivatehandleoffsets, exactcompiler/configuration orrealIRQ/DMAbehavior remaindistinctinputs. ClosedDSP/LZ4/Nema/STRDISfindings arepreserved; no repeatedprobe isproposed.
