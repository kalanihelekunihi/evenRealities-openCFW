/* Native RB rotations0x5c3860/0x5c3896 and insert fix-up0x5c38cc. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static uint32_t get(const void *node,uint32_t offset) {
    return *(const uint32_t *)(const void *)((const uint8_t *)node+offset);
}
static void set(void *node,uint32_t offset,uint32_t value) {
    *(uint32_t *)(void *)((uint8_t *)node+offset)=value;
}
static uint8_t color(const void *node) { return ((const uint8_t *)node)[0x0cu]; }
static void set_color(void *node,uint8_t value) { ((uint8_t *)node)[0x0cu]=value; }
static void rotate_right(void *tree,void *node) { /* 0x5c3860 */
    uint8_t *n=(uint8_t *)node;
    uint8_t *pivot=(uint8_t *)(uintptr_t)get(n,4u);
    uint32_t middle=get(pivot,8u);
    set(n,4u,middle);
    if(middle!=0u) set((void *)(uintptr_t)middle,0u,(uint32_t)(uintptr_t)n);
    uint32_t parent=get(n,0u);
    set(pivot,0u,parent);
    if(parent==0u) set(tree,0u,(uint32_t)(uintptr_t)pivot);
    else if(get((void *)(uintptr_t)parent,8u)==(uint32_t)(uintptr_t)n)
        set((void *)(uintptr_t)parent,8u,(uint32_t)(uintptr_t)pivot);
    else set((void *)(uintptr_t)parent,4u,(uint32_t)(uintptr_t)pivot);
    set(pivot,8u,(uint32_t)(uintptr_t)n);
    set(n,0u,(uint32_t)(uintptr_t)pivot);
}
static void rotate_left(void *tree,void *node) { /* 0x5c3896 */
    uint8_t *n=(uint8_t *)node;
    uint8_t *pivot=(uint8_t *)(uintptr_t)get(n,8u);
    uint32_t middle=get(pivot,4u);
    set(n,8u,middle);
    if(middle!=0u) set((void *)(uintptr_t)middle,0u,(uint32_t)(uintptr_t)n);
    uint32_t parent=get(n,0u);
    set(pivot,0u,parent);
    if(parent==0u) set(tree,0u,(uint32_t)(uintptr_t)pivot);
    else if(get((void *)(uintptr_t)parent,4u)==(uint32_t)(uintptr_t)n)
        set((void *)(uintptr_t)parent,4u,(uint32_t)(uintptr_t)pivot);
    else set((void *)(uintptr_t)parent,8u,(uint32_t)(uintptr_t)pivot);
    set(pivot,4u,(uint32_t)(uintptr_t)n);
    set(n,0u,(uint32_t)(uintptr_t)pivot);
}
void audio_uart_font_rb_fix_insert(void *tree,void *node) { /* native 0x5c38cc */
    uint8_t *n=(uint8_t *)node;
    while(get(n,0u)!=0u &&
          color((void *)(uintptr_t)get(n,0u))==0u) {
        uint8_t *parent=(uint8_t *)(uintptr_t)get(n,0u);
        uint8_t *grand=(uint8_t *)(uintptr_t)get(parent,0u);
        if((uint32_t)(uintptr_t)parent==get(grand,4u)) {
            uint32_t uncle=get(grand,8u);
            if(uncle!=0u && color((void *)(uintptr_t)uncle)==0u) {
                set_color((void *)(uintptr_t)uncle,1u);
                set_color(parent,1u);
                set_color(grand,0u);
                n=grand;
            } else {
                uint8_t *pivot=parent;
                if((uint32_t)(uintptr_t)n==get(parent,8u)) {
                    rotate_left(tree,parent);
                    pivot=n;
                    n=parent;
                }
                set_color(pivot,1u);
                set_color(grand,0u);
                rotate_right(tree,grand);
            }
        } else {
            uint32_t uncle=get(grand,4u);
            if(uncle!=0u && color((void *)(uintptr_t)uncle)==0u) {
                set_color((void *)(uintptr_t)uncle,1u);
                set_color(parent,1u);
                set_color(grand,0u);
                n=grand;
            } else {
                uint8_t *pivot=parent;
                if((uint32_t)(uintptr_t)n==get(parent,4u)) {
                    rotate_right(tree,parent);
                    pivot=n;
                    n=parent;
                }
                set_color(pivot,1u);
                set_color(grand,0u);
                rotate_left(tree,grand);
            }
        }
    }
    set_color((void *)(uintptr_t)get(tree,0u),1u);
}

static uint8_t black_or_color(uint32_t node) {
    return node==0u?1u:color((void *)(uintptr_t)node);
}
static void blacken(uint32_t node) {
    if(node!=0u) set_color((void *)(uintptr_t)node,1u);
}
void audio_uart_font_rb_fix_remove(void *tree,void *child,void *parent) { /* 0x5c3976 */
    if(tree==0) {
        audio_uart_lvgl_log(3u,
            "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_rb.c",
            0x1e7u,"rb_delete_color","Asserted at expression: %s (%s)",
            "tree != NULL","NULL pointer");
        for(;;) { /* authenticated native assertion loop */ }
    }
    uint32_t x=(uint32_t)(uintptr_t)child;
    uint32_t p=(uint32_t)(uintptr_t)parent;
    while(x!=get(tree,0u) && black_or_color(x)==1u) {
        if(p==0u) break;
        uint8_t *pa=(uint8_t *)(uintptr_t)p;
        if(x==get(pa,4u)) {
            uint32_t sibling=get(pa,8u);
            if(color((void *)(uintptr_t)sibling)==0u) {
                blacken(sibling);
                set_color(pa,0u);
                rotate_left(tree,pa);
                sibling=get(pa,8u);
            }
            uint32_t left=get((void *)(uintptr_t)sibling,4u);
            uint32_t right=get((void *)(uintptr_t)sibling,8u);
            if(black_or_color(left)==1u && black_or_color(right)==1u) {
                set_color((void *)(uintptr_t)sibling,0u);
                x=p;p=get(pa,0u);
            } else {
                if(black_or_color(right)==1u) {
                    blacken(left);
                    set_color((void *)(uintptr_t)sibling,0u);
                    rotate_right(tree,(void *)(uintptr_t)sibling);
                    sibling=get(pa,8u);
                    right=get((void *)(uintptr_t)sibling,8u);
                }
                set_color((void *)(uintptr_t)sibling,color(pa));
                set_color(pa,1u);
                blacken(right);
                rotate_left(tree,pa);
                x=get(tree,0u);
            }
        } else {
            uint32_t sibling=get(pa,4u);
            if(color((void *)(uintptr_t)sibling)==0u) {
                blacken(sibling);
                set_color(pa,0u);
                rotate_right(tree,pa);
                sibling=get(pa,4u);
            }
            uint32_t left=get((void *)(uintptr_t)sibling,4u);
            uint32_t right=get((void *)(uintptr_t)sibling,8u);
            if(black_or_color(left)==1u && black_or_color(right)==1u) {
                set_color((void *)(uintptr_t)sibling,0u);
                x=p;p=get(pa,0u);
            } else {
                if(black_or_color(left)==1u) {
                    blacken(right);
                    set_color((void *)(uintptr_t)sibling,0u);
                    rotate_left(tree,(void *)(uintptr_t)sibling);
                    sibling=get(pa,4u);
                    left=get((void *)(uintptr_t)sibling,4u);
                }
                set_color((void *)(uintptr_t)sibling,color(pa));
                set_color(pa,1u);
                blacken(left);
                rotate_right(tree,pa);
                x=get(tree,0u);
            }
        }
    }
    blacken(x);
}
