/* Apollo LVGL event callback add and first-use pointer-array setup. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, ...);
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lv_obj_setup_layer_43e1fa(void *);
extern uint32_t audio_uart_lv_event_count_450388(void *);
extern uint32_t audio_uart_lv_array_push_488506(void *, const void *);

static const char obj_path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_event.c";
static const char event_path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_event.c";
static const char array_path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_array.c";
static const char asserted[] = "Asserted at expression: %s (%s)";
static const char null_pointer[] = "NULL pointer";



struct audio_lv_event_descriptor {
    void (*callback)(void);
    void *user_data;
    uint32_t filter;
};
_Static_assert(sizeof(struct audio_lv_event_descriptor) == 12u,
               "LV event descriptor ABI");


