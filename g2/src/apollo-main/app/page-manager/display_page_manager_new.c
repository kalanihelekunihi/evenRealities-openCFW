/* Native page_manager_init 0x45f15a, complete allocation, LV object
 * construction, callback setup and fatal allocation branch. Product RAM and
 * page style data remain typed contracts. */
#include <stdint.h>
extern void *file_heap_allocate(uint32_t); /* selected allocator contract */
uint8_t *audio_uart_display_page_manager; /* BSS slot 0x20074858, assigned below */
extern void (*audio_uart_display_fatal_handler)(const char *,const char *,uint32_t); /* RAM 0x2007456c */
extern const uint8_t audio_uart_display_page_style[]; /* ROM 0x755610 */
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
extern void lv_obj_set_style_border_width(void *,uint32_t,uint32_t);
extern void audio_uart_page_44129e(void *,uint32_t,uint32_t);
extern void audio_uart_page_43dfa4(void *,uint32_t);
extern void *audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44127e(void *,void *,uint32_t);
extern void lv_obj_set_style_radius(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_outline_width(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_outline_pad(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_shadow_width(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_shadow_spread(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_shadow_offset_x(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_shadow_offset_y(void *,uint32_t,uint32_t);
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

/* Stock 0x0045F15A (page_manager_init) */
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
    lv_obj_set_style_border_width(root,0u,0u);
    audio_uart_page_44129e(root,0u,0u);
    audio_uart_page_43dfa4(root,0x10u);
    void *middle=audio_uart_page_43de82(root);
    __builtin_memcpy(page+0x1cu,&middle,4u);
    /* Evidence: stock 0x45f284 loads literal 0x45fa98 = 0x20000064 into r5
     * and passes it as both w and h to lv_obj_set_size (0x43f4c0). That is
     * the LVGL 9 coordinate LV_PCT(100) = LV_COORD_TYPE_SPEC(1<<29)|100, not
     * a RAM address; it only coincides with stock RAM 0x20000064. */
    uint32_t dimension=0x20000064u; /* LV_PCT(100) */
    audio_uart_page_43f4c0(middle,dimension,dimension);
    audio_uart_page_45ec7c(middle,0u,0u);
    lv_obj_set_style_border_width(middle,0u,0u);
    void *align=audio_uart_page_44104c(0u);
    audio_uart_page_44127e(middle,align,0u);
    audio_uart_page_44129e(middle,0xffu,0u);
    lv_obj_set_style_radius(middle,0u,0u);
    lv_obj_set_style_outline_width(middle,0u,0u);
    lv_obj_set_style_outline_pad(middle,0u,0u);
    lv_obj_set_style_shadow_width(middle,0u,0u);
    lv_obj_set_style_shadow_spread(middle,0u,0u);
    lv_obj_set_style_shadow_offset_x(middle,0u,0u);
    lv_obj_set_style_shadow_offset_y(middle,0u,0u);
    audio_uart_page_43dfa4(middle,0x10u);
    void *last=audio_uart_page_43de82(root);
    __builtin_memcpy(page+0x20u,&last,4u);
    audio_uart_page_43f4c0(last,dimension,dimension);
    audio_uart_page_45ec7c(last,0u,0u);
    lv_obj_set_style_border_width(last,0u,0u);
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
