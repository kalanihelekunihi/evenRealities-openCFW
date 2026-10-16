/* LVGL animimage frame callback, stock 0x598008..0x598041. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                 const char *,...);
extern void audio_uart_page_498680(void *,const void *);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\widgets\\animimage\\lv_animimage.c";
static const char function[]="index_change";
static const char message[]="dsc is null";
static uint32_t load_u32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
void audio_terminal_voice_anim_exec_598008(void *object,int32_t index) {
    const uint8_t *s=(const uint8_t *)object;
    const uint32_t descriptors=load_u32(s+0xbcu);
    if(descriptors==0u) {
        audio_uart_lvgl_log(2u,path,0xd0u,function,message);
        return;
    }
    const int32_t count=(int8_t)s[0xc0u];
    if(index>=count) index=count-1;
    const uint8_t *entry=(const uint8_t *)(uintptr_t)descriptors+
        (uint32_t)index*4u;
    audio_uart_page_498680(object,(const void *)(uintptr_t)load_u32(entry));
}
