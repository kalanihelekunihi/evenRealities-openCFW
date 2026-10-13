/* Entire native lv_obj_refr_size43f1a4..43f4bf (796bytes).
 * Source: pinned Ambiq LVGL lv_obj_pos.c87-209 and original native assembly/lift.
 * Historical basic_invalidate symbol retained to resolve its existing callers.
 * UNADMITTED: native comparison/selected-TU/API-declaration gates remain. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern void *audio_uart_lv_obj_parent_44dca2(void *);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern int32_t audio_uart_lv_style_width_43eea6(void *,uint32_t);
extern int32_t audio_uart_lv_style_min_width_43eeb0(void *,uint32_t);
extern int32_t audio_uart_lv_style_max_width_43eeba(void *,uint32_t);
extern int32_t audio_uart_lv_style_height_43eec4(void *,uint32_t);
extern int32_t audio_uart_lv_style_min_height_43eece(void *,uint32_t);
extern int32_t audio_uart_lv_style_max_height_43eed8(void *,uint32_t);
extern int32_t audio_uart_lv_obj_content_width_43fe16(void *,uint32_t,uint32_t,uint32_t);
extern int32_t audio_uart_lv_obj_content_height_43fe70(void *,uint32_t,uint32_t,uint32_t);
extern int32_t audio_uart_lv_calc_content_width_440a3c(void *);
extern int32_t audio_uart_lv_calc_content_height_440c2e(void *);
extern int32_t audio_uart_lv_style_pad_left_43efc6(void *,uint32_t,uint32_t,uint32_t);
extern int32_t audio_uart_lv_style_pad_right_43eff4(void *,uint32_t);
extern int32_t audio_uart_lv_style_pad_top_43f022(void *,uint32_t,uint32_t,uint32_t);
extern int32_t audio_uart_lv_style_pad_bottom_43f050(void *,uint32_t);
extern int32_t audio_uart_lv_style_margin_left_43ef84(void *,uint32_t);
extern int32_t audio_uart_lv_style_margin_right_43ef8e(void *,uint32_t);
extern int32_t audio_uart_lv_style_margin_top_43ef70(void *,uint32_t);
extern int32_t audio_uart_lv_style_margin_bottom_43ef7a(void *,uint32_t);
extern int32_t audio_uart_lv_clamp_width_4408d6(int32_t,int32_t,int32_t,int32_t);
extern int32_t audio_uart_lv_clamp_height_440968(int32_t,int32_t,int32_t,int32_t);
extern void audio_uart_display_size_changed(void *); /* native440656 invalidate */
extern void audio_uart_lv_obj_coords_43fc2a(const void *,void *);
extern void audio_uart_lv_obj_content_coords_43feca(void *,void *);
extern uint32_t audio_uart_lv_area_contains_450f28(const int32_t *,const int32_t *,uint32_t);
extern void audio_uart_lv_scrollbar_invalidate_44f2ca(void *);
extern uint8_t audio_uart_lv_style_base_dir_43efba(void *,uint32_t);
extern uint32_t audio_uart_lv_obj_event_451670(void *,uint32_t,void *);
extern void audio_uart_lv_refresh_draw_452d42(void *);

