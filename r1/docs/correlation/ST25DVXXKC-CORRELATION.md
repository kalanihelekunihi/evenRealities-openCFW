# ST25DVxxKC NFC provider correlation

## Decision

R1 firmware `2.2.6.0009` contains an STMicroelectronics ST25DVxxKC dynamic-NFC-tag
driver. Twenty-nine recovered functions belong to ST's provider boundary and must be
compiled from the pinned BSD-3-Clause upstream component. Twenty-three adjacent functions are
R1-specific board or policy adapters and are the only NFC functions in this reviewed
cluster eligible for local clean-room implementation.

The selected compatible source is ST's fp-sns-stbox1 commit
`e9a35449b777699b5e1dd0f1466de0ead554893a`, component path
`Drivers/BSP/Components/st25dvxxkc`. This is an authenticated compatible snapshot;
the exact checkout originally used by R1 has not been uniquely proven.

## Provider-owned functions

| R1 entry | Upstream symbol | Correlation basis |
| --- | --- | --- |
| `0x00031B32` | `ST25DVxxKC_GetGPO1_ALL` | GPO1 register extraction |
| `0x00031B46` | `ST25DVxxKC_GetGPO2_ALL` | GPO2 mask `0x1f` |
| `0x00031B62` | `ST25DVxxKC_GetGPOStatus` | GPO status read/control flow |
| `0x00031B96` | `ST25DVxxKC_GetI2C_SSO_DYN_I2CSSO` | dynamic register `0x2004`, bit 0 |
| `0x00031BF4` | `ST25DVxxKC_GetMB_CTRL_DYN_ALL` | dynamic mailbox-control byte |
| `0x00031C0A` | `ST25DVxxKC_GetFTM_MBMODE` | mailbox-mode bit extraction |
| `0x00031C26` | `ST25DVxxKC_Init` | IC reference `0x50/0x51` and init state |
| `0x00031C56` | `ST25DVxxKC_PresentI2CPassword` | exact 17-byte password/validation-code frame and register `0x0900` |
| `0x00031CA4` | `ST25DVxxKC_IsDeviceReady` | IO readiness callback and tag address |
| `0x00031CB6` | `ST25DVxxKC_ReadI2CSecuritySession_Dyn` | dynamic security-session read |
| `0x00031CD2` | `ST25DVxxKC_ReadID` | object wrapper over IC-reference register `0x17` |
| `0x00031D36` | `ST25DVxxKC_ReadMBMode` | mailbox-mode register read |
| `0x00031D52` | `ST25DVxxKC_ReadMailboxData` | maximum offset 256 and mailbox base `0x2008` |
| `0x00031D78` | `ST25DVxxKC_ReadReg` | exact BSim similarity `1.0` |
| `0x00031D88` | `ST25DVxxKC_RegisterBusIO` | complete IO callback-table assignment |
| `0x00031DC8` | `ST25DVxxKC_ResetEHENMode_Dyn` | dynamic energy-harvesting reset |
| `0x00031DDA` | `ST25DVxxKC_SetEH_CTRL_DYN_EH_EN` | read/modify/write of EH enable |
| `0x00031E0E` | `ST25DVxxKC_SetGPO1_ALL` | GPO1 whole-register write |
| `0x00031E22` | `ST25DVxxKC_SetGPO2_ALL` | masked GPO2 update |
| `0x00031E64` | `ST25DVxxKC_SetMB_CTRL_DYN_MBEN` | mailbox-enable update |
| `0x00031D00` | `ST25DVxxKC_WriteData` | `0xA6`, 256-byte chunking, timeout 320 |
| `0x00031F2C` | `ST25DVxxKC_WriteReg` | exact BSim similarity `1.0` |
| `0x00031F3A` | `ST25DVxxKC_WriteRegister` | `0xAE`, 256-byte chunking, timeout 320 |
| `0x00077CE4` | `ST25DVxxKC_ReadITSTStatus_Dyn` | object wrapper over dynamic interrupt-status register `0x2005` |
| `0x00077CF0` | `ST25DVxxKC_ReadMailboxData` | mailbox bounds and address `0x2008` |
| `0x00077CFC` | `ST25DVxxKC_ReadMBCtrl_Dyn` | complete mailbox status-bit decoding |
| `0x00077D08` | `ST25DVxxKC_ReadMBLength_Dyn` | dynamic length register `0x2007` |
| `0x00077D14` | `ST25DVxxKC_SetMBEN_Dyn` | mailbox enable wrapper |
| `0x00077D20` | `ST25DVxxKC_WriteMailboxData` | maximum 256 bytes, address `0x2008` |

