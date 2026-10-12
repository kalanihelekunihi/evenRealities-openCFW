/* Native lv_obj_refresh_style 0x44bc8c with product LVGL refresh flag at
 * root+0x24 and ordered layout, layer, geometry, and child effects. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern void audio_uart_display_size_changed(void *); /* selected 0x440656 */
extern uint32_t audio_uart_page_style_selector_44b860(uint32_t);
extern uint32_t audio_uart_page_style_needs_invalidate_44b844(uint32_t,uint32_t);
extern uint32_t audio_uart_lv_style_position_a_44b870(void *,uint32_t);
extern uint32_t audio_uart_lv_style_position_b_44b866(void *,uint32_t);
extern void audio_uart_lv_obj_event_451670(void *,uint32_t,uint32_t);
extern void audio_uart_lv_mark_layout_43f648(void *);
extern void *audio_uart_lv_obj_has_parent_44dca2(void *);
extern void audio_uart_lv_update_layer_44c50e(void *);
extern void audio_uart_lv_refresh_draw_452d42(void *);
extern void audio_uart_lv_refresh_children_44c9dc(void *);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_style.c";
void audio_uart_page_style_refresh_44bc8c(void *object,uint32_t selector,uint32_t property) {
    if(object==0) {
        audio_uart_lvgl_log(3u,source,0x115u,"lv_obj_refresh_style",
                            "Asserted at expression: %s (%s)","obj != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    if(audio_uart_display_lv_root[0x24u]==0u)return;
    audio_uart_display_size_changed(object);
    uint32_t part=audio_uart_page_style_selector_44b860(selector);
    uint8_t prop=(uint8_t)property;
    uint8_t layout=(uint8_t)audio_uart_page_style_needs_invalidate_44b844(prop,4u);
    uint8_t ext_draw=(uint8_t)audio_uart_page_style_needs_invalidate_44b844(prop,2u);
    uint8_t inheritable=(uint8_t)audio_uart_page_style_needs_invalidate_44b844(prop,1u);
    uint8_t layer=(uint8_t)audio_uart_page_style_needs_invalidate_44b844(prop,16u);
    if(layout!=0u) {
        if(part==0xf0000u || part==0u ||
           (audio_uart_lv_style_position_a_44b870(object,0u)==0x3fffffffu ||
            audio_uart_lv_style_position_b_44b866(object,0u)==0x3fffffffu)) {
            audio_uart_lv_obj_event_451670(object,0x32u,0u);
            audio_uart_lv_mark_layout_43f648(object);
        }
    }
    if(part==0xf0000u || part==0u) {
        if(prop==0xffu || layout!=0u) {
            void *parent=audio_uart_lv_obj_has_parent_44dca2(object);
            if(parent!=0)
                audio_uart_lv_mark_layout_43f648(parent);
        }
        if(layer!=0u)audio_uart_lv_update_layer_44c50e(object);
    }
    if(prop==0xffu || ext_draw!=0u)audio_uart_lv_refresh_draw_452d42(object);
    audio_uart_display_size_changed(object);
    if(prop!=0xffu && !(inheritable!=0u && (ext_draw!=0u || layout!=0u)))return;
    if(part!=0x10000u)audio_uart_lv_refresh_children_44c9dc(object);
}
