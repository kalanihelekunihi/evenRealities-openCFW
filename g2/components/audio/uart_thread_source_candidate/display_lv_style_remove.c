/* Native 0x44ba9a lv_obj_remove_style, including local/transition ownership,
 * transition removal, compacted style records, and refresh after mutation. */
#include <stdint.h>
extern uint32_t audio_uart_page_style_selector_44b860(uint32_t);
extern uint32_t audio_uart_page_style_resolve_44ca18(void *,uint32_t,uint8_t,void *);
extern void audio_uart_display_size_changed(void *);
extern uint32_t audio_uart_lv_style_has_flag_44ce2c(void *,uint32_t);
extern void audio_uart_lv_style_reset_482796(void *);
extern void audio_uart_lv_heap_free(void *); /* selected 0x44f758 */
extern void *audio_uart_lv_realloc_44f76a(void *,uint32_t);
extern void audio_uart_lv_style_removed_44ce2a(void *,uint32_t);
extern void audio_uart_page_style_refresh_44bc8c(void *,uint32_t,uint32_t);
static uint16_t read16(const uint8_t *p){uint16_t v;__builtin_memcpy(&v,p,2u);return v;}
static uint32_t read32(const uint8_t *p){uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
static void write16(uint8_t *p,uint16_t v){__builtin_memcpy(p,&v,2u);}
static void write32(uint8_t *p,uint32_t v){__builtin_memcpy(p,&v,4u);}
void audio_uart_lv_style_remove_44ba9a(void *object,void *style,uint32_t selector) {
    uint8_t *obj=(uint8_t *)object;
    int16_t state=(int16_t)selector;
    uint32_t part=audio_uart_page_style_selector_44b860(selector);
    int8_t refresh_property=-1;
    if(style!=0 && ((uint8_t *)style)[8u]==0u)refresh_property=0;
    if(style!=0 && part==0u && audio_uart_lv_style_has_flag_44ce2c(style,0x20u)!=0u)
        audio_uart_display_size_changed(object);
    uint32_t i=0u;
    uint8_t removed=0u;
    for(;;) {
        uint16_t packed=read16(obj+0x2au);
        uint32_t count=(packed&0x3ffu)>>4u;
        if(i>=count)break;
        uint8_t *entries=(uint8_t *)(uintptr_t)read32(obj+0x0cu);
        uint8_t *entry=entries+i*8u;
        uint32_t bits=read32(entry+4u);
        uint32_t entry_selector=bits&0x00ffffffu;
        if(!((state==-1 || (int16_t)entry_selector==state) &&
             (part==0xf0000u || audio_uart_page_style_selector_44b860(entry_selector)==part) &&
             (style==0 || (void *)(uintptr_t)read32(entry)==style))) {
            i++;
            continue;
        }
        if((bits&0x02000000u)!=0u)
            (void)audio_uart_page_style_resolve_44ca18(object,part,0xffu,0);
        if((bits&0x03000000u)!=0u) {
            void *owned=(void *)(uintptr_t)read32(entry);
            if(owned!=0)audio_uart_lv_style_reset_482796(owned);
            audio_uart_lv_heap_free(owned);
            write32(entry,0u);
        }
        for(uint32_t j=i;j+1u<count;j++)
            __builtin_memcpy(entries+j*8u,entries+(j+1u)*8u,8u);
        packed=(uint16_t)((packed&0xfc0fu)|(((count-1u)&0x3fu)<<4u));
        write16(obj+0x2au,packed);
        void *smaller=audio_uart_lv_realloc_44f76a(entries,(count-1u)*8u);
        write32(obj+0x0cu,(uint32_t)(uintptr_t)smaller);
        removed=1u;
    }
    if(removed!=0u && refresh_property!=0) {
        audio_uart_lv_style_removed_44ce2a(object,part);
        audio_uart_page_style_refresh_44bc8c(object,part,(uint8_t)refresh_property);
    }
}
