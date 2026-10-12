/* Native RB node creation/parent walk 0x5c37a4/0x5c3838. */
#include <stdint.h>
extern void *audio_uart_lv_heap_alloc(uint32_t); /* selected calloc0x44f730 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_rb.c";
static void fail(uint32_t line,const char *expression) {
    audio_uart_lvgl_log(3u,source,line,"rb_create_node",
                        "Asserted at expression: %s (%s)",expression,"Out of memory");
    for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
void *audio_uart_lv_cache_rb_create_node_5c37a4(const volatile uint32_t *tree) {
    uint8_t *node=(uint8_t *)audio_uart_lv_heap_alloc(0x14u);
    if(node==0) fail(0x150u,"node != NULL");
    void *data=audio_uart_lv_heap_alloc(tree[2]);
    *(volatile uint32_t *)(void *)(node+0x10u)=(uint32_t)(uintptr_t)data;
    if(data==0) fail(0x156u,"node->data != NULL");
    *(volatile uint8_t *)(node+0x0cu)=0u;
    *(volatile uint32_t *)(void *)(node+4u)=0u;
    *(volatile uint32_t *)(void *)(node+8u)=0u;
    return node;
}
void *audio_uart_lv_cache_rb_find_parent_5c3838(const volatile uint32_t *tree,const volatile uint8_t *new_node) {
    uint32_t current=tree[0],parent=tree[0];
    while(current!=0u) {
        uint32_t new_data=*(const volatile uint32_t *)(const void *)(new_node+0x10u);
        uint32_t old_data=*(const volatile uint32_t *)(const void *)(uintptr_t)(current+0x10u);
        int32_t (*compare)(const void *,const void *)=
            (int32_t (*)(const void *,const void *))(uintptr_t)tree[1];
        int32_t order=compare((const void *)(uintptr_t)new_data,
                              (const void *)(uintptr_t)old_data);
        parent=current;
        current=*(const volatile uint32_t *)(const void *)(uintptr_t)(current+(order<0?4u:8u));
    }
    return (void *)(uintptr_t)parent;
}
extern void *audio_uart_font_rb_find(void *,const void *); /* 0x5c3594 */
extern void audio_uart_font_rb_fix_insert(void *,void *); /* 0x5c38cc */
void *audio_uart_font_rb_alloc_insert(void *tree,const void *key) { /* native 0x5c34e4 */
    if(tree==0) {
        audio_uart_lvgl_log(3u,source,0x44u,"lv_rb_insert",
                            "Asserted at expression: %s (%s)",
                            "tree != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    volatile uint32_t *t=(volatile uint32_t *)tree;
    void *existing=audio_uart_font_rb_find(tree,key);
    if(existing!=0) return existing;
    uint8_t *node=(uint8_t *)audio_uart_lv_cache_rb_create_node_5c37a4(t);
    if(node==0) return 0;
    if(t[0]==0u) {
        t[0]=(uint32_t)(uintptr_t)node;
        *(volatile uint32_t *)(void *)node=0u;
        *(volatile uint8_t *)(node+0x0cu)=1u;
    } else {
        uint32_t data=*(volatile uint32_t *)(void *)(node+0x10u);
        *(volatile uint32_t *)(void *)(node+0x10u)=(uint32_t)(uintptr_t)key;
        uint8_t *parent=(uint8_t *)audio_uart_lv_cache_rb_find_parent_5c3838(t,node);
        *(volatile uint32_t *)(void *)node=(uint32_t)(uintptr_t)parent;
        *(volatile uint8_t *)(node+0x0cu)=0u;
        int32_t (*compare)(const void *,const void *)=
            (int32_t (*)(const void *,const void *))(uintptr_t)t[1];
        uint32_t parent_data=*(volatile uint32_t *)(void *)(parent+0x10u);
        uint32_t branch=compare(key,(const void *)(uintptr_t)parent_data)<0?4u:8u;
        *(volatile uint32_t *)(void *)(parent+branch)=(uint32_t)(uintptr_t)node;
        audio_uart_font_rb_fix_insert(tree,node);
        *(volatile uint32_t *)(void *)(node+0x10u)=data;
    }
    return node;
}
