/* Native hciCoreResetSequence 0x569b56. Fourth argument is native R3. */
#include <stdint.h>

extern uint8_t audio_ble_hci_controller_state_20071478[]; /* native live state */
extern uint8_t audio_ble_hci_stack_state_20073870[]; /* native live state */
extern volatile uint8_t audio_ble_hci_reset_rand_count; /* 0x20074fd0 */
extern uint8_t audio_ble_hci_local_address[]; /* 0x200714e0, live RAM */
extern uint8_t audio_ble_hci_white_list_size[]; /* 0x200714d8, live RAM */
extern const uint8_t audio_ble_hci_event_mask_78d6dc[];
extern const uint8_t audio_ble_hci_le_event_mask_78d6e4[];
extern const uint8_t audio_ble_hci_event_mask_page2_78d6ec[];

extern void HciLeSetEventMaskCmd(const void *);
extern void HciVscUpdateNvdsParam(void);
extern void HciReadBdAddrCmd(void);
extern void HciLeReadBufSizeCmd(void);
extern void HciSetEventMaskPage2Cmd(const void *);
extern void HciLeReadSupStatesCmd(void);
extern void audio_ble_hci_read_resolving_list_size(const void *);
extern void HciLeReadLocalSupFeatCmd(const void *);
extern void HciLeRandCmd(void);
extern void HciLeReadWhiteListSizeCmd(void);
extern void audio_ble_hci_read_max_data_len(const void *);
extern void HciLeWriteDefDataLen(uint32_t,uint32_t,const void *);
extern void HciSetEventMaskCmd(const void *);
extern void HciVscSetRfPowerLevelEx(uint32_t);

static uint16_t word(const uint8_t *p) { return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8)); }
static uint32_t pointer(const uint8_t *p) { uint32_t v; __builtin_memcpy(&v,p,4u); return v; }
static void put16(uint8_t *p,uint16_t v) { __builtin_memcpy(p,&v,2u); }
static void dispatch_option(uint8_t *state,const uint8_t *parameters,uint32_t opcode) {
    uint32_t target=pointer(state+0xa0u);
    if(target!=0u) ((void (*)(const void *,uint32_t))(uintptr_t)target)(parameters,opcode);
}

uint32_t audio_ble_hci_reset_sequence_body(const void *message,uint32_t unused1,
                                            uint32_t unused2,uint32_t scratch) {
    (void)unused1;(void)unused2;
    const uint8_t *p=(const uint8_t *)message;
    uint8_t *state=audio_ble_hci_controller_state_20071478;
    if(p[0]!=0x0eu)return scratch;
    uint32_t opcode=word(p+3u);
    const uint8_t *parameters=p+6u;
    switch(opcode) {
    case 0x0c01u: HciLeSetEventMaskCmd(audio_ble_hci_le_event_mask_78d6e4); break;
    case 0x0c03u: audio_ble_hci_reset_rand_count=0u; HciVscUpdateNvdsParam(); break;
    case 0x0c63u: HciReadBdAddrCmd(); break;
    case 0x1009u:
        __builtin_memcpy(audio_ble_hci_local_address,parameters,6u);
        HciLeReadBufSizeCmd(); break;
    case 0x2001u: HciSetEventMaskPage2Cmd(audio_ble_hci_event_mask_page2_78d6ec); break;
    case 0x2002u:
        put16(state+0x7eu,word(parameters));
        state[0x83u]=p[8u];state[0x82u]=state[0x83u];
        HciLeReadSupStatesCmd();break;
    case 0x2003u:
        __builtin_memcpy(state+0x88u,parameters,8u);
        audio_ble_hci_read_resolving_list_size(p+0x0eu);break;
    case 0x200fu:
        state[0x84u]=parameters[0];HciLeReadLocalSupFeatCmd(p+7u);break;
    case 0x2018u:
        if(audio_ble_hci_reset_rand_count<3u) {
            audio_ble_hci_reset_rand_count++;
            HciLeRandCmd();
        } else {
            audio_ble_hci_stack_state_20073870[0x21u]=0u;
            scratch&=0xff000000u;
            uint32_t callback=pointer(audio_ble_hci_stack_state_20073870+8u);
            ((void (*)(uint32_t *))(uintptr_t)callback)(&scratch);
        }
        break;
    case 0x201cu:
        __builtin_memcpy(audio_ble_hci_white_list_size,parameters,8u);
        HciLeReadWhiteListSizeCmd();break;
    case 0x2024u:
        if(pointer(state+0xa0u)!=0u)dispatch_option(state,parameters,opcode);
        else {
            put16(state+0x92u,0u);state[0x94u]=0u;state[0x95u]=0u;
            HciLeRandCmd();
        }
        break;
    case 0x202au:
        state[0x91u]=parameters[0];audio_ble_hci_read_max_data_len(p+7u);break;
    case 0x202fu:
        HciLeWriteDefDataLen(word(p+6u),word(p+8u),p+10u);break;
    case 0xfcc4u: HciSetEventMaskCmd(audio_ble_hci_event_mask_78d6dc);break;
    case 0xfff2u: HciVscSetRfPowerLevelEx(6u);break;
    case 0x1001u: case 0x203au: case 0x203bu: case 0x204au:
        dispatch_option(state,parameters,opcode);break;
    default: break;
    }
    return scratch;
}

/* The native one-argument caller leaves R3 as call residue. Branching rather
 * than calling keeps that architectural input intact for the 0x2018 callback. */
__attribute__((naked)) uint32_t audio_ble_hci_reset_sequence(const void *message) {
    __asm volatile("b audio_ble_hci_reset_sequence_body");
}
