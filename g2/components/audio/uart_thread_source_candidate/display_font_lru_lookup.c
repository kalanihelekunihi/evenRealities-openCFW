/* Native LRU get 0x5c2e4c and LVGL list move-before 0x482d22. */
#include <stdint.h>
extern void *audio_uart_font_cache_entry_at(void *,uint32_t);
extern void *audio_uart_font_rb_find(void *,const void *); /* native 0x5c3594 */
extern void audio_uart_lv_list_remove(void *,void *); /* selected 0x482c0e */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static void list_move_before(uint32_t *list,uint32_t node,uint32_t before) {
    if(node==before) return;
    uint32_t offset=list[0];
    uint32_t previous=before==0u?list[2]:
        *(uint32_t *)(void *)(uintptr_t)(before+offset);
    if(node==previous) return;
    audio_uart_lv_list_remove(list,(void *)(uintptr_t)node);
    *(uint32_t *)(void *)(uintptr_t)(node+offset)=previous;
    *(uint32_t *)(void *)(uintptr_t)(node+offset+4u)=before;
    if(previous!=0u)
        *(uint32_t *)(void *)(uintptr_t)(previous+offset+4u)=node;
    else list[1]=node;
    if(before!=0u)
        *(uint32_t *)(void *)(uintptr_t)(before+offset)=node;
    else list[2]=node;
}
void *audio_uart_font_lru_lookup(void *cache,const void *key) {
    if(cache==0 || key==0) {
        audio_uart_lvgl_log(3u,
            "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache_lru_rb.c",
            cache==0?0x10bu:0x10cu,"get_cb",
            "Asserted at expression: %s (%s)",
            cache==0?"lru != NULL":"key != NULL","NULL pointer");
        for(;;) { /* authenticated native assertion loop */ }
    }
    uint8_t *base=(uint8_t *)cache;
    uint32_t *list=(uint32_t *)(void *)(base+0x34u);
    uint32_t first=list[1];
    if(first!=0u) {
        uint32_t rb=*(uint32_t *)(void *)(uintptr_t)first;
        uint32_t data=*(uint32_t *)(void *)(uintptr_t)(rb+0x10u);
        int32_t (*compare)(const void *,const void *)=
            (int32_t (*)(const void *,const void *))(uintptr_t)
            *(uint32_t *)(void *)(base+0x10u);
        if(compare((const void *)(uintptr_t)data,key)==0)
            return audio_uart_font_cache_entry_at((void *)(uintptr_t)data,
                             *(uint32_t *)(void *)(base+4u));
    }
    uint8_t *rb=(uint8_t *)audio_uart_font_rb_find(base+0x28u,key);
    if(rb==0) return 0;
    uint32_t data=*(uint32_t *)(void *)(rb+0x10u);
    uint32_t link=*(uint32_t *)(void *)(base+0x30u)+data-4u;
    uint32_t node=*(uint32_t *)(void *)(uintptr_t)link;
    list_move_before(list,node,first);
    return audio_uart_font_cache_entry_at((void *)(uintptr_t)data,
                                          *(uint32_t *)(void *)(base+4u));
}
