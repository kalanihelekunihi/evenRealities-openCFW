/* Native lv_style_remove_prop 0x4827b0: allocate compacted values and
 * property bytes, retain first-match removal and constant-style diagnostic. */
#include <stdint.h>
extern void *audio_uart_lv_malloc(uint32_t); /* selected 0x44f718 */
extern void audio_uart_lv_heap_free(void *); /* selected 0x44f758 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_style.c";
uint32_t audio_uart_lv_style_notify_4827b0(void *style,uint32_t property) {
    uint8_t *s=(uint8_t *)style;
    if(s[8u]==0xffu) {
        audio_uart_lvgl_log(3u,path,0x117u,"lv_style_remove_prop",
                            "Cannot remove prop from const style");
        return 0u;
    }
    uint32_t count=s[8u];
    if(count==0u)return 0u;
    uint8_t *old=*(uint8_t **)(void *)s;
    uint8_t *old_props=old+count*4u;
    for(uint32_t i=0;i<count;i++) {
        if((int8_t)old_props[i]!=(int8_t)property)continue;
        uint8_t *next=(uint8_t *)audio_uart_lv_malloc((count-1u)*5u);
        if(next==0)return 0u;
        *(uint8_t **)(void *)s=next;
        uint32_t remaining=count-1u;
        s[8u]=(uint8_t)remaining;
        uint32_t dst=0u;
        for(uint32_t src=0;src<count;src++) {
            if((int8_t)old_props[src]==(int8_t)property)continue;
            __builtin_memcpy(next+dst*4u,old+src*4u,4u);
            next[remaining*4u+dst]=old_props[src];
            dst++;
        }
        audio_uart_lv_heap_free(old);
        return 1u;
    }
    return 0u;
}
