/* Native lv_obj_get_style_prop 0x44bdea. The zero value_act seed in pinned
 * LVGL source matches product ROM word 0x78f26c. */
#include <stdint.h>
const uint32_t audio_uart_lv_property_default_seed=0u;
extern uint32_t audio_uart_lv_selector_style_prop_44ce8a(void *,uint32_t,uint32_t,uint32_t *);
extern uint32_t audio_uart_lv_property_default_48297c(uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_style.c";
uint32_t audio_uart_lv_style_property_44bdea(void *object,uint32_t selector,uint32_t property) {
    if(object==0) {
        audio_uart_lvgl_log(3u,path,0x14cu,"lv_obj_get_style_prop",
                            "Asserted at expression: %s (%s)","obj != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    uint16_t state;__builtin_memcpy(&state,(uint8_t *)object+0x28u,2u);
    uint32_t value=audio_uart_lv_property_default_seed;
    uint8_t result=(uint8_t)audio_uart_lv_selector_style_prop_44ce8a(
        object,selector|state,(uint8_t)property,&value);
    return result==1u ? value : audio_uart_lv_property_default_48297c((uint8_t)property);
}
