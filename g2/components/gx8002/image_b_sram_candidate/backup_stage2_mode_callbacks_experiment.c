/* Native image-B IDLE/denoise mode leaves around 0x1000b7c0..0x1000b7ff.
 * Typed strings are the authenticated NUL-terminated SDK mode labels.
 * The denoise buffer callback keeps R0 from selected runtime init 0x9d7c.
 */
#include <stdint.h>

extern int gx8002_image_b_heap_log_10009934(const char *, ...);
extern void gx8002_image_b_runtime_state_init_10009d7c(void);

void gx8002_image_b_idle_tick_1000b7c0(void)
{
}

int32_t gx8002_image_b_idle_buffer_1000b7c4(void)
{
    return 0;
}

void gx8002_image_b_idle_done_1000b7c8(uint32_t next_mode)
{
    (void)next_mode;
    (void)gx8002_image_b_heap_log_10009934("[IDLE]Exit IDLE mode\n");
}

int32_t gx8002_image_b_idle_init_1000b7d8(uint32_t previous_mode)
{
    (void)previous_mode;
    (void)gx8002_image_b_heap_log_10009934("[IDLE]Init IDLE mode\n");
    return 0;
}

void gx8002_image_b_mode5_done_1000b7e8(uint32_t next_mode)
{
    (void)next_mode;
    (void)gx8002_image_b_heap_log_10009934(
        "[LVP_MODE_DENOISE]Exit denoise mode\n");
}

__attribute__((naked))
int32_t gx8002_image_b_mode5_buffer_1000b7f8(void)
{
    __asm__ volatile (
        "push r15\n\t"
        "bsr gx8002_image_b_runtime_state_init_10009d7c\n\t"
        "pop r15");
}
