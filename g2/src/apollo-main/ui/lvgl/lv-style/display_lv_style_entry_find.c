/* Native LV style property fetch 0x44b7ce and object entry search 0x44c834. */
#include <stdint.h>
extern uint32_t audio_uart_page_style_selector_44b860(uint32_t);
static uint16_t get16(const uint8_t *p){uint16_t v;__builtin_memcpy(&v,p,2u);return v;}
static uint32_t get32(const uint8_t *p){uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
uint32_t audio_uart_lv_style_get_prop_44b7ce(void *style,uint32_t property,uint32_t *out) {
    uint8_t *s=(uint8_t *)style;
    uint8_t *items=(uint8_t *)(uintptr_t)get32(s);
    uint8_t prop=(uint8_t)property;
    if(s[8u]!=0xffu) {
        uint32_t count=s[8u];
        for(uint32_t i=0;i<count;i++)if(items[count*4u+i]==prop) {
            *out=get32(items+i*4u);
            return 1u;
        }
    }
    else {
        for(uint32_t i=0;items[i*8u]!=0u;i++)if(items[i*8u]==prop) {
            *out=get32(items+i*8u+4u);
            return 1u;
        }
    }
    return 0u;
}
uint32_t audio_uart_lv_style_entry_find_44c834(void *object,uint32_t selector,
                                                uint8_t property,uint32_t *out) {
    uint8_t *obj=(uint8_t *)object;
    uint32_t group=(uint8_t)property>>2;
    if(group>30u)group=31u;
    uint32_t group_bit=1u<<group;
    uint32_t part=audio_uart_page_style_selector_44b860(selector);
    uint16_t state=(uint16_t)selector;
    uint16_t packed=get16(obj+0x2au);
    uint32_t count=(packed&0x3ffu)>>4u;
    uint32_t best=UINT32_MAX;
    uint32_t i=0u;
    uint8_t *entries=(uint8_t *)(uintptr_t)get32(obj+0x0cu);
    while(i<count && (get32(entries+i*8u+4u)&0x02000000u)!=0u) {
        if((packed&8u)==0u) {
            uint32_t bits=get32(entries+i*8u+4u);
            uint32_t sel=bits&0x00ffffffu;
            if(audio_uart_page_style_selector_44b860(sel)==part) {
                uint8_t *style=(uint8_t *)(uintptr_t)get32(entries+i*8u);
                if((get32(style+4u)&group_bit)!=0u &&
                   audio_uart_lv_style_get_prop_44b7ce(style,property,out)==1u)
                    return 1u;
            }
        }
        i++;
    }
    for(;i<count;i++) {
        uint32_t bits=get32(entries+i*8u+4u);
        uint8_t *style=(uint8_t *)(uintptr_t)get32(entries+i*8u);
        if((get32(style+4u)&group_bit)==0u)continue;
        uint32_t sel=bits&0x00ffffffu;
        if(audio_uart_page_style_selector_44b860(sel)!=part)continue;
        uint16_t entry_state=(uint16_t)sel;
        if((entry_state&(uint16_t)~state)!=0u)continue;
        if((int32_t)best>=(int32_t)entry_state)continue;
        if(audio_uart_lv_style_get_prop_44b7ce(style,property,out)!=1u)continue;
        if(entry_state==state)return 1u;
        best=entry_state;
    }
    return best==UINT32_MAX ? 0u : 1u;
}
