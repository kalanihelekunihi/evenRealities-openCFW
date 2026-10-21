/* Native image-B LvpAppEventTick 0x1000be5c..0x1000be9f.
 * Pinned NationalChip lvp/app_core/lvp_app_core.c provides the same ring,
 * event_response, task_loop and registration-dispatch callback sequence.
 */
#include <stdint.h>

typedef struct {
    const char *app_name;
    int (*app_init)(void);
    int (*event_response)(void *);
    int (*task_loop)(void);
    int (*suspend)(void *);
    void *suspend_priv;
    int (*resume)(void *);
    void *resume_priv;
} image_b_lvp_app;
_Static_assert(sizeof(image_b_lvp_app) == 32, "native app record width");

extern image_b_lvp_app *gx8002_image_b_sample_app_selected_20016f74;
extern uint32_t gx8002_image_b_audio_ring_read_10009fbc(
    volatile int32_t *, uint8_t *);
extern int32_t gx8002_image_b_audio_registration_dispatch_1000b4c8(void);

int32_t gx8002_image_b_main_continue_1000be5c(void)
{
    uint32_t event[2] = {0u, 0u};
    if (gx8002_image_b_audio_ring_read_10009fbc(
            (volatile int32_t *)(uintptr_t)UINT32_C(0x2002d784),
            (uint8_t *)(void *)event) != 0u) {
        image_b_lvp_app *app = gx8002_image_b_sample_app_selected_20016f74;
        if (app != 0 && app->event_response != 0)
            (void)app->event_response(event);
    }
    image_b_lvp_app *app = gx8002_image_b_sample_app_selected_20016f74;
    if (app != 0 && app->task_loop != 0)
        (void)app->task_loop();
    (void)gx8002_image_b_audio_registration_dispatch_1000b4c8();
    return 0;
}
