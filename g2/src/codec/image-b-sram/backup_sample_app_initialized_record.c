/* Native normal-copy region 0x10016f74..0x10016f97 / runtime
 * 0x20016f74..0x20016f97, matching pinned NationalChip LVP_APP layout.
 * The callback addresses were authenticated from the eight native words;
 * this record is not selected until all callbacks have source bodies. */
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

_Static_assert(sizeof(void *) == 4, "native C-SKY pointer ABI");
_Static_assert(sizeof(image_b_lvp_app) == 32, "pinned LVP_APP record");

extern int gx8002_image_b_sample_app_init_1000c0bc(void);
extern int gx8002_image_b_sample_app_event_1000c1c8(void *);
extern int gx8002_image_b_sample_app_task_1000bea8(void);
extern int gx8002_image_b_sample_app_suspend_1000bed0(void *);
extern int gx8002_image_b_sample_app_resume_1000beac(void *);

static const char sample_name[] = "sample app";
static const char suspend_name[] = "SampleAppSuspend";
static const char resume_name[] = "SampleAppResume";

image_b_lvp_app gx8002_image_b_sample_app_record_20016f78
    __attribute__((section(".data.image_b.sample_app"), used)) = {
        .app_name = sample_name,
        .app_init = gx8002_image_b_sample_app_init_1000c0bc,
        .event_response = gx8002_image_b_sample_app_event_1000c1c8,
        .task_loop = gx8002_image_b_sample_app_task_1000bea8,
        .suspend = gx8002_image_b_sample_app_suspend_1000bed0,
        .suspend_priv = (void *)suspend_name,
        .resume = gx8002_image_b_sample_app_resume_1000beac,
        .resume_priv = (void *)resume_name,
};

image_b_lvp_app *gx8002_image_b_sample_app_selected_20016f74
    __attribute__((section(".data.image_b.sample_app_pointer"), used)) =
    &gx8002_image_b_sample_app_record_20016f78;
