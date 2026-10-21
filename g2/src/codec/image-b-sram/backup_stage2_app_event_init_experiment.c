/* Native image-B LvpInitializeAppEvent 0x1000bdfc..0x1000be3d and its
 * suspend/resume callbacks 0x1000bdb0/0x1000bdcc. Pinned NationalChip
 * lvp/app_core/lvp_app_core.c establishes the queue and callback record
 * semantics; native strings and SRAM addresses are exact product evidence.
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

typedef struct {
    int (*callback)(void *);
    const char *name;
} image_b_callback_record;
_Static_assert(sizeof(image_b_callback_record) == 8, "native callback record");

extern image_b_lvp_app *gx8002_image_b_sample_app_selected_20016f74;
extern void gx8002_image_b_audio_frame_set_10009fa8(
    uint32_t *, uint32_t, int32_t, int32_t);
extern uint32_t gx8002_image_b_audio_record_one_1000a784(const uint32_t *);
extern uint32_t gx8002_image_b_audio_record_two_1000a7f0(const uint32_t *);

int32_t gx8002_image_b_app_suspend_1000bdb0(void *unused)
{
    (void)unused;
    image_b_lvp_app *app = gx8002_image_b_sample_app_selected_20016f74;
    if (app != 0 && app->suspend != 0)
        (void)app->suspend(app->suspend_priv);
    return 0;
}

int32_t gx8002_image_b_app_resume_1000bdcc(void *unused)
{
    (void)unused;
    image_b_lvp_app *app = gx8002_image_b_sample_app_selected_20016f74;
    if (app != 0 && app->resume != 0)
        (void)app->resume(app->resume_priv);
    return 0;
}

int32_t gx8002_image_b_main_services_1000bdfc(void)
{
    gx8002_image_b_audio_frame_set_10009fa8(
        (uint32_t *)(uintptr_t)UINT32_C(0x2002d784),
        UINT32_C(0x2002d31c), 64, 8);
    image_b_lvp_app *app = gx8002_image_b_sample_app_selected_20016f74;
    if (app != 0 && app->app_init != 0)
        (void)app->app_init();
    static const char suspend_name[] = "_LvpAppSuspend";
    static const char resume_name[] = "_LvpAppResume";
    const image_b_callback_record suspend_record = {
        gx8002_image_b_app_suspend_1000bdb0, suspend_name};
    const image_b_callback_record resume_record = {
        gx8002_image_b_app_resume_1000bdcc, resume_name};
    (void)gx8002_image_b_audio_record_one_1000a784(
        (const uint32_t *)(const void *)&suspend_record);
    (void)gx8002_image_b_audio_record_two_1000a7f0(
        (const uint32_t *)(const void *)&resume_record);
    return 0;
}
