/* Native lv_obj_update_layer_type predicate 0x44cd9e. Generated style getter
 * wrappers at 0x44b88e/7a/84/98/a2/c4/902/8ea all forward exact property
 * IDs to the already selected 0x44bdea style property source. */
#include <stdint.h>
extern uint32_t audio_uart_lv_style_property_44bdea(void *,uint32_t,uint32_t);
uint32_t audio_uart_lv_obj_layer_type_44cd9e(void *object) {
    if(audio_uart_lv_style_property_44bdea(object,0u,0x70u)!=0u)return 2u;
    if(audio_uart_lv_style_property_44bdea(object,0u,0x6eu)!=0x100u)return 2u;
    if(audio_uart_lv_style_property_44bdea(object,0u,0x6fu)!=0x100u)return 2u;
    if(audio_uart_lv_style_property_44bdea(object,0u,0x73u)!=0u)return 2u;
    if(audio_uart_lv_style_property_44bdea(object,0u,0x74u)!=0u)return 2u;
    if((uint8_t)audio_uart_lv_style_property_44bdea(object,0u,0x63u)!=0xffu)return 1u;
    if(audio_uart_lv_style_property_44bdea(object,0u,0x75u)!=0u)return 1u;
    if((uint8_t)audio_uart_lv_style_property_44bdea(object,0u,0x69u)!=0u)return 1u;
    return 0u;
}
