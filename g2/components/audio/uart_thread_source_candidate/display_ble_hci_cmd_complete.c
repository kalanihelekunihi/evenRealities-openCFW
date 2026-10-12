/* Native hciEvtProcessCmdCmpl 0x56b182, command-complete event mapping. */
#include <stdint.h>

extern uint8_t audio_ble_hci_stack_state_20073870[]; /* live */
extern const uint8_t audio_ble_hci_event_sizes_6e3720[]; /* ROM */
extern const uint32_t audio_ble_hci_event_decoders_6c910c[]; /* ROM */
extern void *audio_wsf_buffer_alloc(uint16_t); /* selected 0x530446 */
extern void g2_wsf_candidate_buffer_free_word(uint32_t); /* selected 0x5304d4 */
extern void audio_ble_hci_cmd_receive_complete(uint32_t); /* native 0x52aef8 */

static uint16_t word(const uint8_t *p) { return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8)); }
static uint32_t pointer(const uint8_t *p) { uint32_t v;__builtin_memcpy(&v,p,4u);return v; }
static uint8_t event_type(uint16_t opcode) {
    switch(opcode) {
    case 0x0c2du:return 9u;case 0x0c7cu:return 0x27u;case 0x0c83u:return 0x4cu;
    case 0x100du:return 0x4du;case 0x100eu:return 0x4eu;case 0x100fu:return 0x4fu;
    case 0x1405u:return 7u;case 0x200au:return 0x35u;case 0x200cu:return 0x34u;
    case 0x200eu:return 5u;case 0x2015u:return 8u;
    case 0x2017u:return 0x1bu;case 0x2018u:return 0x1cu;
    case 0x201au:return 0x0cu;case 0x201bu:return 0x0du;
    case 0x2020u:return 0x1du;case 0x2021u:return 0x1eu;
    case 0x2022u:return 0x21u;case 0x2023u:return 0x1fu;
    case 0x2024u:return 0x20u;case 0x2027u:return 0x15u;
    case 0x2028u:return 0x16u;case 0x2029u:return 0x17u;
    case 0x202bu:return 0x18u;case 0x202cu:return 0x19u;
    case 0x202du:return 0x1au;case 0x202fu:return 0x22u;
    case 0x2030u:return 0x29u;case 0x2031u:return 0x2au;
    case 0x2039u:return 0x37u;case 0x2040u:return 0x38u;
    case 0x2042u:return 0x36u;case 0x2054u:return 0x3fu;
    case 0x2055u:return 0x40u;case 0x2056u:return 0x41u;
    case 0x2057u:return 0x42u;case 0x2062u:return 0x48u;
    case 0x2065u:return 0x49u;case 0x206cu:return 0x54u;
    case 0x206eu:return 0x4au;case 0x206fu:return 0x4bu;
    default:return (opcode>>10)==0x3fu?0x12u:0u;
    }
}
uint32_t audio_ble_hci_event_cmd_complete_body(const void *parameters,uint32_t length,
                                                 uint32_t unused,uint32_t scratch) {
    (void)unused;
    const uint8_t *p=(const uint8_t *)parameters;
    uint8_t count=p[0];
    uint16_t opcode=word(p+1u);
    uint8_t type=event_type(opcode);
    if(type!=0u) {
        uint8_t *event=(uint8_t *)audio_wsf_buffer_alloc(audio_ble_hci_event_sizes_6e3720[type]);
        if(event!=0) {
            event[0]=0u;event[1]=0u;event[2]=type;event[3]=0u;
            uint32_t decoder=audio_ble_hci_event_decoders_6c910c[type];
            ((void (*)(void *,const void *,uint32_t))(uintptr_t)decoder)(event,p+3u,(uint8_t)length);
            uint32_t callback=pointer(audio_ble_hci_stack_state_20073870+
                        ((opcode==0x2017u||opcode==0x2018u)?0x0cu:8u));
            ((void (*)(void *))(uintptr_t)callback)(event);
            g2_wsf_candidate_buffer_free_word((uint32_t)(uintptr_t)event);
        }
    }
    audio_ble_hci_cmd_receive_complete(count);
    return scratch;
}
__attribute__((naked)) uint32_t audio_ble_hci_event_cmd_complete(const void *parameters,
                                                                  uint32_t length) {
    __asm volatile("b audio_ble_hci_event_cmd_complete_body");
}
