# Independent IOM/CMSIS bounded review

All81 static checks PASS in IOM-CMSIS-INDEPENDENT-VERIFICATION.json; reproducible verifier verify_iom_cmsis.py. No firmware/SDK object execution, duplicate extraction, redistribution, canonical admission, production/index/Git/device mutation occurred.

## IOM source delta closed

Authenticated all four stock ranges/hex/hash receipts and serialized listing halfwords against locked main raw bytes. Independently decoded all three LDR.W aligned PC+4 targets, STR.W r1,[r2,#2C0] immediates, rate-comparison BEQ targets, common backward branches and module-address add encodings. Loads at55CB8C/55CB9E/55CBB0 read55D264/55D26C/55D274 respectively; stores55CB94/55CBA6/55CBB8 write0003F070/0003F270/00023040. Rate literals independently decode100000,400000,1000000 and route to the correct branches. Each branch returns to55CB22 for common CLKCFG flow.

Listing/reference context authenticates r6 from handle+4, base40050000 from55CF38, range checkmodule<8, and r2=r7+(r6<<12). Thus MI2CCFG destination is400502C0+module*1000. Full380byte function code envelope55CA94–55CC10 ends with POP; adjacent/shared literals remain separately accounted. Code/constant behavior does not identify a complete source/compiler producer.

All three words match previous source equations exactly and differ from unchanged new SDK defaults solely in STRDIS24/mask01000000. Official field description remains disabling detection of stretches smaller than one cycle; no observed bus timing/physical clock-stretch or active-route claim follows. This finite new-source hypothesis is closed with old software configuration behavior. No additional source/compiler sweep is justified. Private modification/configuration alternatives prevent assigning the whole firmware a5.1release solely from these writes. Full-function source equality, other MI2CCFG writers and bootloader remain untested.

## CMSIS exact-byte negative confirmed

Independently authenticated archive hash034dfb178804c3885b73e15c28bd3ff72c34d5fc9800409c44c453061662c772, parsed ar member/ELF section data, checked all20selected body hashes/object hashes and each of20reported relocation-free spans against actual archive bytes and complete main raw payload. Every span has zero raw hits and avoids the reported conservative8byte relocation exclusions. Four complete distinctive table symbols were independently resolved from ELF symbol tables, their byte/hash extents verified, and zero stock hits confirmed.

Inventory has15ELF objects and638nonempty function-symbol records;638unique(object,section,start,size) tuples here, not638stockcoveredfunctions. Twenty named selections contain14functions>=128bytes; only four qualifying complete functions have no recorded relocations: biquad_df1_f32, biquad_df2T_f32, fir_q15, mat_inverse_f32. The correction from five to four is valid. Other complete raw-body misses are unlinked comparisons, not resolved-link exclusions. Relocation-free internal instruction blocks can still change under other compilation or relaxation; no semantic or whole-library absence follows.

This audit verifies table contents/extents and selected span absence, but does not independently certify every archive relocation type/addend or all638function classifications. Searching the complete main byte payload includes code/data without admitting a code/data denominator. A match would require classification; absence covers raw presence of only these exact needles. No other payload, source revision, alternative flags, dictionary/partial algorithms or CMSIS Core/RTOS exclusion is established. Stop this unanchored CMSIS candidate until a real target name/constant/caller or matching producer evidence appears; no further generic acquisition is justified.

## Genuine unresolved opportunity and finite boundary

The remainder of the newly acquired IOM source is not exhausted by STRDIS closure. Source-delta scan identifies newly added am_hal_iom_spi_nonblocking_fullduplex and private helpers iom_fdnb_drain_rx_fifo/iom_fdnb_fill_tx_fifo/iom_fdnb_finish, alongside new FDNB interrupt handling. These are concrete new source definitions, not evidence they appear in stock. They could support an address-bound presence/absence or handler-branch comparison if owner/discovery independently selects/hash-binds a stock SPI full-duplex provider and source dependencies. No such target was established by this audit; do not call this execution-ready or infer device capability from API availability. It is separate from closed audio/UART and the three I2C configuration stores.

Current finite outputs exclude the unchanged5.2STRDIS path at three main stores and exact selected CMSIS archive needles in main. They do not justify universal SDK/public-source exhaustion or whole-firmware/source/byte equality. Further work should use a concrete changed-provider/target binding, not repeat closed probes or search generic DSP families without attribution evidence.
