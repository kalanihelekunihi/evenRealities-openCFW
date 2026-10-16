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

static void fatal_assert(const char *path, uint32_t line, const char *function,
                         const char *expression, const char *reason) {
    audio_uart_lvgl_log(3u, path, line, function, asserted, expression, reason);
    for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
}

void audio_uart_lv_array_init_4883fc(void *array, uint32_t capacity,
                                     uint32_t stride) {
    uint8_t *bytes = (uint8_t *)array;
    *(uint32_t *)(void *)(bytes + 4u) = 0u;
    *(uint32_t *)(void *)(bytes + 8u) = capacity;
    *(uint32_t *)(void *)(bytes + 12u) = stride;
    void *data = audio_uart_lv_malloc(capacity * stride);
    *(void **)(void *)bytes = data;
    bytes[16] = 1u;
    if (data == 0)
        fatal_assert(array_path, 0x2eu, "lv_array_init",
                     "array->data != NULL", "Out of memory");
}

struct audio_lv_event_descriptor {
    void (*callback)(void);
    void *user_data;
    uint32_t filter;
};
_Static_assert(sizeof(struct audio_lv_event_descriptor) == 12u,
               "LV event descriptor ABI");

void *audio_uart_lv_event_add_4500e4(void *list, void (*callback)(void),
                                      uint32_t filter, void *user_data) {
    struct audio_lv_event_descriptor *descriptor = audio_uart_lv_malloc(12u);
    if (descriptor == 0)
        fatal_assert(event_path, 0x7cu, "lv_event_add",
                     "dsc != NULL", null_pointer);
    descriptor->callback = callback;
    descriptor->filter = filter;
    descriptor->user_data = user_data;
    if (audio_uart_lv_event_count_450388(list) == 0u)
        audio_uart_lv_array_init_4883fc(list, 1u, 4u);
    (void)audio_uart_lv_array_push_488506(list, &descriptor);
    return descriptor;
}

void *audio_uart_page_451740(void *object, void (*callback)(void),
                             uint32_t filter, void *user_data) {
    if (object == 0)
        fatal_assert(obj_path, 0x66u, "lv_obj_add_event_cb",
                     "obj != NULL", null_pointer);
    audio_uart_lv_obj_setup_layer_43e1fa(object);
    uint8_t *spec = *(uint8_t **)(void *)((uint8_t *)object + 8u);
    return audio_uart_lv_event_add_4500e4(spec + 8u, callback, filter, user_data);
}
