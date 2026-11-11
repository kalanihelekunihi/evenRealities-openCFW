/* SPDX-License-Identifier: MIT
 * Recovered from stock firmware_ble_em9305.bin (g2-2.2.6.10) application
 * record @ VMA 0x302400 / file +0x424. HCI command tables registered by
 * application_main_30eb8c via ROM 0x10207c.
 * Wave 26: application handlers are symbolic (the image is not at stock layout, so the
 * stock 0x30xxxx literals were live bugs). ROM handlers (0x10xxxx) stay literal: ROM does not move.
 * FLAG: the first table is extended from 12 to 34 records (stock bytes 0x3340BC..0x334254 are 34
 * contiguous records); only the first 12 are registered by stock code (count 12 at 0x334950). The
 * trailing 22 records are copied verbatim but no consumer was found (guess: ROM or unused).
 */
#include <stdint.h>

struct g2_em_hci_cmd_entry {
    uint32_t handler;
    uint32_t guard;
    uint16_t opcode;
    uint16_t pad;
};
_Static_assert(sizeof(struct g2_em_hci_cmd_entry) == 12, "hci cmd entry");

extern void opencfw_em9305_EMSG_CallWeakFunction(void);
extern void opencfw_em9305_emsys_reset_cmd_304c0c(void);
extern void opencfw_em9305_emsys_reset_cmd_304c40(void);
extern void opencfw_em9305_emsys_reset_cmd_304c74(void);
extern void opencfw_em9305_EMSG_GetEmCoreInformation(void);
extern void opencfw_em9305_emsys_reply_status1_cmd_304cdc(void);
extern void opencfw_em9305_EMSG_SetBootModeFlags(void);
extern void opencfw_em9305_EMSG_SetPublicAddress(void);
extern void opencfw_em9305_EMSG_SetRssiOffset(void);
extern void opencfw_em9305_EMSG_SetSleepOptions(void);
extern void opencfw_em9305_EMSG_SetUartBaudRate(void);
extern void opencfw_em9305_EMSG_SvldMeasurement(void);
extern void opencfw_em9305_EMSMM_NVMEraseFull(void);
extern void opencfw_em9305_EMSMM_NVMEraseMain(void);
extern void opencfw_em9305_EMSMM_NVMErasePage(void);
extern void opencfw_em9305_EMSMM_ReadAtAddress(void);
extern void opencfw_em9305_EMSMM_WriteAtAddress(void);
extern void opencfw_em9305_EMSMM_WriteContinue(void);
extern void opencfw_em9305_emsys_ack_if_unlocked_cmd_305104(void);
extern void opencfw_em9305_emsys_ack_if_unlocked_cmd_305138(void);
extern void opencfw_em9305_emsys_ack_if_unlocked_cmd_30516c(void);
extern void opencfw_em9305_emsys_ack_if_unlocked_cmd_3051a0(void);
extern void opencfw_em9305_EMSRC_EmCoreReceiver154TestEnd(void);
extern void opencfw_em9305_EMSRC_EmCoreReceiverTest(void);
extern void opencfw_em9305_EMSRC_EmCoreReceiverTestEnd(void);
extern void opencfw_em9305_EMSRC_EmCoreScan15_4(void);
extern void opencfw_em9305_EMSRC_EmCoreStartAdvPattern(void);
extern void opencfw_em9305_EMSRC_EmCoreTransmitterTest(void);
extern void opencfw_em9305_EMSRC_EmCoreTransmitterTestEnd(void);
extern void opencfw_em9305_EMSRC_ReceiverTest(void);
extern void opencfw_em9305_emsrc_receiver_test_end_3054f0(void);
extern void opencfw_em9305_emsrc_status1_reply_305548(void);
extern void opencfw_em9305_EMSRC_SetRfPower(void);
extern void opencfw_em9305_EMSRC_TransmitterTest(void);
extern void opencfw_em9305_EMSRC_TransmitterTestEnd(void);
extern void opencfw_em9305_EMSRC_setAOADCteConfig(void);
extern void opencfw_em9305_EMSS_LeDecrypt(void);
extern void opencfw_em9305_EMSS_LeDecryptKC(void);
extern void opencfw_em9305_EMSS_LeEncrypt(void);
extern void opencfw_em9305_EMSS_LeEncryptKC(void);
extern void opencfw_em9305_EMSS_LeRand(void);

