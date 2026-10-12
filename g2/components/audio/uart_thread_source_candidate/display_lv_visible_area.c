/* Native LVGL lv_obj_is_visible/invalidate-area clipping 0x4406c4.
 * The display screen comparisons, parent clipping and scrollbar effect
 * retain the product's actual child ABIs. */
#include <stdint.h>
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *,uint32_t);
extern void *audio_uart_lv_object_screen(void *);
extern void *audio_uart_lv_display_for_object(void *);
extern void *audio_uart_display_active_screen_get(void *); /* selected 0x44fc62 */
extern void *audio_uart_lv_display_previous_screen_44fc90(void *);
extern void *audio_uart_lv_display_bottom_layer_44fd38(void *);
extern void *audio_uart_lv_display_top_layer_44fcbe(void *);
extern void *audio_uart_lv_display_system_layer_44fcfc(void *);
extern uint32_t audio_uart_lv_draw_size_get_452dc8(void *); /* selected */
extern void audio_uart_lv_area_copy_4530fc(int32_t *,const int32_t *); /* same body as native 0x43ee94 */
extern void audio_uart_lv_area_expand_450b98(int32_t *,int32_t,int32_t);
extern uint32_t audio_uart_lv_area_intersect_450bcc(int32_t *,const int32_t *,const int32_t *);
extern uint32_t audio_uart_lv_object_scrollbar_visible_440a18(void *);
extern void audio_uart_lv_object_scrollbar_area_440494(void *,const int32_t *,uint32_t);
extern void *audio_uart_lv_obj_has_parent_44dca2(void *); /* selected */

uint32_t audio_uart_lv_visible_area(void *object,int32_t *area) {
    if(audio_uart_lv_obj_has_flag_43e0e0(object,1u)!=0u)return 0u;
    void *screen=audio_uart_lv_object_screen(object);
    void *display=audio_uart_lv_display_for_object(screen);
    if(screen!=audio_uart_display_active_screen_get(display) &&
       screen!=audio_uart_lv_display_previous_screen_44fc90(display) &&
       screen!=audio_uart_lv_display_bottom_layer_44fd38(display) &&
       screen!=audio_uart_lv_display_top_layer_44fcbe(display) &&
       screen!=audio_uart_lv_display_system_layer_44fcfc(display))return 0u;
    int32_t viewport[4];
    int32_t ext=(int32_t)audio_uart_lv_draw_size_get_452dc8(object);
    audio_uart_lv_area_copy_4530fc(viewport,(const int32_t *)((uint8_t *)object+0x14u));
    audio_uart_lv_area_expand_450b98(viewport,ext,ext);
    if(audio_uart_lv_area_intersect_450bcc(area,area,viewport)==0u)return 0u;
    if(audio_uart_lv_object_scrollbar_visible_440a18(object)!=0u)
        audio_uart_lv_object_scrollbar_area_440494(object,area,1u);
    for(uint8_t *parent=(uint8_t *)audio_uart_lv_obj_has_parent_44dca2(object);
        parent!=0;parent=(uint8_t *)audio_uart_lv_obj_has_parent_44dca2(parent)) {
        if(audio_uart_lv_obj_has_flag_43e0e0(parent,1u)!=0u)return 0u;
        int32_t clip[4];
        __builtin_memcpy(clip,parent+0x14u,16u);
        if(audio_uart_lv_obj_has_flag_43e0e0(parent,0x100000u)!=0u) {
            int32_t size=(int32_t)audio_uart_lv_draw_size_get_452dc8(parent);
            audio_uart_lv_area_expand_450b98(clip,size,size);
        }
        if(audio_uart_lv_object_scrollbar_visible_440a18(parent)!=0u)
            audio_uart_lv_object_scrollbar_area_440494(parent,clip,1u);
        if(audio_uart_lv_area_intersect_450bcc(area,area,clip)==0u)return 0u;
    }
    return 1u;
}
