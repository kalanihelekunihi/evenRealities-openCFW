/* Apollo 0x46c984, 0x46c9aa and 0x46c9dc display setter entry points. */
#include <stdint.h>
extern uint32_t audio_settings_display_profile_cell; /* selected 0x20000648 */
extern uint32_t audio_settings_display_brightness_cell; /* selected 0x2000064c */
extern uint32_t display_driver_horizontal_offset_cell; /* 0x20000650 */
extern uint32_t display_driver_vertical_offset_cell; /* 0x200744c8 */
extern void display_driver_prepare_update_47381e(void);
extern void display_driver_submit_window_474066(uint32_t,uint32_t,uint32_t,
                                                uint32_t,uint32_t,uint32_t);

static uint32_t submit_full_window(void) {
    display_driver_prepare_update_47381e();
    display_driver_submit_window_474066(0u,0u,0u,0u,0x240u,0x120u);
    return 0u;
}
uint32_t display_driver_set_brightness_46c984(uint32_t value) {
    audio_settings_display_brightness_cell=value;
    return submit_full_window();
}
uint32_t display_driver_set_profile_46c9aa(uint32_t value) {
    audio_settings_display_profile_cell=value;
    return submit_full_window();
}
uint32_t display_driver_set_offsets_46c9dc(uint32_t horizontal,uint32_t vertical) {
    if(horizontal>=0x31u || vertical>=0x41u) return UINT32_MAX;
    display_driver_horizontal_offset_cell=horizontal;
    display_driver_vertical_offset_cell=vertical;
    return submit_full_window();
}