Every entry, size, and recovered body SHA-256 is enforced by
`../../tools/verify_openr1.py`.
The raw 31,776-row comparison and its independent hashes are in
[`generated/st25dvxxkc-source-correlation/README.md`](../README.md).

The two new exact starts are independently bounded tail targets. The `0x00044C90` legacy row
loads the fixed R1 object and tail-branches to the 78-byte password presenter at `0x00031C56`;
the `0x00077CF0` legacy row does the same for the 38-byte mailbox reader at `0x00031D52`.
Both targets have their own prologue and return and reproduce the pinned BSD provider functions,
so the ledger now owns them separately instead of accepting the legacy noncontiguous span.
Their body SHA-256 values are respectively
`584479be5f22628424ca82235f167069063d134e057e37ebf3737b099156886e` and
`9da42db6e851a04174232c5df737888b813f01b4e341fc558e9c08c8c59f8c6b`.

## Authenticated R1 bus-IO callback table

The literal table at `0x00044C34` contains the six odd Thumb pointers in the exact
`ST25DVxxKC_IO_t` field order from the pinned upstream header: `Init`, `DeInit`,
`IsReady`, `Read`, `Write`, and `GetTick`. The registration function at
`0x00044BEC` installs that complete table. Independent disassembly of the rebuilt
application authenticates each callback as a contiguous function:

| IO field | Stock extent | Bytes | Body SHA-256 | Transparent C symbol |
| --- | --- | ---: | --- | --- |
| `Init` | `0x00044C6E..<0x00044C78` | 10 | `378533c2312d3aa997953218f921e56e6d82c563759485194f425adfa90c695e` | `r1_st25dvxxkc_bus_initialize` |
| `DeInit` | `0x00044C64..<0x00044C6E` | 10 | `8b7848ac566af13545e7c0ca052a08264dc3a9288942aa275f34e827fc2cab7c` | `r1_st25dvxxkc_bus_deinitialize` |
| `IsReady` | `0x00044C78..<0x00044C84` | 12 | `7c8d31605621bc9f7adc17e70c7b5f74f8b1f5d27bcb0442c513fb7f12c5604c` | `r1_st25dvxxkc_bus_is_ready` |
| `Read` | `0x00044C84..<0x00044C8A` | 6 | `030026b653096676e0a1e42ef849033b09a3312468389e5824d859449eb37404` | `r1_st25dvxxkc_bus_read` |
| `Write` | `0x00044C8A..<0x00044C90` | 6 | `3bbff11ae7fbd405ae5aaf1d4b32ea5cc2eaa8c23b34e3434c0c935076b3c1f0` | `r1_st25dvxxkc_bus_write` |
| `GetTick` | `0x00044C58..<0x00044C5E` | 6 | `579f66b93cd2bbcb53693929db18e36025cdc6e5d94aa3e7590989e1d8a117b1` | `r1_st25dvxxkc_bus_tick_get` |

The read/write veneers truncate the device address to eight bits, as the stock
`uxtb` instructions do. `IsReady` delays for ten ticks and returns success; init
and deinit acquire/release the recovered `i2c_5` resource. The clean-room API
fails closed when one of those typed providers is absent rather than dereferencing
an unbound stock callback.

## Authenticated charging-dock state helpers

Six further script-created entries form a compact R1 product-state API used by
the recovered factory commands. They operate on the byte fields rooted at stock
address `0x20006858` and the 11-byte dock-version buffer at `0x20006864`; the
clean-room implementation moves that state into `r1_st25dvxxkc_dock_state`.

| Stock extent | Bytes | Body SHA-256 | Transparent behavior |
| --- | ---: | --- | --- |
| `0x00077250..<0x00077258` | 8 | `b1f2be62466b2e568a7b60fa3e04186116d2e80759e8dfd862045d14c8d4c0ca` | clear dock-hardware byte |
| `0x0007725C..<0x00077264` | 8 | `167416acc38887c21d902ff6d88f6e27317bfc38bfe9eae44df370934d033188` | clear all 11 dock-version bytes |
| `0x00077268..<0x0007726E` | 6 | `3c0a2c335e8fcf80c4100a66f61a44a70183c0c30be0a8749f802571f9a6902e` | read dock-hardware byte |
| `0x00077274..<0x0007728A` | 22 | `2aea8b96b3cc9a764ebc460e79864f0dd8e1b481984679d25b5b8a9ba67ba2c0` | return version pointer and byte length |
| `0x00077290..<0x00077296` | 6 | `2e9cd305fe6b02a0dab2e3f8d223d6c3eb0961e10d18c0f961bb0dd9a567f4a5` | store factory charge-temperature byte |
| `0x0007729C..<0x000772A2` | 6 | `0594a3e6604c4c62a70819ee5094ceab26fb2eb8fbb5280fd4b92fff602100ce` | store dock-advertising enable byte |

