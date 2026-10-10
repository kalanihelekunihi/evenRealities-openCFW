# Independent STRDIS source delta contract

PASS: source/header/register-document mapping across three branches. Reproducible `strdis_contract.py` and `STRDIS-CONTRACT.json` retain SDK ZIP-member hashes, baseline file hash, literal field equations and version labels. No SDK members were extracted, no compiler/firmware/device execution occurred, and no source/pin/index/Git/coverage changes occurred. Stock binding belongs to focused owner01a1228e-2121-71b9-a9df-9eede6787020.

Authoritative SDK Apollo510 CMSIS header defines STRDIS position24/mask0x01000000. SDK register HTML identifies MI2CCFG as I2C Master configuration, instance0 address400502C0. With documented IOM0base40050000, offset is2C0; module bases are40050000 + module*1000 for0..7. It is read/write and documented reset field value0. The register description says “Disable detection of clock stretch events smaller than 1 cycle”. Preserve this narrow description: bit1 does not by itself prove complete clock-stretch disablement, physical tolerance or observed bus timing.

SDK HAL additionally comments that Apollo510 I2C clock stretching is not guaranteed and sets new AM_HAL_IOM_MI2CCFG_STRDIS_DEFAULT1. That software comment describes motivation/default policy; it must not replace the narrower register semantics. Canonical previous source explicitly programmed STRDIS0 in each branch, rather than leaving an unspecified field. The source uses complete MI2CCFG assignment, not a runtime OR into unknown prior state.

| I2C selection/argument | Previous word | SDK5.2word | Source timing comment |
|---|---|---|---|
|100KHZ/100000|0003F070|0103F070|approximately100kHz|
|400KHZ/400000|0003F270|0103F270|approximately400kHz|
|1MHZ/1000000|00023040|01023040|approximately860kHz|

Every word differs only by0x01000000. Other MI2CCFG fields remain identical:100/400kHz SMPCNT3,SDAENDLY15,SDADLY3; SCLENDLY0/2respectively. Nominal1MHz branch uses SMPCNT2,SDAENDLY3,SCLENDLY0,SDADLY0. All three use MI2CRST1,ARBDISABLE0,MSBFIRST0,7bit-address0. These are field encodings, not claims about reset realization/electrical output.

All three configure CLKCFG with HFRC24MHz selection,DIVEN enabled,DIV3disabled,IOCLKEN1. TOTPER/LOWPER pairs are77/3B,1D/0E,0B/05hex respectively. New STRDIS addition does not change those source clock equations. Branch is selected only under eInterfaceMode=AM_HAL_IOM_I2C_MODE; unsupported I2C rates return INVALID_ARG. SPI branch is separate and does not use these MI2CCFG constants. Common later configuration/enabling/provider behavior remains outside this delta.

Version provenance: previous local source label release_sdk5p1p0-366b80e084; newly acquired source label release_sdk5p2p0-66487dd10. User package and recorded release notes authenticate the latter input. Labels alone do not identify locked firmware's private producing checkout or establish a version-wide trait for all5.1/5.2artifacts. Both source hashes are explicit in JSON; canonical registered pin is unchanged.

Owner finite comparison should locate/hash the actual locked function and MI2CCFG stores, decode module-base and register-offset context, then compare all three complete source expressions/branches. Constants elsewhere in literal pools are not sufficient caller/register binding. If stock writes old values, exclude the unchanged new configuration path as producer for those branches, not whole SDK. If new values match, require other fields/controlflow before attribution and retain private patch/configuration alternatives. The field-name/document comparison cannot certify physical clock stretching, real active IOM routes, callback state or whole-image source/byte completeness.
