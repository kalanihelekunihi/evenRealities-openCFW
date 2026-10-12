/* Native LVGL intrusive linked-list accessors 0x482ce4/0x482cfa and
 * removal 0x482c0e. List base plus node offset is the authenticated ABI. */
#include <stdint.h>
static uint32_t read32(const void *p){uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
static void write32(void *p,uint32_t v){__builtin_memcpy(p,&v,4u);}
void *audio_uart_lv_list_first_482ce4(void *list) {
    return list==0 ? 0 : (void *)(uintptr_t)read32((uint8_t *)list+8u);
}
void *audio_uart_lv_list_next_482cfa(void *list,void *node) {
    uint32_t base=read32(list);
    return (void *)(uintptr_t)read32((void *)(uintptr_t)(base+(uint32_t)(uintptr_t)node));
}
void audio_uart_lv_list_remove_482c0e(void *list,void *node) {
    if(list==0)return;
    uint8_t *l=(uint8_t *)list;
    uint32_t n=(uint32_t)(uintptr_t)node;
    uint32_t base=read32(l);
    uint32_t head=read32(l+4u);
    uint32_t tail=read32(l+8u);
    if(head==n) {
        uint32_t next=read32((void *)(uintptr_t)(base+n+4u));
        write32(l+4u,next);
        if(next==0u)write32(l+8u,0u);
        else write32((void *)(uintptr_t)(base+next),0u);
    }
    else if(tail==n) {
        uint32_t prev=read32((void *)(uintptr_t)(base+n));
        write32(l+8u,prev);
        if(prev==0u)write32(l+4u,0u);
        else write32((void *)(uintptr_t)(base+prev+4u),0u);
    }
    else {
        uint32_t prev=read32((void *)(uintptr_t)(base+n));
        uint32_t next=read32((void *)(uintptr_t)(base+n+4u));
        if(prev!=0u)write32((void *)(uintptr_t)(base+prev+4u),next);
        if(next!=0u)write32((void *)(uintptr_t)(base+next),prev);
    }
}