static uint16_t lv338_flags(const void *object)
{return *(const volatile uint16_t *)((const uint8_t *)object+42u);}
static int32_t lv338_coord(const void *object,uint32_t offset)
{return *(const volatile int32_t *)((const uint8_t *)object+offset);}
static void lv338_coordinate(void *object,uint32_t offset,int32_t value)
{*(volatile int32_t *)((uint8_t *)object+offset)=value;}
static int32_t lv338_add(int32_t a,int32_t b){return (int32_t)((uint32_t)a+(uint32_t)b);}
static int32_t lv338_sub(int32_t a,int32_t b){return (int32_t)((uint32_t)a-(uint32_t)b);}
static uint32_t lv338_is_percentage(uint32_t encoded)
{return (encoded&0x60000000u)==0x20000000u && (int32_t)(encoded&0x9fffffffu)<0x1fffffff;}
static int32_t lv338_percentage_size(uint32_t encoded,int32_t reference)
{
    int32_t plain=(int32_t)(encoded&0x9fffffffu);
    int32_t factor=plain<0x10000000?plain:(int32_t)(0x0fffffffu-(uint32_t)plain);
    int32_t product=(int32_t)((uint32_t)reference*(uint32_t)factor);
    return product/100;
}
static _Noreturn void lv338_null(void)
{
    audio_uart_lvgl_log(3u,"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_pos.c",
        89u,"lv_obj_refr_size","Asserted at expression: %s (%s)","obj != NULL","NULL pointer");
    for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
uint32_t audio_uart_lv_basic_invalidate_43f1a4(void *object)
{
    if(object==0)lv338_null();
    if((lv338_flags(object)&0xc00u)==0xc00u)return 0u;
    void *parent=audio_uart_lv_obj_parent_44dca2(object);
    if(parent==0)return 0u;
    int32_t width,height;
    if((lv338_flags(object)&0x800u)!=0u)width=audio_uart_lv_obj_width_43fd9e(object);
    else{
        uint32_t encoded=(uint32_t)audio_uart_lv_style_width_43eea6(object,0u);
        uint32_t percentage=lv338_is_percentage(encoded);
        int32_t reference=audio_uart_lv_obj_content_width_43fe16(parent,0u,0u,0u);
        width=(int32_t)encoded;
        if(encoded==0x3fffffffu)width=audio_uart_lv_calc_content_width_440a3c(object);
        else if(percentage){
            if((lv338_flags(parent)&0x800u)==0u &&
               (uint32_t)audio_uart_lv_style_width_43eea6(parent,0u)==0x3fffffffu){
                int32_t left=audio_uart_lv_style_pad_left_43efc6(object,0u,0u,0u);
                int32_t right=audio_uart_lv_style_pad_right_43eff4(object,0u);width=lv338_add(right,left);
            }else{
                int32_t size=lv338_percentage_size(encoded,reference);
                int32_t left=audio_uart_lv_style_margin_left_43ef84(object,0u);
                int32_t right=audio_uart_lv_style_margin_right_43ef8e(object,0u);
                width=lv338_sub(lv338_sub(size,left),right);
            }
        }
        int32_t minimum=audio_uart_lv_style_min_width_43eeb0(object,0u);
        int32_t maximum=audio_uart_lv_style_max_width_43eeba(object,0u);
        width=audio_uart_lv_clamp_width_4408d6(width,minimum,maximum,reference);
    }
    if((lv338_flags(object)&0x400u)!=0u)height=audio_uart_lv_obj_height_43fdda(object);
    else{
        uint32_t encoded=(uint32_t)audio_uart_lv_style_height_43eec4(object,0u);
        uint32_t percentage=lv338_is_percentage(encoded);
        int32_t reference=audio_uart_lv_obj_content_height_43fe70(parent,0u,0u,0u);
        height=(int32_t)encoded;
        if(encoded==0x3fffffffu)height=audio_uart_lv_calc_content_height_440c2e(object);
        else if(percentage){
            if((lv338_flags(parent)&0x400u)==0u &&
               (uint32_t)audio_uart_lv_style_height_43eec4(parent,0u)==0x3fffffffu){
                int32_t top=audio_uart_lv_style_pad_top_43f022(object,0u,0u,0u);
                int32_t bottom=audio_uart_lv_style_pad_bottom_43f050(object,0u);height=lv338_add(bottom,top);
            }else{
                int32_t size=lv338_percentage_size(encoded,reference);
                int32_t top=audio_uart_lv_style_margin_top_43ef70(object,0u);
                int32_t bottom=audio_uart_lv_style_margin_bottom_43ef7a(object,0u);
                height=lv338_sub(lv338_sub(size,top),bottom);
            }
        }
        int32_t minimum=audio_uart_lv_style_min_height_43eece(object,0u);
        int32_t maximum=audio_uart_lv_style_max_height_43eed8(object,0u);
        height=audio_uart_lv_clamp_height_440968(height,minimum,maximum,reference);
    }
    if(audio_uart_lv_obj_width_43fd9e(object)==width &&
       audio_uart_lv_obj_height_43fdda(object)==height)return 0u;
    audio_uart_display_size_changed(object);
    int32_t original[4],parent_fit[4];
    audio_uart_lv_obj_coords_43fc2a(object,original);
    audio_uart_lv_obj_content_coords_43feca(parent,parent_fit);
    uint8_t on1=(uint8_t)audio_uart_lv_area_contains_450f28(original,parent_fit,0u);
    if(on1==0u)audio_uart_lv_scrollbar_invalidate_44f2ca(parent);
    lv338_coordinate(object,32u,lv338_sub(lv338_add(height,lv338_coord(object,24u)),1));
    if(audio_uart_lv_style_base_dir_43efba(object,0u)==1u)
        lv338_coordinate(object,20u,lv338_add(lv338_sub(lv338_coord(object,28u),width),1));
    else lv338_coordinate(object,28u,lv338_sub(lv338_add(width,lv338_coord(object,20u)),1));
    (void)audio_uart_lv_obj_event_451670(object,49u,original);
    (void)audio_uart_lv_obj_event_451670(parent,42u,object);
    audio_uart_display_size_changed(object);
    *(volatile uint16_t *)((uint8_t *)object+42u)=(uint16_t)(lv338_flags(object)|2u);
    uint8_t on2=(uint8_t)audio_uart_lv_area_contains_450f28((const int32_t *)((uint8_t *)object+20u),parent_fit,0u);
    if(on1!=0u || on2!=0u)audio_uart_lv_scrollbar_invalidate_44f2ca(parent);
    audio_uart_lv_refresh_draw_452d42(object);
    return 1u;
}
