/* Native get_selector_style_prop 0x44ce8a. Built-in property flags are an
 * authenticated ROM table at 0x6d439c; extended flags live under LV root. */
#include <stdint.h>
extern const uint8_t audio_uart_lv_builtin_property_flags[];
extern uint8_t audio_uart_display_lv_root[];
extern uint32_t audio_uart_page_style_selector_44b860(uint32_t);
extern uint32_t audio_uart_lv_style_entry_find_44c834(void *,uint32_t,uint8_t,uint32_t *);
uint32_t audio_uart_lv_selector_style_prop_44ce8a(void *object,uint32_t selector,
                                                   uint32_t property,uint32_t *out) {
    uint8_t prop=(uint8_t)property;
    uint32_t part=audio_uart_page_style_selector_44b860(selector);
    if((uint8_t)audio_uart_lv_style_entry_find_44c834(object,selector,prop,out)==1u)
        return 1u;
    uint8_t inheritable=0u;
    if(prop<0x8au)inheritable=audio_uart_lv_builtin_property_flags[prop]&1u;
    else {
        uint8_t *extension=*(uint8_t **)(void *)(audio_uart_display_lv_root+0x30u);
        if(extension!=0)inheritable=extension[(uint32_t)prop-0x8au]&1u;
    }
    if(inheritable==0u) {
        if(part==0u && (prop==1u || prop==2u)) {
            for(uint8_t *ancestor=*(uint8_t **)(void *)object;
                ancestor!=0;ancestor=*(uint8_t **)(void *)ancestor) {
                uint32_t value=*(uint32_t *)(void *)(ancestor+(prop==1u?24u:28u));
                if(value!=0u){*out=value;return 1u;}
            }
        }
        return 0u;
    }
    for(uint8_t *parent=part==0u ? *(uint8_t **)(void *)((uint8_t *)object+4u) :
                                  (uint8_t *)object;
        parent!=0;parent=*(uint8_t **)(void *)(parent+4u)) {
        uint16_t state;__builtin_memcpy(&state,parent+0x28u,2u);
        if((uint8_t)audio_uart_lv_style_entry_find_44c834(parent,state,prop,out)==1u)
            return 1u;
    }
    return 0u;
}
