/* Native page_manager_init 0x45f15a, complete allocation, LV object
 * construction, callback setup and fatal allocation branch. Product RAM and
 * page style data remain typed contracts. */
#include <stdint.h>
extern void *file_heap_allocate(uint32_t); /* selected allocator contract */
uint8_t *audio_uart_display_page_manager; /* BSS slot 0x20074858, assigned below */
extern void (*audio_uart_display_fatal_handler)(const char *,const char *,uint32_t); /* RAM 0x2007456c */
extern const uint8_t audio_uart_display_page_style[]; /* ROM 0x755610 */
extern uint32_t audio_uart_display_page_size_cell; /* RAM 0x20000064, address passed */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void audio_ble_radio_ready_44b0ae(void); /* selected native reset wrapper */
extern void *audio_uart_display_default_get(void); /* selected 0x44fa1a */
extern void *audio_uart_page_488290(uint32_t);
extern void *audio_uart_page_487022(void *,void *,void *,uint32_t,const void *);
extern void audio_uart_page_44fe0e(void *,void *);
extern void *audio_uart_page_43de82(void *);
extern void audio_uart_page_43f4c0(void *,uint32_t,uint32_t);
extern void audio_uart_page_45ec7c(void *,uint32_t,uint32_t);
extern void audio_uart_page_44131c(void *,uint32_t,uint32_t);
extern void audio_uart_page_44129e(void *,uint32_t,uint32_t);
extern void audio_uart_page_43dfa4(void *,uint32_t);
extern void *audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44127e(void *,void *,uint32_t);
extern void audio_uart_page_44146a(void *,uint32_t,uint32_t);
extern void audio_uart_page_44133a(void *,uint32_t,uint32_t);
extern void audio_uart_page_441378(void *,uint32_t,uint32_t);
extern void audio_uart_page_441386(void *,uint32_t,uint32_t);
extern void audio_uart_page_4413b0(void *,uint32_t,uint32_t);
extern void audio_uart_page_441394(void *,uint32_t,uint32_t);
extern void audio_uart_page_4413a2(void *,uint32_t,uint32_t);
extern void audio_uart_page_45fba2(void *);
extern void audio_uart_page_451740(void *,void (*)(void),uint32_t,void *);
extern void audio_uart_page_event_45f914(void); /* native callback Thumb 0x45f915 */

static const char module[]="page.mgr";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\page_manager\\page_manager.c";
static const char name[]="page_manager_init";
static const char failure[]="page manager init failed, malloc failed";
static const char compact[]="[page.mgr]page manager init failed, malloc failed";
static const char assert_module[]="elog";
static const char assert_format[]="(%s) has assert failed at %s:%ld.";
static const char assert_condition[]="0"; /* authenticated 0x45f3c4 */

uint32_t audio_uart_display_audio_new(void *active_screen) {
    uint8_t *page=(uint8_t *)file_heap_allocate(0xecu);
    audio_uart_display_page_manager=page;
    if(!page) {
        if(audio_log_flags()&2u)
            audio_log_extended(1u,module,source,name,0x197u,failure);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x04000000u,compact,compact);
        if(!audio_uart_display_fatal_handler) {
            audio_log_extended(0u,assert_module,source,name,0x198u,
                               assert_format,assert_condition,name,0x198u);
            for(;;)audio_ble_radio_ready_44b0ae();
        }
        audio_uart_display_fatal_handler(assert_condition,name,0x198u);
        return 0u;
    }
    void *display=audio_uart_display_default_get();
    void *part_a=audio_uart_page_488290(0u);
    void *part_b=audio_uart_page_488290(0u);
    void *instance=audio_uart_page_487022(display,part_b,part_a,0u,
                                             audio_uart_display_page_style);
    audio_uart_page_44fe0e(display,instance);
    void *root=audio_uart_page_43de82(active_screen);
    __builtin_memcpy(page+0x18u,&root,4u);
    audio_uart_page_43f4c0(root,0x240u,0x120u);
    audio_uart_page_45ec7c(root,0u,0u);
    audio_uart_page_44131c(root,0u,0u);
    audio_uart_page_44129e(root,0u,0u);
    audio_uart_page_43dfa4(root,0x10u);
    void *middle=audio_uart_page_43de82(root);
    __builtin_memcpy(page+0x1cu,&middle,4u);
    uint32_t dimension=(uint32_t)(uintptr_t)&audio_uart_display_page_size_cell;
    audio_uart_page_43f4c0(middle,dimension,dimension);
    audio_uart_page_45ec7c(middle,0u,0u);
    audio_uart_page_44131c(middle,0u,0u);
    void *align=audio_uart_page_44104c(0u);
    audio_uart_page_44127e(middle,align,0u);
    audio_uart_page_44129e(middle,0xffu,0u);
    audio_uart_page_44146a(middle,0u,0u);
    audio_uart_page_44133a(middle,0u,0u);
    audio_uart_page_441378(middle,0u,0u);
    audio_uart_page_441386(middle,0u,0u);
    audio_uart_page_4413b0(middle,0u,0u);
    audio_uart_page_441394(middle,0u,0u);
    audio_uart_page_4413a2(middle,0u,0u);
    audio_uart_page_43dfa4(middle,0x10u);
    void *last=audio_uart_page_43de82(root);
    __builtin_memcpy(page+0x20u,&last,4u);
    audio_uart_page_43f4c0(last,dimension,dimension);
    audio_uart_page_45ec7c(last,0u,0u);
    audio_uart_page_44131c(last,0u,0u);
    audio_uart_page_44129e(last,0u,0u);
    audio_uart_page_43dfa4(last,0x10u);
    for(uint32_t offset=0u;offset<=0x10u;offset+=4u)
        *(uint32_t *)(void *)(page+offset)=0u;
    page[0x14u]=0u;page[0xe8u]=0u;
    audio_uart_page_45fba2(page+0x24u);
    __builtin_memcpy((uint8_t *)root+0x10u,&page,4u);
    audio_uart_page_451740(root,audio_uart_page_event_45f914,0u,page);
    return (uint32_t)(uintptr_t)page;
}
