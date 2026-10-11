/* Native pathname compare/duplicate and LVGL list append children. */
#include <stdint.h>
extern uint32_t g2_log_module_length(const char *); /* selected 0x44a43c */
extern void *audio_uart_lv_malloc(uint32_t); /* 0x44f718 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */
int32_t audio_uart_font_path_compare(const char *left,const char *right) {
    for(;;) {
        uint32_t a=(uint8_t)*left;
        uint32_t b=(uint8_t)*right;
        if(a==0u||a!=b) return (int32_t)(a-b);
        ++left;++right;
    }
}
char *audio_uart_font_path_duplicate(const char *source) {
    uint32_t length=g2_log_module_length(source);
    char *result=(char *)audio_uart_lv_malloc(length+1u);
    if(result!=0) (void)audio_queue_copy_bytes(result,source,length+1u);
    return result;
}
void *audio_uart_font_path_node_append(void *list) {
    uint32_t *l=(uint32_t *)list;
    uint8_t *node=(uint8_t *)audio_uart_lv_malloc(l[0]+8u);
    if(node==0) return 0;
    *(uint32_t *)(void *)(node+l[0]+4u)=0u; /* next */
    *(uint32_t *)(void *)(node+l[0])=l[2]; /* previous tail */
    if(l[2]!=0u)
        *(uint32_t *)(void *)(uintptr_t)(l[2]+l[0]+4u)=(uint32_t)(uintptr_t)node;
    l[2]=(uint32_t)(uintptr_t)node;
    if(l[1]==0u) l[1]=(uint32_t)(uintptr_t)node;
    return node;
}
