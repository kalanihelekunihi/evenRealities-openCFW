/* Native Cordio HCI initialization commands. Opcode/length and payload
 * bytes are literal stock contracts; masks remain caller-owned ROM data. */
#include <stdint.h>
extern void *audio_ble_hci_cmd_alloc_52ae38(uint16_t,uint16_t);
extern void audio_ble_hci_cmd_send(void *);
void audio_ble_hci_vendor_specific_cmd(uint16_t opcode,uint8_t length,
                                       const void *payload) { /* 0x52b84c */
    uint8_t *command=(uint8_t *)audio_ble_hci_cmd_alloc_52ae38(opcode,length);
    if(command!=0) {
        const uint8_t *src=(const uint8_t *)payload;
        for(uint32_t i=0;i<length;i++)command[3u+i]=src[i];
        audio_ble_hci_cmd_send(command);
    }
}
static void send_empty(uint16_t opcode) {
    void *command=audio_ble_hci_cmd_alloc_52ae38(opcode,0u);
    if(command!=0)audio_ble_hci_cmd_send(command);
}
static void send_mask(uint16_t opcode,const void *mask) {
    uint8_t *command=(uint8_t *)audio_ble_hci_cmd_alloc_52ae38(opcode,8u);
    if(command!=0) {
        const uint8_t *src=(const uint8_t *)mask;
        for(uint32_t i=0;i<8u;i++)command[3u+i]=src[i];
        audio_ble_hci_cmd_send(command);
    }
}
void HciLeRandCmd(void) {send_empty(0x2018u);} /* 0x52b304 */
void HciLeReadBufSizeCmd(void) {send_empty(0x2002u);} /* 0x52b31e */
void HciLeReadLocalSupFeatCmd(void) {send_empty(0x2003u);} /* 0x52b338 */
void HciLeReadSupStatesCmd(void) {send_empty(0x201cu);} /* 0x52b37c */
void HciLeReadWhiteListSizeCmd(void) {send_empty(0x200fu);} /* 0x52b396 */
void HciLeReadResolvingListSize(void) {send_empty(0x202au);} /* 0x52b7dc */
void HciLeReadMaxDataLen(void) {send_empty(0x202fu);} /* 0x52b24c */
void HciReadBdAddrCmd(void) {send_empty(0x1009u);} /* 0x52b606 */
void HciLeSetEventMaskCmd(const void *mask) {send_mask(0x2001u,mask);} /* 0x52b492 */
void HciSetEventMaskCmd(const void *mask) {send_mask(0x0c01u,mask);} /* 0x52b6bc */
void HciSetEventMaskPage2Cmd(const void *mask) {send_mask(0x0c63u,mask);} /* 0x52b6e4 */
uint32_t HciLeWriteDefDataLen(uint16_t octets,uint16_t time,
                              uint32_t unused,uint32_t high) { /* 0x52b1bc */
    (void)unused;
    uint8_t *command=(uint8_t *)audio_ble_hci_cmd_alloc_52ae38(0x2024u,4u);
    if(command!=0) {
        command[3]=(uint8_t)octets;command[4]=(uint8_t)(octets>>8u);
        command[5]=(uint8_t)time;command[6]=(uint8_t)(time>>8u);
        audio_ble_hci_cmd_send(command);
    }
    return high;
}
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
