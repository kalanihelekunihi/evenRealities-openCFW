/* Conversate timer manager helpers, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\conversate\conversate_timer_mgr.c.
 * Native 0x5b3a5a..0x5b3a87, 0x5b3c2a..0x5b3c6f and 0x5b3c70..0x5b3cb9
 * (literal pool 0x5b3e14..0x5b3ed0).
 *
 * Timer manager block, RAM 0x20073a3c (0x1c bytes, three timers):
 *   +0x00 loading timer running, +0x08 select timer running,
 *   +0x10 auto-extend timer running, +0x18 auto-extend countdown
 *   (0xffffffff = restart the countdown on the next tick). */
#include <stdint.h>
#include <stdbool.h>
#include "conversate_ui_context.h"

#define LOG_MODULE module
#define LOG_PATH path

extern uint8_t audio_conversate_timer_mgr_ram_20073a3c[0x1c]; /* RAM 0x20073a3c */
extern uint32_t display_driver_uled_mode_45a568(void);       /* device role, 1 = master */
extern void audio_conversate_timer_2_start_5b37d8(void);      /* select timeout start */

static const char module[] = "conversate.timer"; /* ROM 0x77ea8c */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_timer_mgr.c"; /* ROM 0x6ec668 */
static const char reset_fn[] = "conversate_timer_mgr_set_auto_extend_countdown_reset"; /* ROM 0x71d0d8 */
static const char reset_msg[] = "Set auto extend countdown reset"; /* ROM 0x75ea70 */
static const char reset_c[] = "[conversate.timer]Set auto extend countdown reset"; /* ROM 0x727d60 */
static const char select_fn[] = "conversate_timer_mgr_reset_select_timeout"; /* ROM 0x73ced4 */
static const char select_msg[] = "Select timeout reset/start"; /* ROM 0x76a578 */
static const char select_c[] = "[conversate.timer]Select timeout reset/start"; /* ROM 0x7326b4 */

/* Auto-extend timer is armed and the tag page (state 4, unselected) was
 * opened by an auto pop. */
bool conversate_timer_auto_extend_active_5b3a5a(void)
{
    const g2_conversate_ui_t *const ui = G2_CONVERSATE_UI;

    return audio_conversate_timer_mgr_ram_20073a3c[0x10] != 0u && ui->state == 4u &&
           ui->selected == 0u && ui->tracking.open_type == 1u;
}

void conversate_timer_mgr_set_auto_extend_countdown_reset_5b3c2a(void)
{
    *(uint32_t *)(void *)(audio_conversate_timer_mgr_ram_20073a3c + 0x18) = UINT32_MAX;
    CONV_LOG0(4u, reset_fn, 0x158u, 0x10000000u, reset_msg, reset_c);
}

void conversate_timer_mgr_reset_select_timeout_5b3c70(void)
{
    if (display_driver_uled_mode_45a568() == 1u) {
        audio_conversate_timer_2_start_5b37d8();
        CONV_LOG0(4u, select_fn, 0x162u, 0x10000000u, select_msg, select_c);
    }
}
