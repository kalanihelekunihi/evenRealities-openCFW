/* Native LV style property fetch 0x44b7ce and object entry search 0x44c834. */
#include <stdint.h>
extern uint32_t audio_uart_page_style_selector_44b860(uint32_t);
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