/* Stock 0x003340BC, 12 registered entries (count 0x334950) followed by 22 more contiguous stock records (0x33414C..0x334254) */
const struct g2_em_hci_cmd_entry g2_em_hci_cmd_table_3340bc[34] = {
    { (uint32_t)(uintptr_t)&opencfw_em9305_emsys_reply_status1_cmd_304cdc, 0x00000000u, 0xfc41u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSG_SetUartBaudRate, 0x00000000u, 0xfc44u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSG_SetSleepOptions, 0x00000000u, 0xfc49u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSG_SvldMeasurement, 0x00000000u, 0xfc4au, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_emsys_reset_cmd_304c74, 0x00000000u, 0xfc4fu, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSG_CallWeakFunction, 0xa9a9a9a9u, 0xfc51u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_emsrc_status1_reply_305548, 0x00000000u, 0xfcc3u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSG_SetRssiOffset, 0x00000000u, 0xfcc8u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_emsys_ack_if_unlocked_cmd_3051a0, 0x53535353u, 0xfd81u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_emsys_ack_if_unlocked_cmd_30516c, 0x53535353u, 0xfd82u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_emsys_ack_if_unlocked_cmd_305138, 0x53535353u, 0xfd83u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_emsys_ack_if_unlocked_cmd_305104, 0x53535353u, 0xfd84u, 0x0000u },
    { 0x001014bcu, 0x00000000u, 0xfc01u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_emsys_reset_cmd_304c40, 0x00000000u, 0xfc42u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSG_SetSleepOptions, 0x00000000u, 0xfc49u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_emsys_reset_cmd_304c74, 0x00000000u, 0xfc4fu, 0x0000u },
    { 0x00101454u, 0x00000000u, 0xfc52u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSG_GetEmCoreInformation, 0x00000000u, 0xfc53u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSG_SetBootModeFlags, 0x00000000u, 0xfc54u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_emsys_reset_cmd_304c0c, 0x00000000u, 0xfc55u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSS_LeRand, 0x00000000u, 0xfc87u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSS_LeEncrypt, 0x00000000u, 0xfc88u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSS_LeEncryptKC, 0x00000000u, 0xfc89u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSS_LeDecrypt, 0x00000000u, 0xfc8au, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSS_LeDecryptKC, 0x00000000u, 0xfc8bu, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSRC_EmCoreTransmitterTest, 0x00000000u, 0xfcc1u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSRC_EmCoreTransmitterTestEnd, 0x00000000u, 0xfcc2u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSRC_EmCoreReceiverTest, 0x00000000u, 0xfcc5u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSRC_EmCoreReceiverTestEnd, 0x00000000u, 0xfcc6u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSRC_EmCoreStartAdvPattern, 0x00000000u, 0xfcc9u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSRC_EmCoreScan15_4, 0x00000000u, 0xfcceu, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSRC_EmCoreReceiver154TestEnd, 0x00000000u, 0xfccfu, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSMM_ReadAtAddress, 0x53535353u, 0xfd01u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSMM_WriteAtAddress, 0x53535353u, 0xfd03u, 0x0000u },
};
const uint16_t g2_em_hci_cmd_count_334950 = 12u; /* stock 0x00334950 */

