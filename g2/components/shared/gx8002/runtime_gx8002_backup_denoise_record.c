/* SPDX-License-Identifier: MIT */
/* Recovered backup mode dispatch record and its complete entry wrappers. */
#include "lvp_mode.h"
extern int printf(const char *, ...);
extern int open_cfw_gx8002_backup_context_initialize(void);
extern int open_cfw_gx8002_backup_denoise_init(LVP_MODE_TYPE);
extern void open_cfw_gx8002_backup_denoise_tick(void);
static const char exit_message[] __attribute__((section(".denoise_message"))) =
    "[LVP_MODE_DENOISE]Exit denoise mode\n";
static void denoise_done(LVP_MODE_TYPE next_mode)
{
    (void)next_mode;
    printf(exit_message);
}
static int denoise_buffer_init(void)
{
    return open_cfw_gx8002_backup_context_initialize();
}
const LVP_MODE_INFO lvp_denoise_mode_info = {
    .type = LVP_MODE_DENOISE,
    .init = open_cfw_gx8002_backup_denoise_init,
    .done = denoise_done,
    .tick = open_cfw_gx8002_backup_denoise_tick,
    .buffer_init = denoise_buffer_init,
};
