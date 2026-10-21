/* Native LVGL lv_obj_invalidate 0x440656 with authenticated geometry data.
 * Its area invalidator 0x4405d4 remains an explicit connected code child. */
#include <stdint.h>

extern void audio_uart_display_invalidate_area(void *,const int32_t *); /* 0x4405d4 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...); /* 0x44d25c */
static const char source_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_pos.c";
static const char function[]="lv_obj_invalidate";
static const char asserted[]="Asserted at expression: %s (%s)";
static const char expression[]="obj != NULL";
static const char null_pointer[]="NULL pointer";

void audio_uart_display_size_changed(void *object) {
    if(object==0) {
        audio_uart_lvgl_log(3u,source_path,852u,function,asserted,expression,null_pointer);
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    const uint8_t *o=(const uint8_t *)object;
    const uint8_t *parent=*(const uint8_t *const *)(const void *)(o+8u);
    int32_t shift=parent==0 ? 0 : *(const int32_t *)(const void *)(parent+0x2cu);
    int32_t area[4];
    for(uint32_t i=0;i<4u;i++) area[i]=*(const int32_t *)(const void *)(o+20u+4u*i);
    area[0]-=shift;
    area[1]-=shift;
    area[2]+=shift;
    area[3]+=shift;
    audio_uart_display_invalidate_area(object,area);
}
