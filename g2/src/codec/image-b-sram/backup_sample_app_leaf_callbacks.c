/* Image-B native sample application leaf callbacks. Product logging uses
 * the I2S_OUT_APP prefix in this image, not the generic SDK sample prefix. */
#include <stdint.h>

extern int gx8002_image_b_heap_log_10009934(const char *format, ...);

int gx8002_image_b_sample_app_task_1000bea8(void)
{
    return 0;
}

int gx8002_image_b_sample_app_resume_1000beac(void *priv)
{
    (void)gx8002_image_b_heap_log_10009934(
        "[I2S_OUT_APP] ---- %s ----\n", "SampleAppResume");
    (void)gx8002_image_b_heap_log_10009934("%s\n", priv);
    return 0;
}

int gx8002_image_b_sample_app_suspend_1000bed0(void *priv)
{
    (void)gx8002_image_b_heap_log_10009934(
        "[I2S_OUT_APP] ---- %s ----\n", "SampleAppSuspend");
    (void)gx8002_image_b_heap_log_10009934("%s\n", priv);
    return 0;
}
