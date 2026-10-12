/* Native LVGL red-black tree init/find/destroy 0x5c3428/0x5c3594/0x5c3716. */
#include <stdint.h>
extern void audio_uart_lv_heap_free(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
extern void *audio_uart_font_rb_remove(void *,void *); /* native 0x5c3600 */
/* Full native5c341c..5c3428; R0 scratch is void. */
extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
void audio_uart_lv_cache_rb_memzero_5c341c(void *object,uint32_t bytes)
{ audio_uart_lv_basic_box_clear_454746(object,0u,bytes); }
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_rb.c";
static void fail(uint32_t line,const char *function,const char *expression,uint32_t simple) {
    if(simple!=0u)
        audio_uart_lvgl_log(3u,source,line,function,
                            "Asserted at expression: %s",expression);
    else
        audio_uart_lvgl_log(3u,source,line,function,
                            "Asserted at expression: %s (%s)",expression,"NULL pointer");
    for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
uint32_t audio_uart_font_rb_initialize(void *tree,uint32_t compare,uint32_t node_size) {
    if(tree==0) fail(0x31u,"lv_rb_init","tree != NULL",0u);
    if(compare==0u) fail(0x32u,"lv_rb_init","compare != NULL",0u);
    if(node_size==0u) fail(0x33u,"lv_rb_init","node_size > 0",1u);
    volatile uint32_t *t=(volatile uint32_t *)tree;
    audio_uart_lv_cache_rb_memzero_5c341c(tree,12u);
    t[0]=0u;
    t[1]=compare;
    t[2]=node_size;
    return 1u;
}
void *audio_uart_font_rb_find(void *tree,const void *key) {
    if(tree==0) fail(0x69u,"lv_rb_find","tree != NULL",0u);
    volatile uint32_t *t=(volatile uint32_t *)tree;
    uint32_t node=t[0];
    while(node!=0u) {
        uint32_t data=*(volatile uint32_t *)(void *)(uintptr_t)(node+0x10u);
        int32_t (*compare)(const void *,const void *)=
            (int32_t (*)(const void *,const void *))(uintptr_t)t[1];
        int8_t order=(int8_t)compare(key,(const void *)(uintptr_t)data);
        if(order==0) return (void *)(uintptr_t)node;
        node=*(volatile uint32_t *)(void *)(uintptr_t)(node+(order<0?4u:8u));
    }
    return 0;
}
void audio_uart_font_rb_clear(void *tree) {
    if(tree==0) fail(0x103u,"lv_rb_destroy","tree != NULL",0u);
    volatile uint32_t *t=(volatile uint32_t *)tree;
    uint32_t node=t[0];
    while(node!=0u) {
        uint32_t left=*(volatile uint32_t *)(void *)(uintptr_t)(node+4u);
        if(left!=0u) {node=left;continue;}
        uint32_t right=*(volatile uint32_t *)(void *)(uintptr_t)(node+8u);
        if(right!=0u) {node=right;continue;}
        uint32_t parent=*(volatile uint32_t *)(void *)(uintptr_t)node;
        if(parent!=0u) {
            volatile uint32_t *p=(volatile uint32_t *)(void *)(uintptr_t)parent;
            if(p[1]==node) p[1]=0u; else p[2]=0u;
        }
        audio_uart_lv_heap_free((void *)(uintptr_t)
            *(volatile uint32_t *)(void *)(uintptr_t)(node+0x10u));
        audio_uart_lv_heap_free((void *)(uintptr_t)node);
        node=parent;
    }
    t[0]=0u;
}
uint32_t audio_uart_font_rb_erase(void *tree,void *node) { /* native 0x5c36c8 */
    if(tree==0) fail(0xe5u,"lv_rb_drop_node","tree != NULL",0u);
    void *data=audio_uart_font_rb_remove(tree,node);
    if(data==0) return 0u;
    audio_uart_lv_heap_free(data);
    return 1u;
}
