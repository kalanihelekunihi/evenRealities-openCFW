/* Native Cordio HCI initialization commands. Opcode/length and payload
 * bytes are literal stock contracts; masks remain caller-owned ROM data. */
#include <stdint.h>
extern void *audio_ble_hci_cmd_alloc_52ae38(uint16_t,uint16_t);
extern void audio_ble_hci_cmd_send(void *);
extern void audio_ble_hci_vendor_specific_cmd(uint16_t opcode,uint8_t length, const void *payload); /* opencfw U5: now provided by the Cordio unit */
extern void HciLeRandCmd(void); /* opencfw U5: now provided by the Cordio unit */
/* 0x52b304 */
/* 0x52b31e */
/* 0x52b338 */
/* 0x52b37c */
/* 0x52b396 */
extern void HciLeReadResolvingListSize(void); /* opencfw U5: now provided by the Cordio unit */
/* 0x52b7dc */
extern void HciLeReadMaxDataLen(void); /* opencfw U5: now provided by the Cordio unit */
/* 0x52b24c */
/* 0x52b606 */
/* 0x52b492 */
/* 0x52b6bc */
/* 0x52b6e4 */
uint64_t HciVscSetRfPowerLevelEx(uint32_t level) { /* 0x4b4cb2 */
    uint32_t value=level;
    uint32_t valid=((uint32_t)(int32_t)(int8_t)level+0x1bu)<0x22u;
    if(valid)audio_ble_hci_vendor_specific_cmd(0xfcc4u,1u,&value);
    return ((uint64_t)level<<32u)|valid;
}
void HciVscUpdateNvdsParam(void) { /* 0x4b4c8a */
    volatile uint8_t *const nvds=(volatile uint8_t *)(uintptr_t)0x20074150u;
    nvds[0]=0xffu;nvds[1]=0x7cu;nvds[2]=1u;
    nvds[3]=0x0fu;nvds[4]=0xb8u;nvds[5]=0x19u;
    audio_ble_hci_vendor_specific_cmd(0xfff2u,8u,(const void *)nvds);
}
void audio_ble_hci_read_max_data_len(const void *ignored) { /* 0x569b2a */
    (void)ignored;
    volatile uint8_t *const state=(volatile uint8_t *)(uintptr_t)0x20071478u;
    volatile uint8_t *const capabilities=(volatile uint8_t *)(uintptr_t)0x20000028u;
    if((state[0x88u]&0x20u)!=0u && (*capabilities&0x20u)!=0u)
        HciLeReadMaxDataLen();
    else HciLeRandCmd();
}
void audio_ble_hci_read_resolving_list_size(const void *ignored) { /* 0x569b04 */
    (void)ignored;
    volatile uint8_t *const state=(volatile uint8_t *)(uintptr_t)0x20071478u;
    volatile uint8_t *const capabilities=(volatile uint8_t *)(uintptr_t)0x20000028u;
    if((state[0x88u]&0x40u)!=0u && (*capabilities&0x40u)!=0u)
        HciLeReadResolvingListSize();
    else {
        state[0x91u]=0u;
        audio_ble_hci_read_max_data_len(0);
    }
}
