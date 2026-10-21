/* Native LV object parent/count and recursive style propagation. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern void audio_uart_display_size_changed(void *);
extern void audio_uart_lv_obj_event_451670(void *,uint32_t,uint32_t);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_tree.c";
static void fail(uint32_t line,const char *function) {
    audio_uart_lvgl_log(3u,path,line,function,"Asserted at expression: %s (%s)",
                        "obj != NULL","NULL pointer");
    for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
uint32_t audio_uart_lv_theme_check_44ddea(void *object) {
    if(object==0)fail(0x195u,"lv_obj_get_child_count");
    uint8_t *obj=(uint8_t *)object;
    void *children=*(void **)(void *)(obj+8u);
    if(children==0)return 0u;
    return *(uint16_t *)(void *)((uint8_t *)children+0x30u);
}
void *audio_uart_lv_obj_has_parent_44dca2(void *object) {
    return object==0 ? 0 : *(void **)(void *)((uint8_t *)object+4u);
}
void audio_uart_lv_refresh_children_44c9dc(void *object) {
    uint32_t count=audio_uart_lv_theme_check_44ddea(object);
    for(uint32_t i=0;i<count;i++) {
        uint8_t *obj=(uint8_t *)object;
        void *children=*(void **)(void *)(obj+8u);
        uint32_t *slots=*(uint32_t **)(void *)children;
        void *child=(void *)(uintptr_t)slots[i];
        audio_uart_display_size_changed(child);
        audio_uart_lv_obj_event_451670(child,0x32u,0u);
        audio_uart_display_size_changed(child);
        audio_uart_lv_refresh_children_44c9dc(child);
    }
}
