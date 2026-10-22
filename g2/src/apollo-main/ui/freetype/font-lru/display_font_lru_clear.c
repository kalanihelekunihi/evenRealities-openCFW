/* Full native LRU drop-all5c315a..5c3222 and list cleanup482c9a..482cd8,
 * wrapper482da4..482dae. */
#include <stdint.h>
extern void *audio_uart_font_cache_entry_at(void *,uint32_t);
extern uint32_t audio_uart_font_cache_has_owner(void *);
extern void audio_uart_font_rb_clear(void *);
extern void *audio_uart_lv_list_first(void *);
extern void *audio_uart_lv_list_next(void *,void *);
extern void audio_uart_lv_list_remove(void *,void *);
extern void audio_uart_lv_heap_free(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
/* Retired: stock 0x482da4 is upstream lv_ll_clear (lvgl/src/misc/lv_ll.c); this name is a link alias. */
void audio_uart_font_lru_list_clear(void *list);
/* Stock 0x5C315A (drop_all_cb; upstream third-party/upstream/lvgl/src/misc/cache/lv_cache_lru_rb.c) */
void audio_uart_font_lru_clear(void *cache,uint32_t context)
{
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache_lru_rb.c";
    if(cache==0) {
        audio_uart_lvgl_log(3u,source,385u,"drop_all_cb",
            "Asserted at expression: %s (%s)","lru != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    volatile uint32_t *c=cache;
    void *list=(uint8_t *)cache+52u;
    uint32_t count=0u;
    void *node=audio_uart_lv_list_first(list);
    while(node!=0) {
        const volatile uint32_t *rb=(void *)(uintptr_t)*(volatile uint32_t *)node;
        uint32_t data=rb[4];
        void *entry=audio_uart_font_cache_entry_at((void *)(uintptr_t)data,c[1]);
        if(audio_uart_font_cache_has_owner(entry)==0u) {
            void (*destroy)(void *,uint32_t)=(void (*)(void *,uint32_t))(uintptr_t)c[6];
            destroy((void *)(uintptr_t)data,context);
        } else {
            audio_uart_lvgl_log(2u,source,401u,"drop_all_cb",
                "entry (%p) is still referenced (%d)",entry,
                audio_uart_font_cache_has_owner(entry));
            count=count+1u;
        }
        node=audio_uart_lv_list_next(list,node);
    }
    if(count!=0u) audio_uart_lvgl_log(2u,source,406u,"drop_all_cb",
        "%d entries are still referenced",count);
    audio_uart_font_rb_clear((uint8_t *)cache+40u);
    audio_uart_font_lru_list_clear(list);
    c[3]=0u;
}
