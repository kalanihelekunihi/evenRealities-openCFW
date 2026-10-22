/* Apollo display case-3 frame prelude 0x46ca14..0x46ca6d. Candidate. */
#include <stdint.h>

extern uint32_t audio_settings_display_profile_cell; /* selected 0x20000648 */
extern uint32_t audio_settings_display_brightness_cell; /* selected 0x2000064c */
uint32_t display_driver_horizontal_offset_cell = 0x18u; /* decoded 0x20000650 */
uint32_t display_driver_vertical_offset_cell; /* BSS 0x200744c8 */
extern void *display_driver_uled_context; /* decoded 0x200007b8 */
extern void display_driver_frame_prepare_46c73c(void *,void *,uint32_t,uint32_t,
                                                 uint32_t,uint32_t,uint32_t,uint32_t);

/* Stock 0x46CA14 (uled framebuffer sync prelude) */
uint32_t display_driver_case3_prelude(void) {
    uint32_t x=audio_settings_display_profile_cell+display_driver_horizontal_offset_cell;
    uint32_t y=audio_settings_display_brightness_cell+display_driver_vertical_offset_cell;
    if(x>=0x41u) x=0x40u;
    x &= ~1u;
    if(y>=0xc1u) y=0xc0u;
    y &= ~1u;
    display_driver_frame_prepare_46c73c(display_driver_uled_context,
        (void *)(uintptr_t)0x20080000u,0x280u,0x1e0u,0x240u,0x120u,x,y);
    return 0u;
}
