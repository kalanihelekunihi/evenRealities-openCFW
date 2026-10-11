/* Native LRU drop-all 0x5c315a. */
#include <stdint.h>
extern void *audio_uart_font_cache_entry_at(void *,uint32_t);
extern uint32_t audio_uart_font_cache_has_owner(void *);
extern void audio_uart_font_rb_clear(void *); /* native 0x5c3716 */
extern void audio_uart_lv_list_remove(void *,void *); /* native 0x482c0e */
extern void audio_uart_lv_heap_free(void *); /* native 0x44f758 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
void audio_uart_font_lru_list_clear(void *);
void audio_uart_font_lru_clear(void *cache,uint32_t context) {
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache_lru_rb.c";
    if(cache==0) {
        audio_uart_lvgl_log(3u,source,0x181u,"drop_all_cb",
                            "Asserted at expression: %s (%s)","lru != NULL","NULL pointer");
        for(;;) { /* authenticated native assertion loop */ }
    }
    uint8_t *base=(uint8_t *)cache;
    uint32_t *list=(uint32_t *)(void *)(base+0x34u);
    uint32_t count=0u;
    uint32_t node=list[1];
    while(node!=0u) {
        uint32_t rb=*(uint32_t *)(void *)(uintptr_t)node;
        uint32_t data=*(uint32_t *)(void *)(uintptr_t)(rb+0x10u);
        void *entry=audio_uart_font_cache_entry_at((void *)(uintptr_t)data,
                            *(uint32_t *)(void *)(base+4u));
        uint32_t refs=audio_uart_font_cache_has_owner(entry);
        if(refs==0u) {
            uint32_t callback=*(uint32_t *)(void *)(base+0x18u);
            ((void (*)(void *,uint32_t))(uintptr_t)callback)(
                            (void *)(uintptr_t)data,context);
        } else {
            audio_uart_lvgl_log(2u,source,0x191u,"drop_all_cb",
                                "entry (%p) is still referenced (%d)",entry,refs);
            ++count;
        }
        node=*(uint32_t *)(void *)(uintptr_t)(node+list[0]+4u);
    }
    if(count!=0u)
        audio_uart_lvgl_log(2u,source,0x196u,"drop_all_cb",
                            "%d entries are still referenced",count);
    audio_uart_font_rb_clear(base+0x28u);
    audio_uart_font_lru_list_clear(base+0x34u);
    *(uint32_t *)(void *)(base+0x0cu)=0u;
}
void audio_uart_font_lru_list_clear(void *list) { /* native 0x482da4/0x482c9a */
    uint32_t *header=(uint32_t *)list;
    uint32_t node=header[1];
    while(node!=0u) {
        uint32_t next=*(uint32_t *)(void *)(uintptr_t)(node+header[0]+4u);
        audio_uart_lv_list_remove(list,(void *)(uintptr_t)node);
        audio_uart_lv_heap_free((void *)(uintptr_t)node);
        node=next;
    }
}
