/* Native lv_obj_get_child_count 0x44ddea. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_tree.c";
static const char function[]="lv_obj_get_child_count";
static const char format[]="Asserted at expression: %s (%s)";
static const char expression[]="obj != NULL";
static const char message[]="NULL pointer";
uint32_t audio_uart_lv_child_count_44ddea(void *object)
{
    if(!object){
        audio_uart_lvgl_log(3u,source,0x195u,function,format,expression,message);
        for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    uint8_t *spec=*(uint8_t **)((uint8_t *)object+8u);
    return spec?*(uint16_t *)(void *)(spec+0x30u):0u;
}
