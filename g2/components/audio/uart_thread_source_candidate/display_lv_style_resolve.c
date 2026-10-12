/* Native LV style selector 0x44b860, flag test 0x44b844 and subscribed
 * style-node resolver 0x44ca18. List root is lv_root+0x18 at 0x2006f560. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[]; /* live 0x2006f548 */
extern void *audio_uart_lv_list_first_482ce4(void *);
extern void *audio_uart_lv_list_next_482cfa(void *,void *);
extern uint32_t audio_uart_lv_style_notify_4827b0(void *,uint32_t);
extern void audio_uart_lv_style_unlink_450500(void *,uint32_t);
extern void audio_uart_lv_list_remove_482c0e(void *,void *);
extern void audio_uart_lv_heap_free(void *); /* selected 0x44f758 */
extern uint32_t audio_uart_lv_property_flags_482a6a(uint8_t);

uint32_t audio_uart_page_style_selector_44b860(uint32_t selector) {
    return selector&0xff0000u;
}
uint32_t audio_uart_page_style_needs_invalidate_44b844(uint32_t property,uint32_t mask) {
    return (audio_uart_lv_property_flags_482a6a((uint8_t)property)&mask)!=0u;
}
uint32_t audio_uart_page_style_resolve_44ca18(void *object,uint32_t group,
                                               uint8_t property,void *stop) {
    void *root=audio_uart_display_lv_root+0x18u;
    uint8_t removed=0u;
    for(uint32_t *node=(uint32_t *)audio_uart_lv_list_first_482ce4(root);
        node!=0 && node!=(uint32_t *)stop;) {
        uint32_t *next=(uint32_t *)audio_uart_lv_list_next_482cfa(root,node);
        if((void *)(uintptr_t)node[0]==object &&
           (group==node[2] || group==0xf0000u) &&
           ((int8_t)property==(int8_t)node[1] || (int8_t)property==-1)) {
            uint8_t *obj=(uint8_t *)object;
            uint16_t count;
            __builtin_memcpy(&count,obj+0x2au,2u);
            uint32_t *entries;
            __builtin_memcpy(&entries,obj+0x0cu,4u);
            for(uint32_t i=0u;i<((count&0x3ffu)>>4u);i++) {
                uint32_t bits=entries[2u*i+1u];
                if((bits&0x02000000u)!=0u &&
                   (group==0xf0000u || (bits&0xffffffu)==group))
                    audio_uart_lv_style_notify_4827b0((void *)(uintptr_t)entries[2u*i],
                                                      (int8_t)node[1]);
            }
            audio_uart_lv_style_unlink_450500(node,0u);
            audio_uart_lv_list_remove_482c0e(root,node);
            audio_uart_lv_heap_free(node);
            removed=1u;
        }
        node=next;
    }
    return removed;
}