The stock version getter calls unbounded `strlen` and truncates the result to a
byte. OpenR1 bounds the scan to the proven 11-byte buffer and returns NULL for
invalid state/length pointers; this is deliberate memory-safety hardening.

## R1-owned adapters

| R1 entry | Clean-room boundary |
| --- | --- |
| `0x00044C58` | `ST25DVxxKC_IO_t.GetTick` board tick callback |
| `0x00044C64` | `ST25DVxxKC_IO_t.DeInit` / `i2c_5` resource release |
| `0x00044C6E` | `ST25DVxxKC_IO_t.Init` / `i2c_5` resource acquire |
| `0x00044C78` | `ST25DVxxKC_IO_t.IsReady` ten-tick readiness delay |
| `0x00044C84` | `ST25DVxxKC_IO_t.Read` address-truncating bus veneer |
| `0x00044C8A` | `ST25DVxxKC_IO_t.Write` address-truncating bus veneer |
| `0x00044BEC` | nRF52 bus registration and provider initialization |
| `0x00044C90` | product password presentation/write policy |
| `0x00044C9C` | security-session state management |
| `0x00044CE8` | product GPO configuration, retry, and logging |
| `0x00077250` | charging-dock hardware-state clear |
| `0x0007725C` | 11-byte charging-dock version clear |
| `0x00077268` | charging-dock hardware-state getter |
| `0x00077274` | bounded charging-dock version getter |
| `0x00077290` | factory charge-temperature state setter |
| `0x0007729C` | dock-advertising state setter |
| `0x00077764` | NFC initialization and recovered product configuration orchestration |
| `0x00077BE0` | bounded mailbox receive and product message dispatch |
| `0x00077C50` | product identity read/log adapter |
| `0x000772A8` | 23-byte R1 dock-advertisement command framing |
| `0x00077430` | dock identity heartbeat and field-control policy |
| `0x00096A48` | product field-seen getter |
| `0x00096A54` | product field-seen setter |

The stock function at `0x00077BE0` obtains a tag-reported mailbox length and can pass it
to the provider without enforcing the destination's 20-byte capacity. The clean-room
implementation must reject or cap any value above 20 bytes before the provider read. That
safety correction is deliberate functional hardening, must be tested at lengths 0, 20, 21,
255, and 256, and must not be hidden inside a rewritten copy of ST's driver.

The lower-level nRF52 I2C callbacks and board configuration remain R1 ports. Similarity to
an ST IO callback signature does not make board pins, bus instance, recovery, or locking
provider-owned.

The four dock-policy additions are independently pinned and described in
[`NFC-DOCK-POLICY-CORRELATION.md`](NFC-DOCK-POLICY-CORRELATION.md). They consume ST mailbox
status and emit a product action; ST dynamic-register and mailbox transport code remains in
the provider.

## Implemented clean-room boundary

The R1 policy adapter is implemented in
`../src/r1_st25dvxxkc.c`, with its
Nordic board port in
`../platform/nrf52840/sdk/openr1_nfc.c`.
The Nordic image links and retains the pinned ST component rather than reproducing any of
its register or password-message code.

Recovered R1 behavior implemented locally is limited to:

- ten initialization attempts and ten GPO-write attempts;
- the all-zero password presentation used to open the I2C security session;
- the recovered `0x12345678:0x13245678` deliberately nonmatching presentation used to
  close that session (these words are a logout sentinel, not an application credential);
- mailbox enable, energy-harvesting reset, five-tick settle intervals, GPO1 `0x21`, and
  clearing GPO2 bits `0x03`;
- accepted IC references `0x50` and `0x51`;
- the recovered `i2c_5` SCL P1.11, SDA P1.14, and rising-edge/no-pull GPO P0.03 board
  topology; and
- a 20-byte application mailbox with bounds checked before provider access.

ST's own example confirms that `MBLEN_DYN` encodes message length minus one. The clean
adapter therefore widens the byte, adds one, rejects values above 20, and only then calls
`ST25DVxxKC_ReadMailboxData`. It intentionally removes the stock `MBLEN_DYN + 2` read.
Tests exercise accepted lengths 0 and 20, rejected lengths 21, 255, and 256, plus encoded
register values 0, 19, 20, and 255; rejected values make no provider read.

