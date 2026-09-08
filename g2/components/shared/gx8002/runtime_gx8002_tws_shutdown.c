/* SPDX-License-Identifier: MIT */
/* Adapted from NationalChip lvp/lvp_mode_tws.c at
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
 * See NATIONALCHIP-TWS-NOTICE.txt for original attribution. */
#include <stddef.h>
#include <lvp_mode.h>
#include <common/lvp_queue.h>
#include <tws-shutdown-interfaces.h>
extern void *memset(void *, int, size_t);
extern int printf(const char *, ...);
extern LVP_QUEUE open_cfw_gx8002_tws_queue;
_Static_assert(sizeof(LVP_QUEUE) == 20, "queue clear extent");
const char open_cfw_gx8002_tws_exit[] __attribute__((aligned(1))) = "[LVP_TWS]Exit TWS mode\n";
void open_cfw_gx8002_tws_done(LVP_MODE_TYPE next_mode)
{
    (void)next_mode;
    memset(&open_cfw_gx8002_tws_queue, 0, sizeof(open_cfw_gx8002_tws_queue));
    LvpKwsDone();
    LvpAudioInDone();
    printf(open_cfw_gx8002_tws_exit);
}
int open_cfw_gx8002_tws_buffer_init(void)
{
    return LvpInitBuffer();
}
