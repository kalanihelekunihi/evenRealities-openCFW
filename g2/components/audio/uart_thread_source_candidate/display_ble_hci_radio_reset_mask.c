/* Native vendor reset 0x55c286 and radio pin routing 0x4c2e30.
 * ROM 0x4c3224 -> 0x78ee48 contains authenticated pin mode 3. */
#include <stdint.h>
extern uint32_t audio_ble_hci_radio_stack_stop_55c430(uint32_t);
extern uint32_t g2_codec_pin_function(uint32_t,uint32_t); /* selected 0x480f0c */
static uint32_t get(const uint8_t *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
static void put(uint8_t *p,uint32_t v) {__builtin_memcpy(p,&v,4u);}

uint64_t audio_ble_hci_radio_stack_reset_body(uint32_t pointer,uint32_t unused,
                                               uint32_t scratch,uint32_t high) {
    (void)unused;(void)scratch;
    uint8_t *row=(uint8_t *)(uintptr_t)pointer;
    uint32_t result=0u;
    if(row==0||(get(row)&0x01ffffffu)!=0x01123456u)result=2u;
    else {
        if((get(row)&0x02000000u)!=0u)(void)audio_ble_hci_radio_stack_stop_55c430(pointer);
        put(row,get(row)&~0x01000000u);
    }
    return ((uint64_t)high<<32)|result;
}
__attribute__((naked)) uint64_t audio_ble_hci_radio_stack_reset_55c286(uint32_t pointer) {
    __asm volatile("b audio_ble_hci_radio_stack_reset_body");
}

void audio_ble_hci_radio_mask_4c2e30(uint32_t index,uint32_t selector) {
    if(index>=8u)return;
    uint32_t code=index*4u+(uint8_t)selector;
    uint32_t a,b,c=0u,d=0u,count=0u;
    switch(code) {
    case 0u:a=5;b=7;c=6;d=0x32;count=4;break;
    case 1u:a=5;b=6;count=2;break;
    case 4u:a=8;b=10;c=9;d=0x33;count=4;break;
    case 5u:a=8;b=9;count=2;break;
    case 8u:a=0x19;b=0x1b;c=0x1a;d=0x0b;count=4;break;
    case 9u:a=0x19;b=0x1a;count=2;break;
    case 12u:a=0x1f;b=0x21;c=0x20;d=0x0d;count=4;break;
    case 13u:a=0x1f;b=0x20;count=2;break;
    case 16u:a=0x22;b=0x24;c=0x23;d=0x10;count=4;break;
    case 17u:a=0x22;b=0x23;count=2;break;
    case 20u:a=0x2f;b=0x31;c=0x30;d=0x11;count=4;break;
    case 21u:a=0x2f;b=0x30;count=2;break;
    case 24u:a=0x3d;b=0x3f;c=0x3e;d=0x75;count=4;break;
    case 25u:a=0x3d;b=0x3e;count=2;break;
    case 28u:a=0x16;b=0x18;c=0x17;d=0x13;count=4;break;
    case 29u:a=0x16;b=0x17;count=2;break;
    default:return;
    }
    (void)g2_codec_pin_function(a,3u);
    (void)g2_codec_pin_function(b,3u);
    if(count==4u) {
        (void)g2_codec_pin_function(c,3u);
        (void)g2_codec_pin_function(d,3u);
    }
}
