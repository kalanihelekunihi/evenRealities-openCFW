/* Native LV object content dimensions 0x43fe16 and 0x43fe70. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern int32_t audio_uart_lv_style_pad_left_43efc6(void *,uint32_t,uint32_t,uint32_t);
extern int32_t audio_uart_lv_style_pad_right_43eff4(void *,uint32_t);
extern int32_t audio_uart_lv_style_pad_top_43f022(void *,uint32_t,uint32_t,uint32_t);
extern int32_t audio_uart_lv_style_pad_bottom_43f050(void *,uint32_t);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_pos.c";
static const char format[]="Asserted at expression: %s (%s)";
static const char expression[]="obj != NULL";
static const char message[]="NULL pointer";
static _Noreturn void invalid_object(uint32_t line,const char *function)
{
    audio_uart_lvgl_log(3u,source,line,function,format,expression,message);
    for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
int32_t audio_uart_lv_obj_content_width_43fe16(void *object,uint32_t unused,uint32_t r2,uint32_t r3)
{
    (void)unused;
    if(!object)invalid_object(0x22fu,"lv_obj_get_content_width");
    int32_t start=audio_uart_lv_style_pad_left_43efc6(object,0u,r2,r3);
    int32_t end=audio_uart_lv_style_pad_right_43eff4(object,0u);
    return (int32_t)((uint32_t)audio_uart_lv_obj_width_43fd9e(object)-(uint32_t)start-(uint32_t)end);
}
int32_t audio_uart_lv_obj_content_height_43fe70(void *object,uint32_t unused,uint32_t r2,uint32_t r3)
{
    (void)unused;
    if(!object)invalid_object(0x239u,"lv_obj_get_content_height");
    int32_t start=audio_uart_lv_style_pad_top_43f022(object,0u,r2,r3);
    int32_t end=audio_uart_lv_style_pad_bottom_43f050(object,0u);
    return (int32_t)((uint32_t)audio_uart_lv_obj_height_43fdda(object)-(uint32_t)start-(uint32_t)end);
}
