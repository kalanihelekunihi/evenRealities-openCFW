# Read-only NOR/MSPI contract comparison

Scope: current emulator source/docs against official Macronix LLD1.1b internal reference and OpenCFW retained hardware/transaction evidence. Emulator AGENTS read; prohibited buzzer work untouched. No model/source modifications, simulation execution or hardware commands; vendor code not redistributed. This is source inspection, not an executed device-contract test.

## Confirmed agreements

- G2MX25U25643G.BeginCommand requires QE for quad commands and CommandAllowedInMode rejects6C inQPI. Official sampleQREAD4B similarly rejectsQPI/missingQE.
- AddressLength treats6C as explicitly4bytes independent ofB7 state; ordinary read/program/erase address width depends on fourByteAddress. This separates dedicated4byte opcodes from global4byte mode correctly at inspected contract level.
- FinishTransmission B7/E9 toggles fourByteAddress; ConfigurationRegister exposes modebit5, permitting software postcommandverification. The referenceEN4B checks resulting mode rather than assuming success.
- DummyCycles6C is8; ReadLaneCount is4. AdvanceIdleCycles consumes dummybits then discards real responsebits, preserving partialbit skew. Matches vendor defaultQREAD dummy selection; shortened/extra clocks are represented rather than silently normalized.
- StatusRegister includesWIP/WEL; mutating operations requireWEL and stageuntilvirtualcompletion; BeginCommand filters commands duringbusy. This is substantial state modeling, not an alwaysready flash stub. Physical timings/interruptiondamage remain unverified synthetic choices.
- Both32MiB andJEDECwireC2/25/39 agree withOpenCFW stock packedID002539C2. Existing G2 command summary03/02/20/B7/6C with8dummy agrees atprotocollevel.

## Useful improvements / qualification limits

1. **Phase-width qualification is not established.** MSPI uses byteExchange/Transmit plusAdvanceIdleCycles; subordinate interface does not expose instruction/address/data lane widths. NOR infers outputlane count fromopcode. Correct6Cprotocolrequires1laneopcode+1lane4byteaddress+4lanedata, but acceptingnormalizedbytes cannot prove thecontrolleractuallyconfiguredthosephasewidths. Add an explicit phasecontract and negativewidthfixtures in a future authorizedmodelchange; here no contradiction orimplementationclaim is made.
2. **Modepostcondition needs executed evidence.** StaticB7state/registercode agrees; no testcase executed here provingcorrectCSboundary, busyignoredB7 andreadbackthroughstockHAL. An offline fixture should retainpre/poststate andactualwireheader, notjustsuccessfulAPIreturn.
3. **Cross-version stock anchors must stay separate.** Emulator external-nor-model.md cites2.2.9.22 RDID00475914/read00476C14/HAL004D77B0. OpenCFWlocks2.2.6.10 withdriver0046F4A4+; samepart/commands doNOTauthenticateold/newinstructiontransactions. Need version/hash-boundcapturesbeforeaddress/callsequencecomparison; neither addresses norconfiguration may transfer silently.
4. **Timing not hardware-qualified.** Model explicitly omits pinrate/turnaround/buswidthwallclockdelay; virtualprogram/erase/WRSRdelays andsyntheticpowerresponse canvalidatefunctionalpollingbutnotphysicaltimeoutmargin. Retainthislimit in userfidelityclaims.
5. **Stock dynamic configuration not established here.** Known6C/eightdummy summary agrees; exactQEsetup,QPItransition, statuspollsequence andbusytraffic needauthenticatedcall/transactioncapture forlockedrelease. Noabsenceclaimfromnotfindingacapture.

No actual protocolcontradiction was established in this boundedsourceinspection. Unsupportedphasequalification andunverifiedphysical/crossversionbehavior must not be reported asbugs. VendorLLD isa reference, notstockprovider; itsownstarting-addressonlycheck isnotacompleterangevalidator tocopy. No campaign/sourcecompleteness/byteequalityclaim.

Inputs: emulatorrenode/peripherals/G2MX25U25643G.cs,G2Apollo510_MSPI.cs,docs/external-nor-model.md; OpenCFWdocs/hardware/components/mx25u25643g.md,g2/symbols/apollo_main.tsv; vendoracquisitionreceipt. Exacthashes inprovenance.json.
