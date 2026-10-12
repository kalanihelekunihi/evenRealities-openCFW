/* Full native LRU insert5c2b00..5c2be4 and list prepend482b12..482b56. */
#include <stdint.h>
extern void *audio_uart_lv_malloc(uint32_t);
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern void *audio_uart_font_rb_alloc_insert(void *,const void *);
extern uint32_t audio_uart_font_rb_erase(void *,void *);
extern void *audio_uart_font_cache_entry_at(void *,uint32_t);
extern void audio_uart_font_cache_entry_init(void *,void *,uint32_t);
extern void *audio_uart_lv_cache_lru_link_5c2be4(void *,void *);
static void previous(volatile uint32_t *list,uint32_t node,uint32_t value)
{ if(node!=0u) *(volatile uint32_t *)(uintptr_t)(list[0]+node)=value; }
static void next(volatile uint32_t *list,uint32_t node,uint32_t value)
{ if(node!=0u) *(volatile uint32_t *)(uintptr_t)(list[0]+node+4u)=value; }
void *audio_uart_lv_list_prepend_482b12(uint32_t *list)
{
    volatile uint32_t *l=list;
    void *node=audio_uart_lv_malloc(l[0]+8u);
    uint32_t n=(uint32_t)(uintptr_t)node;
    if(node==0) return 0;
    previous(l,n,0u);
    next(l,n,l[1]);
    if(l[1]!=0u) previous(l,l[1],n);
    l[1]=n;
    if(l[2]==0u) l[2]=n;
    return node;
}
void *audio_uart_font_lru_insert(void *cache,const void *key)
{
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache_lru_rb.c";
    if(cache==0 || key==0) {
        audio_uart_lvgl_log(3u,source,cache==0?150u:151u,"alloc_new_node",
            "Asserted at expression: %s (%s)",cache==0?"lru != NULL":"key != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    volatile uint32_t *c=cache;
    void *rb=audio_uart_font_rb_alloc_insert((uint8_t *)cache+40u,key);
    if(rb==0) return 0;
    void *data=(void *)(uintptr_t)((volatile uint32_t *)rb)[4];
    void *entry=audio_uart_font_cache_entry_at(data,c[1]);
    audio_uart_lv_grid_copy_454738(data,key,c[1]);
    void *node=audio_uart_lv_list_prepend_482b12((void *)((uint8_t *)cache+52u));
    if(node==0) {
        audio_uart_font_rb_erase((uint8_t *)cache+40u,rb);
        return 0;
    }
    audio_uart_lv_grid_copy_454738(node,&rb,4u);
    void *link=audio_uart_lv_cache_lru_link_5c2be4(cache,rb);
    audio_uart_lv_grid_copy_454738(link,&node,4u);
    audio_uart_font_cache_entry_init(entry,cache,c[1]);
    return rb;
}
