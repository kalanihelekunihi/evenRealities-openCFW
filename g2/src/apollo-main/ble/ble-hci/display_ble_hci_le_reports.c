/* Native LE report decoders 0x56a398/0x56a430/0x56a5be/0x56ab50.
 * The callback pointer at live HCI stack state +8 is configured elsewhere. */
#include <stdint.h>
extern uint8_t audio_ble_hci_stack_state_20073870[];
extern void *audio_wsf_buffer_alloc(uint16_t);
extern void g2_wsf_candidate_buffer_free_word(uint32_t);

static void copy(uint8_t *d,const uint8_t *s,uint32_t n) {for(uint32_t i=0;i<n;i++)d[i]=s[i];}
static void zero(uint8_t *d,uint32_t n) {for(uint32_t i=0;i<n;i++)d[i]=0u;}
static void half(uint8_t *d,uint16_t n) {d[0]=(uint8_t)n;d[1]=(uint8_t)(n>>8);}
static void pointer(uint8_t *d,const uint8_t *p) {uint32_t n=(uint32_t)(uintptr_t)p;__builtin_memcpy(d,&n,4u);}
static void deliver(void *event) {
    uint32_t p;__builtin_memcpy(&p,audio_ble_hci_stack_state_20073870+8u,4u);
    ((void (*)(void *))(uintptr_t)p)(event);
}
static void release(void *p) {g2_wsf_candidate_buffer_free_word((uint32_t)(uintptr_t)p);}

uint32_t audio_ble_hci_le_adv_report_body(const void *bytes,uint32_t unused,
                                          uint32_t scratch,uint32_t high) {
    (void)unused;(void)scratch;
    const uint8_t *input=(const uint8_t *)bytes;
    uint8_t count=input[0];
    if(count<16u) {
        uint8_t *event=(uint8_t *)audio_wsf_buffer_alloc(0x3bu);
        if(event!=0) {
            while(count!=0u) {
                event[10]=input[1];event[11]=input[2];
                copy(event+12u,input+3u,6u);
                event[8]=input[9];
                if(event[8]>31u)break;
                pointer(event+4u,event+0x1cu);
                copy(event+0x1cu,input+10u,event[8]);
                input+=10u+event[8];
                event[9]=input[0];event[18]=0u;
                zero(event+0x13u,6u);
                half(event,0u);event[2]=6u;event[3]=0u;
                deliver(event);
                count--;
            }
            release(event);
        }
    }
    return high;
}
__attribute__((naked)) uint32_t audio_ble_hci_le_adv_report(const void *bytes,uint32_t length) {
    __asm volatile("b audio_ble_hci_le_adv_report_body");
}

uint32_t audio_ble_hci_le_ext_adv_report_body(const void *bytes,uint32_t unused,
                                              uint32_t scratch,uint32_t high) {
    (void)unused;(void)scratch;
    const uint8_t *input=(const uint8_t *)bytes;
    if(input[0]<16u) {
        const uint8_t *row=input+1u;
        uint8_t max=0u;
        for(uint8_t i=0;i<input[0];i++) {uint8_t n=row[0x17u];if(n>max)max=n;row+=0x18u+n;}
        uint8_t *event=(uint8_t *)audio_wsf_buffer_alloc((uint16_t)max+0x24u);
        if(event!=0) {
            row=input+1u;
            for(uint8_t i=0;i<input[0];i++) {
                half(event+4u,(uint16_t)((uint16_t)row[0]|((uint16_t)row[1]<<8)));
                event[6]=row[2];copy(event+7u,row+3u,6u);
                event[13]=row[9];event[14]=row[10];event[15]=row[11];
                event[16]=row[12];event[17]=row[13];
                half(event+18u,(uint16_t)((uint16_t)row[14]|((uint16_t)row[15]<<8)));
                event[20]=row[16];copy(event+21u,row+17u,6u);
                half(event+28u,row[23]);
                if(event[28]>0xe5u)break;
                pointer(event+0x20u,event+0x24u);
                copy(event+0x24u,row+0x18u,event[28]);
                row+=0x18u+event[28];
                half(event,0u);event[2]=0x2cu;event[3]=0u;
                deliver(event);
            }
            release(event);
        }
    }
    return high;
}
__attribute__((naked)) uint32_t audio_ble_hci_le_ext_adv_report(const void *bytes,uint32_t length) {
    __asm volatile("b audio_ble_hci_le_ext_adv_report_body");
}

uint32_t audio_ble_hci_le_per_adv_report_body(const void *bytes,uint32_t unused,
                                              uint32_t scratch,uint32_t high) {
    (void)unused;(void)scratch;
    const uint8_t *in=(const uint8_t *)bytes;
    if(in[6]<0xf8u) {
        uint8_t *event=(uint8_t *)audio_wsf_buffer_alloc((uint16_t)in[6]+0x10u);
        if(event!=0) {
            half(event+4u,(uint16_t)((uint16_t)in[0]|((uint16_t)in[1]<<8)));
            event[6]=in[2];event[7]=in[3];event[8]=in[4];event[9]=in[5];
            half(event+10u,in[6]);pointer(event+12u,event+16u);
            copy(event+16u,in+7u,in[6]);
            half(event,0u);event[2]=0x31u;event[3]=event[9];
            deliver(event);release(event);
        }
    }
    return high;
}
__attribute__((naked)) uint32_t audio_ble_hci_le_per_adv_report(const void *bytes,uint32_t length) {
    __asm volatile("b audio_ble_hci_le_per_adv_report_body");
}

void audio_ble_hci_le_direct_adv_report(const void *bytes,uint32_t length) {
    (void)length;
    const uint8_t *row=(const uint8_t *)bytes;
    uint8_t count=*row++;
    if(count<16u) {
        uint8_t *event=(uint8_t *)audio_wsf_buffer_alloc(0x1cu);
        if(event!=0) {
            while(count!=0u) {
                event[10]=row[0];event[11]=row[1];copy(event+12u,row+2u,6u);
                event[18]=row[8];copy(event+19u,row+9u,6u);event[9]=row[15];
                row+=16u;event[8]=0u;pointer(event+4u,0);
                half(event,0u);event[2]=6u;event[3]=0u;
                deliver(event);count--;
            }
            release(event);
        }
    }
}
