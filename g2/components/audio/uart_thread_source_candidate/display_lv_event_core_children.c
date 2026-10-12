/* Native LVGL active input, base-class event, and bubbling selector
 * 0x452ef8/0x4516f8/0x451b34. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char object_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj.c";

uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *object,uint32_t mask) {
    if(object==0) {
        audio_uart_lvgl_log(3u,object_path,0x150u,"lv_obj_has_flag",
                            "Asserted at expression: %s (%s)","obj != NULL","NULL pointer");
        for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    uint32_t flags=*(uint32_t *)(void *)((uint8_t *)object+0x24u);
    return (flags&mask)==mask?1u:0u;
}

void *audio_uart_lv_active_input_452ef8(void) {
    return *(void **)(void *)(audio_uart_display_lv_root+0x50u);
}
uint32_t audio_uart_lv_object_event_base_4516f8(void *class_arg,void *event) {
    uint8_t *e=(uint8_t *)event;
    uint8_t *class_p=class_arg!=0?*(uint8_t **)(void *)class_arg:
                                  *(uint8_t **)(void *)*(uint8_t **)(void *)e;
    while(class_p!=0 && *(void **)(void *)(class_p+0x0cu)==0)
        class_p=*(uint8_t **)(void *)class_p;
    if(class_p==0)return 1u;
    void (*callback)(void *,void *)=*(void (**)(void *,void *))(void *)(class_p+0x0cu);
    if(callback==0)return 1u;
    *(uint32_t *)(void *)(e+0x0cu)=0u;
    callback(class_p,event);
    return (e[0x18u]&1u)!=0u?0u:1u;
}
uint32_t audio_uart_lv_event_is_bubbled_451b34(void *event) {
    uint8_t *e=(uint8_t *)event;
    if((e[0x18u]&4u)!=0u)return 0u;
    uint32_t code=*(uint32_t *)(void *)(e+8u);
    if(code==43u || code==44u)return 1u;
    if(audio_uart_lv_obj_has_flag_43e0e0(*(void **)(void *)e,0x4000u)==0u)return 0u;
    if(code==22u || (code>=26u && code<=34u) || code==37u ||
       (code>=41u && code<=44u) || (code>=49u && code<=50u) || code==52u)
        return 0u;
    return 1u;
}
