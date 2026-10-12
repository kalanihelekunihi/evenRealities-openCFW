/* Native red-black tree remove 0x5c3600, including transplant and successor. */
#include <stdint.h>
extern void audio_uart_lv_heap_free(void *);
extern void audio_uart_font_rb_fix_remove(void *,void *,void *); /* 0x5c3976 */
static uint32_t get(const void *node,uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)((const uint8_t *)node+offset);
}
static void set(void *node,uint32_t offset,uint32_t value) {
    *(volatile uint32_t *)(void *)((uint8_t *)node+offset)=value;
}
void *audio_uart_lv_cache_rb_leftmost_5c3798(void *node) { /* native 0x5c3798 */
    uint8_t *n=(uint8_t *)node;
    while(get(n,4u)!=0u) n=(uint8_t *)(uintptr_t)get(n,4u);
    return n;
}
void *audio_uart_font_rb_remove(void *tree,void *node) {
    uint8_t *t=(uint8_t *)tree;
    uint8_t *n=(uint8_t *)node;
    uint32_t left=get(n,4u),right=get(n,8u);
    if(left==0u || right==0u) {
        uint32_t child=right!=0u?right:left;
        uint32_t parent=get(n,0u);
        uint8_t color=*(volatile uint8_t *)(n+0x0cu);
        if(child!=0u) set((void *)(uintptr_t)child,0u,parent);
        if(parent==0u) set(t,0u,child);
        else if(get((void *)(uintptr_t)parent,4u)==(uint32_t)(uintptr_t)n)
            set((void *)(uintptr_t)parent,4u,child);
        else set((void *)(uintptr_t)parent,8u,child);
        if(color==1u) audio_uart_font_rb_fix_remove(t,
            (void *)(uintptr_t)child,(void *)(uintptr_t)parent);
    } else {
        uint8_t *successor=(uint8_t *)audio_uart_lv_cache_rb_leftmost_5c3798((void *)(uintptr_t)right);
        uint32_t parent=get(n,0u);
        if(parent==0u) set(t,0u,(uint32_t)(uintptr_t)successor);
        else if(get((void *)(uintptr_t)parent,4u)==(uint32_t)(uintptr_t)n)
            set((void *)(uintptr_t)parent,4u,(uint32_t)(uintptr_t)successor);
        else set((void *)(uintptr_t)parent,8u,(uint32_t)(uintptr_t)successor);
        uint32_t child=get(successor,8u);
        uint32_t old_parent=get(successor,0u);
        uint8_t old_color=*(volatile uint8_t *)(successor+0x0cu);
        uint32_t fix_parent=old_parent;
        if(old_parent==(uint32_t)(uintptr_t)n) fix_parent=(uint32_t)(uintptr_t)successor;
        else {
            if(child!=0u) set((void *)(uintptr_t)child,0u,old_parent);
            set((void *)(uintptr_t)old_parent,4u,child);
            set(successor,8u,right);
            set((void *)(uintptr_t)right,0u,(uint32_t)(uintptr_t)successor);
        }
        set(successor,0u,parent);
        *(volatile uint8_t *)(successor+0x0cu)=*(volatile uint8_t *)(n+0x0cu);
        set(successor,4u,left);
        set((void *)(uintptr_t)left,0u,(uint32_t)(uintptr_t)successor);
        if(old_color==1u) audio_uart_font_rb_fix_remove(t,
            (void *)(uintptr_t)child,(void *)(uintptr_t)fix_parent);
    }
    void *data=(void *)(uintptr_t)get(n,0x10u);
    audio_uart_lv_heap_free(n);
    return data;
}
