/* Native LVGL font-chain constructor 0x46cae0 and its list helpers. */
#include <stdint.h>
extern void *file_heap_allocate(uint32_t);
extern void file_heap_free(void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void *audio_uart_font_create(const char *,uint8_t,uint32_t,uint8_t); /* 0x4b1c9c */
extern void audio_uart_font_delete(void *); /* 0x4b1ef6 */
static const char audio_uart_ring_module[]="font_manager"; /* ROM0x00787a50 */
static const char audio_uart_ring_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\common\\lvgl_font_manager.c"; /* ROM0x006fb45c */
static const char audio_uart_ring_ctor_fn[]="font_manager_create_chain"; /* ROM0x0076df8c */
static const char audio_uart_ring_element_fn[]="create_single_font"; /* ROM0x007811c4 */
static const char audio_uart_ring_add_fn[]="add_font_to_manager"; /* ROM0x007811ec, DAT_0046d5f8 */
static const char audio_uart_ring_free_fn[]="cleanup_single_font"; /* ROM0x00781200 */
static const char audio_uart_ring_text_0046d450[]="configs is NULL"; /* ROM0x00787a60 */
static const char audio_uart_ring_text_0046d458[]="count is 0"; /* ROM0x0078b570 */
static const char audio_uart_ring_text_0046d460[]="count too large"; /* ROM0x00787a70 */
static const char audio_uart_ring_text_0046d58c[]="Failed to allocate font chain manager"; /* ROM0x0074b11c */
static const char audio_uart_ring_text_0046d594[]="Failed to allocate fonts array"; /* ROM0x007620d0 */
static const char audio_uart_ring_text_0046d454[]="[font_manager]configs is NULL"; /* ROM0x00762090 */
static const char audio_uart_ring_text_0046d45c[]="[font_manager]count is 0"; /* ROM0x0076dfa8 */
static const char audio_uart_ring_text_0046d588[]="[font_manager]count too large"; /* ROM0x007620b0 */
static const char audio_uart_ring_text_0046d590[]="[font_manager]Failed to allocate font chain manager"; /* ROM0x0072aa10 */
static const char audio_uart_ring_text_0046d598[]="[font_manager]Failed to allocate fonts array"; /* ROM0x007354d4 */
static const char audio_uart_ring_text_0046d5c8[]="Native font is NULL"; /* ROM0x007811d8 */
static const char audio_uart_ring_text_0046d5dc[]="FreeType font name is NULL"; /* ROM0x0076dfc4 */
static const char audio_uart_ring_text_0046d5e4[]="File system not enabled for binary fonts"; /* ROM0x0073fd3c */
static const char audio_uart_ring_text_0046d5ec[]="Unknown font type: %d"; /* ROM0x007795bc */
static const char audio_uart_ring_text_0046d5f4[]="Failed to allocate font node"; /* ROM0x007620f0 */
static const char audio_uart_ring_text_0046d5d0[]="[font_manager]Native font is NULL"; /* ROM0x00756810 */
static const char audio_uart_ring_text_0046d5e0[]="[font_manager]FreeType font name is NULL"; /* ROM0x0073fd10 */
static const char audio_uart_ring_text_0046d5e8[]="[font_manager]File system not enabled for binary fonts"; /* ROM0x00720280 */
static const char audio_uart_ring_text_0046d5f0[]="[font_manager]Unknown font type: %d"; /* ROM0x00756858 */
static const char audio_uart_ring_text_0046d5fc[]="[font_manager]Failed to allocate font node"; /* ROM0x0073fd68 */
static const char audio_uart_ring_text_0046d600[]="Unknown font type %d for cleanup"; /* ROM0x0075687c */
static const char audio_uart_ring_text_0046d608[]="[font_manager]Unknown font type %d for cleanup"; /* ROM0x00735534 */
static const char audio_uart_ring_text_0046d444[]="font_manager_create_chain called";
static const char audio_uart_ring_text_0046d44c[]="[font_manager]font_manager_create_chain called";
static const char audio_uart_ring_text_0046d5d4[]="Failed to create FreeType font: %s";
static const char audio_uart_ring_text_0046d5d8[]="[font_manager]Failed to create FreeType font: %s";
static const char audio_uart_ring_text_0046d59c[]="Font creation failed";
static const char audio_uart_ring_text_0046d5a0[]="[font_manager]Font creation failed";
static const char audio_uart_ring_text_0046d5a4[]="Failed to track font, cleaning up";
static const char audio_uart_ring_text_0046d5a8[]="[font_manager]Failed to track font, cleaning up";
static const char audio_uart_ring_text_0046d5ac[]="No valid fonts created";
static const char audio_uart_ring_text_0046d5b0[]="[font_manager]No valid fonts created";
static const char audio_uart_ring_text_0046d5b4[]="Font chain created";
static const char audio_uart_ring_text_0046d5b8[]="[font_manager]Font chain created";
typedef struct {uint32_t first,head;uint8_t count,pad[3];} ring_list;
typedef struct {uint32_t item;uint8_t type,pad[3];uint32_t next;} ring_node;
static void ring_log(uint32_t severity,uint32_t line,const char *function,
                     const char *long_text,uint32_t compact_flags,const char *short_text) {
    if(audio_log_flags()&2u)
        audio_log_extended((uint8_t)severity,audio_uart_ring_module,
                           audio_uart_ring_source,function,line,long_text);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(compact_flags,short_text,short_text);
}
/* Stock 0x46D158 (add_font_to_manager) */
static void ring_node_add(ring_list *list,void *item,uint8_t type) {
    if(list==0||item==0) return;
    ring_node *node=(ring_node *)file_heap_allocate(12u);
    if(node==0) {
        ring_log(1u,0x156u,audio_uart_ring_add_fn,
                 audio_uart_ring_text_0046d5f4,0x04000000u,
                 audio_uart_ring_text_0046d5fc);
        return;
    }
    node->item=(uint32_t)(uintptr_t)item;
    node->type=type;
    node->next=list->head;
    list->head=(uint32_t)(uintptr_t)node;
    list->count=(uint8_t)(list->count+1u);
}
/* Stock 0x46CFA6 (create_single_font) */
static void *ring_element(const uint8_t *description) {
    if(description==0) return 0;
    uint8_t type=description[0];
    void *source=*(void *const *)(const void *)(description+4u);
    if(type==0u) {
        if(source==0)
            ring_log(1u,0x11eu,audio_uart_ring_element_fn,
                     audio_uart_ring_text_0046d5c8,0x04000000u,
                     audio_uart_ring_text_0046d5d0);
        return source;
    }
    if(type==1u) {
        if(source==0) {
            ring_log(1u,0x132u,audio_uart_ring_element_fn,
                     audio_uart_ring_text_0046d5dc,0x04000000u,
                     audio_uart_ring_text_0046d5e0);
            return 0;
        }
        void *item=audio_uart_font_create((const char *)source,1u,
                    *(const uint16_t *)(const void *)(description+8u),
                    description[10u]);
        if(item==0) {
            if(audio_log_flags()&2u)
                audio_log_extended(1u,audio_uart_ring_module,audio_uart_ring_source,
                     audio_uart_ring_element_fn,0x12eu,audio_uart_ring_text_0046d5d4,source);
            if((audio_log_flags()&1u)||(audio_log_flags()&4u))
                (void)compressed_log_output(0x04400000u,audio_uart_ring_text_0046d5d8,
                                             audio_uart_ring_text_0046d5d8,source);
        }
        return item;
    }
    if(type==2u)
        ring_log(1u,0x147u,audio_uart_ring_element_fn,
                 audio_uart_ring_text_0046d5e4,0x04000000u,
                 audio_uart_ring_text_0046d5e8);
    else {
        if(audio_log_flags()&2u)
            audio_log_extended(1u,audio_uart_ring_module,audio_uart_ring_source,
                   audio_uart_ring_element_fn,0x14cu,audio_uart_ring_text_0046d5ec,type);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x04400000u,audio_uart_ring_text_0046d5f0,
                                         audio_uart_ring_text_0046d5f0,type);
    }
    return 0;
}
/* Stock 0x46D1C6 (cleanup_single_font) */
static void ring_element_release(void *element,uint8_t type) {
    if(element==0||type==0u||type==2u) return;
    if(type==1u) audio_uart_font_delete(element);
    else {
        if(audio_log_flags()&2u)
            audio_log_extended(2u,audio_uart_ring_module,audio_uart_ring_source,
                   audio_uart_ring_free_fn,0x17au,audio_uart_ring_text_0046d600,type);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x08400000u,audio_uart_ring_text_0046d608,
                                         audio_uart_ring_text_0046d608,type);
    }
}
/* Stock 0x46CAE0 (font_manager_create_chain) */
ring_list *audio_uart_display_ring_construct(const uint8_t *descriptions,
                                             uint32_t requested_count) {
    if(audio_log_flags()&2u)
        audio_log_extended(3u,audio_uart_ring_module,audio_uart_ring_source,
             audio_uart_ring_ctor_fn,0x41u,audio_uart_ring_text_0046d444);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x0c000000u,audio_uart_ring_text_0046d44c,
                                    audio_uart_ring_text_0046d44c);
    uint8_t count=(uint8_t)requested_count;
    if(descriptions==0||count==0u||count>=9u) {
        uint32_t index=descriptions==0?0u:(count==0u?1u:2u);
        ring_log(1u,index==0u?0x44u:(index==1u?0x4au:0x4fu),
                 audio_uart_ring_ctor_fn,(index==0u?audio_uart_ring_text_0046d450:(index==1u?audio_uart_ring_text_0046d458:audio_uart_ring_text_0046d460)),
                 0x04000000u,
                 (index==0u?audio_uart_ring_text_0046d454:(index==1u?audio_uart_ring_text_0046d45c:audio_uart_ring_text_0046d588)));
        return 0;
    }
    ring_list *list=(ring_list *)file_heap_allocate(12u);
    if(list==0) {
        ring_log(1u,0x59u,audio_uart_ring_ctor_fn,
                 audio_uart_ring_text_0046d58c,0x04000000u,
                 audio_uart_ring_text_0046d590);
        return 0;
    }
    list->first=0u;list->head=0u;list->count=0u;
    void **items=(void **)file_heap_allocate((uint32_t)count*4u);
    if(items==0) {
        ring_log(1u,0x67u,audio_uart_ring_ctor_fn,
                 audio_uart_ring_text_0046d594,0x04000000u,
                 audio_uart_ring_text_0046d598);
        file_heap_free(list);return 0;
    }
    for(uint8_t i=0;i<count;++i) items[i]=0;
    for(uint8_t i=0;i<count;++i) {
        const uint8_t *d=descriptions+(uint32_t)i*12u;
        void *item=ring_element(d);
        items[i]=item;
        if(item==0) {
            ring_log(2u,0x8bu,audio_uart_ring_ctor_fn,audio_uart_ring_text_0046d59c,
                     0x08000000u,audio_uart_ring_text_0046d5a0);
            continue;
        }
        uint8_t old_count=list->count;
        ring_node_add(list,item,d[0]);
        if(list->count==old_count) {
            ring_log(1u,0x86u,audio_uart_ring_ctor_fn,audio_uart_ring_text_0046d5a4,
                     0x04000000u,audio_uart_ring_text_0046d5a8);
            ring_element_release(item,d[0]);
            items[i]=0;
        }
    }
    if(list->count==0u) {
        ring_log(1u,0x91u,audio_uart_ring_ctor_fn,audio_uart_ring_text_0046d5ac,
                 0x04000000u,audio_uart_ring_text_0046d5b0);
        for(uint8_t i=0;i<count;++i)
            if(items[i]!=0) ring_element_release(items[i],descriptions[(uint32_t)i*12u]);
        file_heap_free(items);file_heap_free(list);return 0;
    }
    uint32_t previous=0u;
    for(uint8_t i=0;i<count;++i) {
        if(items[i]==0) continue;
        if(previous!=0u)
            *(uint32_t *)(uintptr_t)(previous+0x1cu)=(uint32_t)(uintptr_t)items[i];
        previous=(uint32_t)(uintptr_t)items[i];
    }
    if(previous!=0u) *(uint32_t *)(uintptr_t)(previous+0x1cu)=0u;
    for(uint8_t i=0;i<count;++i) {
        if(items[i]==0) continue;
        list->first=(uint32_t)(uintptr_t)items[i];
        file_heap_free(items);
        ring_log(3u,0xb9u,audio_uart_ring_ctor_fn,audio_uart_ring_text_0046d5b4,
                 0x0c000000u,audio_uart_ring_text_0046d5b8);
        return list;
    }
    file_heap_free(items);file_heap_free(list);return 0;
}
