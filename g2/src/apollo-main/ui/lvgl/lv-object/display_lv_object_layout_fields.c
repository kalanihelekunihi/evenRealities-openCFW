/* Native LV object layout flag/parent/outer-size accessors. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
extern int32_t audio_uart_lv_area_width_451598(const int32_t *);
extern int32_t audio_uart_lv_area_height_4515a4(const int32_t *);
static const char core_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj.c";
static const char pos_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_pos.c";
static const char format[]="Asserted at expression: %s (%s)";
static const char expression[]="obj != NULL";
static const char message[]="NULL pointer";
static const char flag_function[]="lv_obj_has_flag_any";
static const char width_function[]="lv_obj_get_width";
static const char height_function[]="lv_obj_get_height";

static _Noreturn void invalid_object(uint32_t line,const char *source,const char *function)
{
    audio_uart_lvgl_log(3u,source,line,function,format,expression,message);
    for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
uint32_t audio_uart_lv_obj_has_flag_any_43e11c(void *object,uint32_t flags)
{
    if(!object)invalid_object(0x157u,core_source,flag_function);
    return (*(uint32_t *)((uint8_t *)object+0x24u)&flags)!=0u;
}
void *audio_uart_lv_obj_parent_44dca2(void *object)
{
    return object?*(void **)((uint8_t *)object+4u):0;
}
int32_t audio_uart_lv_obj_width_43fd9e(void *object)
{
    if(!object)invalid_object(0x221u,pos_source,width_function);
    return audio_uart_lv_area_width_451598((const int32_t *)((uint8_t *)object+0x14u));
}
int32_t audio_uart_lv_obj_height_43fdda(void *object)
{
    if(!object)invalid_object(0x228u,pos_source,height_function);
    return audio_uart_lv_area_height_4515a4((const int32_t *)((uint8_t *)object+0x14u));
}
