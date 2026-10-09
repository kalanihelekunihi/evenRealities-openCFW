# EM9305 transport: independent 2.2.6.10 binding

The older unresolved IOM note can be narrowed: locked OpenCFW **2.2.6.10 selects IOM6 for the EM9305 host driver**. This is independently evidenced by old-image instructions, not transplantation of 2.2.9.22 addresses. It resolves firmware transport selection; it does not supply a board schematic or physical measurements. Canonical documents were not edited.

Input: `g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`, SHA256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`. File offset 0x20 maps to 0x438000. HciDrvRadioBoot [0x4B48A6,0x4B49CE) freshly hashes to the existing symbol record `6521b6ef083e2d005e890c922bcd93b2271e7d256b0543e2471f5e797cda09bd` (see receipt). Emulator audit input and comparison-image hashes are separately recorded.

| Contract | Locked 2.2.6.10 evidence | Emulator audit 2.2.9.22 evidence |
|---|---|---|
| Module 6 selected | 4B48C8 sets r0=6; 4B48CA calls 52DD94 | 4C669E argument; 4C66A0 calls 544114 |
| Module propagated to HAL | 52DD9A saves r0 in r6; 52DDF6 restores r0=r6; 52DDF8 calls 55C2BC with handle output | 544114 driver init; HAL initialize 574328 |
| IOM MMIO derivation | configure 55CAD4 loads handle module to r6; 55CADA loads literal at55CF38 =40050000; 55CAE2 computes base+(module<<12), writes offset104 at55CAE6; module6 yields40056000 | IOM6 base40056000; configure574B00 |
| Ready GPIO117 / IRQ59 | 4B49A8 r1=117; callback registration4B49B2; 4B49BA priority4,4B49BC IRQ59; enable4B49C2 IRQ59 | registration4C67AA, priority4C67BC, enable4C67C4 |
| Ready register | reset52E502 loads literal52EBA4=40010410;52E508 extracts bit21; repeated52E52E/530. Transaction polling52DF94/9A does same | reset54490A/544936 and handler4C6988 |
| Software CS GPIO149 |52DF6A r1=0;52DF6C r0=149;52DF6E calls480FD6; additional release calls use1 | TX544372, release54443C/54446A |
| Reset GPIO93 low/high |52E4E0/4E2 sets0/93;52E4E4 calls GPIO writer;52E4EE/4F0 sets1/93;52E4F2 writes |5448E8..5448FA |
| Configuration clock GPIO15 |52E854 helper toggles GPIO15, including52E870..52E888; caller52E8F8 passes40 and52E8FA calls helper |544C5C helper;544D14 caller argument40 |

GPIO writer480FD6 independently decodes pin bank/index: action0 writes a bit to literal481758=40010458 plus bank*4, action1 to48175C=4001043C plus bank*4. Thus the low/high claims are tied to hardware GPIO clear/set register operations rather than inferred solely from function names. The ready address40010410 is GPIO RD3 (GPIO base40010000+410); bit21 is GPIO96+21=117 under the Apollo510 register layout, consistent with explicit callback pin117. It should not be described as a dedicated BLEIF status MMIO register.

The initialization chain is 52DD94 ->55C2BC initialize,55C7E8 power control,55CA94 configure,55C32E enable; names follow public HAL topology and the preserved module argument. HAL enums not independently discriminated remain numeric. These addresses are specific to2.2.6.10.

## Prior-audit reconciliation

`docs/hardware/components/em9305.md:73–75` says which IOM (if any) carries the driver is open and mentions unavailable IOM6 pinout. Firmware module selection is now bound; absence of a board pinout does not invalidate the executable module argument. `g2/docs/reference/protocols.md:34` labels the driver Apollo3-derived/blocking BLEIF-style and physical bus unverified. Its packet/source lineage description should not be promoted to an Apollo dedicated BLEIF register bank: the selected old driver calls the IOM HAL, polls GPIO117 and controls a software CS. Historical referenced detailed audit/map files are absent locally; consolidated notes and authenticated current bytes governed this comparison.

## Physical and behavioral limits

- IOM6 selection, MMIO computation and Apollo GPIO numbers are firmware contracts. Physical SCK/MOSI/MISO pad-to-EM pin continuity, board traces and electrical levels are not independently measured here.
- GPIO149's software low/assert and high/release transaction role is established; actual net continuity to EM nCS remains schematic/measurement-dependent.
- GPIO93 low/high reset behavior is established. Calling the physical net EM ENABLE is a datasheet-supported functional interpretation, not a verified board net name.
- GPIO15's configuration pulse routine and40 argument are established. Exact connection to EM GPIO5 remains a functional wiring inference.
- Ready active-high polling and GPIO117 callback are established. Controller timing, actual interrupt edge delivery and wake latency remain physical/runtime assumptions.
- Emulator audit leaves GPIO61/62/63 individual software-SPI roles, GPIO136 shutdown purpose and GPIO138 lifecycle purpose unresolved. This bounded pass does not resolve them or infer a dedicated wake wire.
- No physical bus test, ARC controller execution, complete radio model, source completeness, or bundle byte equality follows from this result.

Static disassemblies and selected interval/literal hashes are alongside this report. No downloaded code/device action/emulator modification or canonical/index edit was performed.
