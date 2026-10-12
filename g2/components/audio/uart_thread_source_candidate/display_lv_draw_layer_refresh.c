/* Native LV ext-draw refresh 0x452d42 and layer-type refresh 0x44c50e. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern void audio_uart_lv_obj_event_451670(void *,uint32_t,void *);
extern void audio_uart_lv_obj_setup_layer_43e1fa(void *);
extern void audio_uart_display_size_changed(void *); /* selected 0x440656 */
extern uint32_t audio_uart_lv_obj_layer_type_44cd9e(void *);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_draw.c";
uint32_t audio_uart_lv_draw_size_get_452dc8(void *object) {
    uint8_t *obj=(uint8_t *)object;
    uint8_t *layer=*(uint8_t **)(void *)(obj+8u);
    return layer==0 ? 0u : *(uint32_t *)(void *)(layer+0x2cu);
}
void audio_uart_lv_refresh_draw_452d42(void *object) {
    if(object==0) {
        audio_uart_lvgl_log(3u,path,0x165u,"lv_obj_refresh_ext_draw_size",
                            "Asserted at expression: %s (%s)","obj != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    uint8_t *obj=(uint8_t *)object;
    uint32_t previous=audio_uart_lv_draw_size_get_452dc8(object);
    uint32_t updated=0u;
    audio_uart_lv_obj_event_451670(object,0x1bu,&updated);
    uint8_t *layer=*(uint8_t **)(void *)(obj+8u);
    if(layer==0 && updated!=0u) {
        audio_uart_lv_obj_setup_layer_43e1fa(object);
        layer=*(uint8_t **)(void *)(obj+8u);
    }
    if(layer!=0)__builtin_memcpy(layer+0x2cu,&updated,4u);
    if(updated!=previous)audio_uart_display_size_changed(object);
}
void audio_uart_lv_update_layer_44c50e(void *object) {
    uint8_t *obj=(uint8_t *)object;
    uint32_t type=audio_uart_lv_obj_layer_type_44cd9e(object);
    uint8_t *layer=*(uint8_t **)(void *)(obj+8u);
    if(layer==0) {
        if((uint8_t)type==0u)return;
        audio_uart_lv_obj_setup_layer_43e1fa(object);
        layer=*(uint8_t **)(void *)(obj+8u);
    }
    uint16_t bits;__builtin_memcpy(&bits,layer+0x32u,2u);
    bits=(uint16_t)((bits&0xf3ffu)|((type&3u)<<10));
    __builtin_memcpy(layer+0x32u,&bits,2u);
}
