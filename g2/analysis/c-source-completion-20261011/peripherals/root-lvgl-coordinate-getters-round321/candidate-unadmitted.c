/* Complete native43fc2a..43fc63 and43feca..43ff43; pinned lv_obj_pos.c.
 * Genuine native null assertion: diagnostic call then faulting volatile word write.
 * No assertion-body placeholder or fabricated successful return. */
#include <stdint.h>
#include <stddef.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern void audio_uart_lv_area_copy_43ee94(void *,const void *);
extern int32_t audio_uart_lv_style_pad_left_43efc6(void *,uint32_t,uint32_t,uint32_t);
extern int32_t audio_uart_lv_style_pad_right_43eff4(void *,uint32_t);
extern int32_t audio_uart_lv_style_pad_top_43f022(void *,uint32_t,uint32_t,uint32_t);
extern int32_t audio_uart_lv_style_pad_bottom_43f050(void *,uint32_t);
static const char lv321_format[]="Asserted at expression: %s (%s)";
static const char lv321_expression[]="obj != NULL";
static const char lv321_message[]="NULL pointer";
static const char lv321_coords_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_pos.c";
static const char lv321_coords_function[]="lv_obj_get_coords";
static const char lv321_content_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_pos.c";
static const char lv321_content_function[]="lv_obj_get_content_coords";
static _Noreturn void lv321_assert_null(uint32_t line,const char *function,const char *file)
{
 audio_uart_lvgl_log(3u,file,line,function,lv321_format,lv321_expression,lv321_message);
 for(;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu=0u;
}
void audio_uart_lv_obj_coords_43fc2a(const void *object,void *area)
{
 if(object==NULL)lv321_assert_null(480u,lv321_coords_function,lv321_coords_file);
 audio_uart_lv_area_copy_43ee94(area,(const uint8_t *)object+20u);
}
void audio_uart_lv_obj_content_coords_43feca(void *object,void *area)
{
 if(object==NULL)lv321_assert_null(579u,lv321_content_function,lv321_content_file);
 audio_uart_lv_obj_coords_43fc2a(object,area);
 volatile uint32_t *a=area;
 uint32_t space=(uint32_t)audio_uart_lv_style_pad_left_43efc6(object,0u,0u,0u);a[0]=a[0]+space;
 space=(uint32_t)audio_uart_lv_style_pad_right_43eff4(object,0u);a[2]=a[2]-space;
 space=(uint32_t)audio_uart_lv_style_pad_top_43f022(object,0u,0u,0u);a[1]=a[1]+space;
 space=(uint32_t)audio_uart_lv_style_pad_bottom_43f050(object,0u);a[3]=a[3]-space;
}
