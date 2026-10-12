/* Full native LRU get5c2e4c..5c2f32, link5c2be4..5c2bee,
 * list move-before482d22..482d88. Pointer words wrap at32 bits. */
#include <stdint.h>
extern void *audio_uart_font_cache_entry_at(void *,uint32_t);
extern void *audio_uart_font_rb_find(void *,const void *);
extern void *audio_uart_lv_list_first(void *); /* 482cd8 */
extern void *audio_uart_lv_list_first_482ce4(void *); /* native tail */
extern void *audio_uart_lv_list_next_482cfa(void *,void *); /* native previous */
extern void audio_uart_lv_list_remove(void *,void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static void set_previous(volatile uint32_t *list,uint32_t node,uint32_t value)
{
    if(node!=0u) *(volatile uint32_t *)(uintptr_t)(list[0]+node)=value;
}
static void set_next(volatile uint32_t *list,uint32_t node,uint32_t value)
{
    if(node!=0u) *(volatile uint32_t *)(uintptr_t)(list[0]+node+4u)=value;
}
void audio_uart_lv_list_move_before_482d22(void *list,void *node,void *before)
{
    volatile uint32_t *l=list;
    uint32_t n=(uint32_t)(uintptr_t)node,b=(uint32_t)(uintptr_t)before;
    if(n==b) return;
    uint32_t previous=(uint32_t)(uintptr_t)(b!=0u ?
        audio_uart_lv_list_next_482cfa(list,before) : audio_uart_lv_list_first_482ce4(list));
    if(n==previous) return;
    audio_uart_lv_list_remove(list,node);
    set_next(l,previous,n);
    set_previous(l,n,previous);
    set_previous(l,b,n);
    set_next(l,n,b);
    if(b==0u) l[2]=n;
    if(previous==0u) l[1]=n;
}
void *audio_uart_lv_cache_lru_link_5c2be4(void *cache,void *rb_node)
{
    const volatile uint32_t *c=cache,*n=rb_node;
    uint32_t data=n[4];
    return (void *)(uintptr_t)(c[12]+data-4u);
}
void *audio_uart_font_lru_lookup(void *cache,const void *key,uint32_t context)
{
    (void)context; /* native R2 unused */
    if(cache==0 || key==0) {
        audio_uart_lvgl_log(3u,
            "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache_lru_rb.c",
            cache==0?267u:268u,"get_cb","Asserted at expression: %s (%s)",
            cache==0?"lru != NULL":"key != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    volatile uint32_t *c=cache;
    void *list=(uint8_t *)cache+52u;
    void *first=audio_uart_lv_list_first(list);
    if(first!=0) {
        const volatile uint32_t *first_rb=(void *)(uintptr_t)*(volatile uint32_t *)first;
        uint32_t data=first_rb[4];
        void *entry=audio_uart_font_cache_entry_at((void *)(uintptr_t)data,c[1]);
        int32_t (*compare)(const void *,const void *)=
            (int32_t (*)(const void *,const void *))(uintptr_t)c[4];
        if(compare((const void *)(uintptr_t)data,key)==0) return entry;
    }
    volatile uint32_t *rb=audio_uart_font_rb_find((uint8_t *)cache+40u,key);
    if(rb==0) return 0;
    void *link=audio_uart_lv_cache_lru_link_5c2be4(cache,(void *)rb);
    void *node=(void *)(uintptr_t)*(volatile uint32_t *)link;
    first=audio_uart_lv_list_first(list);
    audio_uart_lv_list_move_before_482d22(list,node,first);
    return audio_uart_font_cache_entry_at((void *)(uintptr_t)rb[4],c[1]);
}
