# ST25DVxxKC NFC provider correlation

## Decision

R1 firmware `2.2.6.0009` contains an STMicroelectronics ST25DVxxKC dynamic-NFC-tag
driver. Twenty-seven recovered functions belong to ST's provider boundary and must be
compiled from the pinned BSD-3-Clause upstream component. Eleven adjacent functions are
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
| `0x00031CA4` | `ST25DVxxKC_IsDeviceReady` | IO readiness callback and tag address |
| `0x00031CB6` | `ST25DVxxKC_ReadI2CSecuritySession_Dyn` | dynamic security-session read |
| `0x00031CD2` | `ST25DVxxKC_ReadID` | object wrapper over IC-reference register `0x17` |
| `0x00031D36` | `ST25DVxxKC_ReadMBMode` | mailbox-mode register read |
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

## R1-owned adapters

| R1 entry | Clean-room boundary |
| --- | --- |
| `0x00044BEC` | nRF52 bus registration and provider initialization |
| `0x00044C90` | product password presentation/write policy |
| `0x00044C9C` | security-session state management |
| `0x00044CE8` | product GPO configuration, retry, and logging |
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

Verified through 2026-08-13:

- strict host tests, AddressSanitizer/UndefinedBehaviorSanitizer, and freestanding Cortex-M4
  compilation pass;
- the complete verifier reconciles the coverage ledger with 202 audit rows and source-gates
  3,165 recovered functions, with 795 still unclassified, nine isolated in the blocked generic
  device-registry family, fourteen in the blocked time/calendar-provider family, and forty in the
  blocked software-TWI-provider family, seven in the blocked RTC-device-provider family, and
  thirteen in the blocked sensor-algorithm heap-provider family, plus one in the blocked
  sensor-stream framework family;
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
output; compile the pinned ST files and keep the eleven product seams in separate local
translation units.
