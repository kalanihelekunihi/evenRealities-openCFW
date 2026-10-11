/* Native LRU RB/list insertion 0x5c2b00 and LVGL list prepend 0x482b12. */
#include <stdint.h>
extern void *audio_uart_lv_malloc(uint32_t);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern void *audio_uart_font_rb_alloc_insert(void *,const void *); /* 0x5c34e4 */
extern uint32_t audio_uart_font_rb_erase(void *,void *); /* 0x5c36c8 */
extern void *audio_uart_font_cache_entry_at(void *,uint32_t); /* 0x4d5452 */
extern void audio_uart_font_cache_entry_init(void *,void *,uint32_t); /* 0x4d547e */
static void *list_prepend(uint32_t *list) { /* native 0x482b12 */
    uint8_t *node=(uint8_t *)audio_uart_lv_malloc(list[0]+8u);
    if(node==0) return 0;
    uint32_t offset=list[0];
    *(uint32_t *)(void *)(node+offset)=0u;
    *(uint32_t *)(void *)(node+offset+4u)=list[1];
    if(list[1]!=0u)
        *(uint32_t *)(void *)(uintptr_t)(list[1]+offset)=(uint32_t)(uintptr_t)node;
    list[1]=(uint32_t)(uintptr_t)node;
    if(list[2]==0u) list[2]=(uint32_t)(uintptr_t)node;
    return node;
}
void *audio_uart_font_lru_insert(void *cache,const void *key) {
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache_lru_rb.c";
    if(cache==0 || key==0) {
        audio_uart_lvgl_log(3u,source,cache==0?0x96u:0x97u,"alloc_new_node",
                            "Asserted at expression: %s (%s)",
                            cache==0?"lru != NULL":"key != NULL","NULL pointer");
        for(;;) { /* authenticated native assertion loop */ }
    }
    uint8_t *base=(uint8_t *)cache;
    uint8_t *rb=(uint8_t *)audio_uart_font_rb_alloc_insert(base+0x28u,key);
    if(rb==0) return 0;
    uint8_t *data=*(uint8_t **)(void *)(rb+0x10u);
    uint32_t offset=*(uint32_t *)(void *)(base+4u);
    void *entry=audio_uart_font_cache_entry_at(data,offset);
    (void)audio_queue_copy_bytes(data,key,offset);
    uint8_t *list=(uint8_t *)list_prepend((uint32_t *)(void *)(base+0x34u));
    if(list==0) {
        (void)audio_uart_font_rb_erase(base+0x28u,rb);
        return 0;
    }
    *(uint32_t *)(void *)list=(uint32_t)(uintptr_t)rb;
    uint8_t *link=(uint8_t *)(uintptr_t)(*(uint32_t *)(void *)(base+0x30u)+
                            *(uint32_t *)(void *)(rb+0x10u)-4u);
    *(uint32_t *)(void *)link=(uint32_t)(uintptr_t)list;
    audio_uart_font_cache_entry_init(entry,cache,offset);
    return rb;
}