The board port uses Nordic `nrfx_twim` instance 1 at 400 kHz on the recovered pins and
`nrfx_gpiote` for GPO. This is a functionally compatible hardware port, not a claim that
the stock software-driven two-wire implementation came from Nordic. The entire active interval
holds an exclusive external `i2c_5` lease so the unresolved YHM2710 peer is never bypassed.
Power and bus leases are mandatory. The Nordic startup now binds the recovered P1.10 board-enable
sequence and a static CMSIS mutex shared with the future YHM provider, while leaving NFC disabled.
No BLE command,
raw register API, mailbox writer, or custom NFC action surface is exposed.

## Verification status

Verified through 2026-08-16:

- strict host tests, AddressSanitizer/UndefinedBehaviorSanitizer, and freestanding Cortex-M4
  compilation pass;
- the complete verifier source-gates all 3,233 ledger functions with zero
  unclassified entries; the six callback targets above are exact manual supplements;
- FlashDB/FAL, tiny-AES-c, vendor provenance, and the Nordic SDK linked-image checks pass;
- the map retains the required ST component and R1 adapter symbols; and
- the unsigned standalone application artifacts have SHA-256
  `48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf`
  (HEX) and
  `421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`
  (BIN).

This is compilation and static/host verification, not physical NFC or dock validation.
YHM2710 electrical coexistence, P1.10 power-state behavior, GPO wake behavior, and official-dock
message compatibility remain open hardware gates.

## Source and license pins

| Artifact | SHA-256 |
| --- | --- |
| upstream archive | `eecdc6795d5c949874d95739403aacaf6f0527c3fd476f7f78fda31e4d35faa6` |
| `st25dvxxkc.c` | `00469629a6b6cf76127a82dd0ab198855d8c794320df7f2d2f41509a289146e9` |
| `st25dvxxkc.h` | `c86f94ec2bef76e3de59d2520abca7f6bf9067f4ec316bdedc3db9091a930d76` |
| `st25dvxxkc_reg.c` | `dff34273b0656f8d45acb751cc576bf55add248d3f02b5c6e6dde0d679463106` |
| `st25dvxxkc_reg.h` | `1923438b4ae90693a32e0c6247ca64f1c880ea7db088c77d2ecee6584e69bd47` |
| component `LICENSE.md` | `da99a74bf8c60dac50d83e98cbe082cef9ff3a90c04705020c383280c8a1be8b` |

The component license is BSD-3-Clause. Preserve the license and attribution when the
provider is fetched or distributed. Do not reconstruct these 27 bodies from decompiler
output; compile the pinned ST files and keep the twenty-three product seams in separate local
translation units.

## Update (2026-08-13)

The Nordic board port no longer instantiates `NRFX_TWIM_INSTANCE(1)` itself. Both the
motion driver (`openr1_motion.c`, worn context, P0.11/P0.14) and this NFC driver (dock
context, P1.11/P1.14) previously claimed the same nRF52840 TWIM1 hardware peripheral
with different pin sets, while TWIM0 is owned by touch. A new R1-owned adaptation
module, `platform/nrf52840/sdk/openr1_twim1_arbiter.c`, now owns every
`nrfx_twim` init/uninit/transfer for instance 1.

This arbiter is adaptation glue, not a recovery of stock behavior: the stock firmware
ran both logical buses (`i2c_1` motion and `i2c_5` NFC/YHM) on the GPIO-driven
software-TWI engines that remain implementation-blocked. OpenR1 substitutes the single
hardware TWIM1 for both clients, and the arbiter serializes that substitution.

Ownership semantics match the recovered product contexts, which are mutually exclusive
(dock NFC versus worn motion):

- acquisition by the current owner is idempotent; acquisition on a free bus
  initializes TWIM1 with the requester's pin/frequency/priority configuration;
- NFC (dock context) acquisition while motion owns the bus performs a documented
  handoff: the motion configuration is uninitialized and the NFC configuration is
  initialized, so the dock path works when NFC is enabled;
- motion never preempts NFC; a contested motion acquisition fails honestly with
  `NRFX_ERROR_BUSY`, and any transfer by a non-owner fails with `NRFX_ERROR_BUSY`
  rather than silently corrupting the bus;
- after NFC releases the bus, motion re-acquires it lazily on its next transfer.

Each driver keeps its own recovered pin constants and passes its configuration to the
arbiter. The existing startup topology is unchanged: NFC remains disabled at startup
and still holds the external `i2c_5` lease (shared with the future YHM provider) for
its entire active interval; the arbiter sits beneath that lease and serializes the
physical peripheral between the two OpenR1 clients. Physical dock/worn switching,
shared-power coexistence, and owned-hardware validation remain open gates.