/* Stock 0x00334254, 11 entries */
const struct g2_em_hci_cmd_entry g2_em_hci_cmd_table_334254[11] = {
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSG_SetPublicAddress, 0x00000000u, 0xfc43u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSRC_TransmitterTest, 0x00000000u, 0xfcc1u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSRC_TransmitterTestEnd, 0x00000000u, 0xfcc2u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSRC_SetRfPower, 0x00000000u, 0xfcc4u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSRC_ReceiverTest, 0x00000000u, 0xfcc5u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_emsrc_receiver_test_end_3054f0, 0x00000000u, 0xfcc6u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSRC_TransmitterTest, 0x00000000u, 0xfccau, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSRC_TransmitterTest, 0x00000000u, 0xfccbu, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSRC_ReceiverTest, 0x00000000u, 0xfcccu, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSRC_ReceiverTest, 0x00000000u, 0xfccdu, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSRC_setAOADCteConfig, 0x00000000u, 0xfcceu, 0x0000u },
};
const uint16_t g2_em_hci_cmd_count_334952 = 11u; /* stock 0x00334952 */

/* Stock 0x00334954, 33 entries */
const struct g2_em_hci_cmd_entry g2_em_hci_cmd_table_334954[33] = {
    { 0x00102b14u, 0x00000000u, 0x0c03u, 0x0000u },
    { 0x001014bcu, 0x00000000u, 0xfc01u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_emsys_reset_cmd_304c40, 0x00000000u, 0xfc42u, 0x0000u },
    { 0x00101514u, 0x53535353u, 0xfc45u, 0x0000u },
    { 0x00101564u, 0x53535353u, 0xfc46u, 0x0000u },
    { 0x001012ccu, 0x53535353u, 0xfc47u, 0x0000u },
    { 0x001015acu, 0x53535353u, 0xfc48u, 0x0000u },
    { 0x00101208u, 0xa9a9a9a9u, 0xfc4bu, 0x0000u },
    { 0x00101138u, 0xa9a9a9a9u, 0xfc4cu, 0x0000u },
    { 0x00101384u, 0xa9a9a9a9u, 0xfc4du, 0x0000u },
    { 0x00101078u, 0x53535353u, 0xfc4eu, 0x0000u },
    { 0x00101420u, 0x00000000u, 0xfc50u, 0x0000u },
    { 0x00101454u, 0x00000000u, 0xfc52u, 0x0000u },
    { 0x00101b48u, 0x00000000u, 0xfc81u, 0x0000u },
    { 0x00101a84u, 0x00000000u, 0xfc82u, 0x0000u },
    { 0x00101cf4u, 0x53535353u, 0xfc83u, 0x0000u },
    { 0x00101ca4u, 0x00000000u, 0xfc84u, 0x0000u },
    { 0x00101c10u, 0x00000000u, 0xfc85u, 0x0000u },
    { 0x00101bccu, 0x00000000u, 0xfc86u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSMM_ReadAtAddress, 0x53535353u, 0xfd01u, 0x0000u },
    { 0x0010187cu, 0x53535353u, 0xfd02u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSMM_WriteAtAddress, 0x53535353u, 0xfd03u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSMM_WriteContinue, 0x53535353u, 0xfd04u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSMM_NVMEraseFull, 0xa9a9a9a9u, 0xfd05u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSMM_NVMEraseMain, 0x53535353u, 0xfd06u, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSMM_NVMErasePage, 0x53535353u, 0xfd07u, 0x0000u },
    { 0x00101700u, 0x53535353u, 0xfd08u, 0x0000u },
    { 0x00101760u, 0x53535353u, 0xfd09u, 0x0000u },
    { 0x001017b8u, 0xa9a9a9a9u, 0xfd0au, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSMM_WriteAtAddress, 0x53535353u, 0xfd0bu, 0x0000u },
    { (uint32_t)(uintptr_t)&opencfw_em9305_EMSMM_WriteContinue, 0x53535353u, 0xfd0cu, 0x0000u },
    { 0x00101a18u, 0xa9a9a9a9u, 0xfd41u, 0x0000u },
    { 0x001019b8u, 0xa9a9a9a9u, 0xfd42u, 0x0000u },
};
const uint16_t g2_em_hci_cmd_count_334ae0 = 33u; /* stock 0x00334AE0 */

