/* Apollo Main scroll dispatch 0x44e884..0x44e9b9 and finish callback 0x44f3f0. */
#include <stdint.h>

extern void *audio_uart_lv_display_for_object(void *);
extern void audio_uart_lv_anim_init_4503d6(void *);
extern int32_t audio_uart_lv_display_width_44fa7e(void *);
extern int32_t audio_uart_lv_display_height_44faa8(void *);
extern int32_t audio_uart_lv_anim_duration_clamp_4505a2(int32_t, int32_t, int32_t);
extern void audio_uart_lv_anim_values_4506ce(void *, int32_t, int32_t);
extern void audio_uart_lv_anim_start_450408(void *);
extern void audio_uart_lv_anim_path_450672(void *);
extern uint32_t audio_uart_lv_obj_event_451670(void *, uint32_t, void *);
extern int32_t audio_uart_lv_obj_x_44e486(void *);
extern int32_t audio_uart_lv_obj_y_44e498(void *);
extern uint32_t audio_uart_lv_style_unlink_450500(void *, void *);
extern uint32_t audio_uart_lv_scroll_by_44ea98(void *, int32_t, int32_t);
extern void audio_uart_lv_scroll_anim_x_44f3b8(void *, int32_t);
extern void audio_uart_lv_scroll_anim_y_44f3d4(void *, int32_t);

typedef struct {
    uint8_t bytes[0x60];
} scroll_anim_descriptor;


void audio_uart_lv_scroll_anim_finish_44f3f0(void *descriptor) {
    const uint8_t *const bytes = (const uint8_t *)descriptor;
    if ((bytes[0x5cu] & 8u) != 0u) {
        void *object = *(void *const *)descriptor;
        (void)audio_uart_lv_obj_event_451670(object, 0x0eu, 0);
    }
}

