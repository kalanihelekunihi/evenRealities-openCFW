/* Charging-case (box) state accessors, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\box_detect\service_box_detect.c.
 * Native 0x4abfac, 0x4ac130..0x4ac16b, 0x4ac59a, 0x4ac718, 0x4ac72e, 0x4ac744,
 * 0x4ac75a and 0x4acac0; literal pools 0x4aca98 (timer cell), 0x4acafc (local
 * record) and 0x4acdd0 (peer record).
 *
 * Local case record at RAM 0x20074928: +0 SoC, +1 charging, +2 lid open,
 * +3 in case. Every setter stores its byte and then runs the change check
 * 0x4ac798, which syncs the record to the peer when it differs from the last
 * sent copy. The getters for +0..+2 (0x4ac726, 0x4ac73c, 0x4ac752) live in
 * app/case-send; the peer record mirror at RAM 0x20074188 (+4..+7 SoC,
 * charging, lid, in case) is written by app/case-sync. */
#include <stdint.h>

extern uint8_t g2_box_case_state[4];                /* RAM 0x20074928 */
extern void *audio_box_detect_timer;               /* RAM 0x20074920 box_detect_out_timer */
extern volatile uint8_t audio_uart_case_sensor_a;   /* RAM 0x2007418f, peer record +7 (in case) */

extern void audio_uart_case_force_out_apply_4ac798(void);           /* 0x4ac798 */
extern uint8_t audio_uart_case_local_lid_4ac752(void);              /* 0x4ac752 */
extern uint32_t osTimerIsRunning(void *timer);                      /* 0x449522 */
extern int32_t osTimerStop(void *timer);                            /* 0x4494d8 */
extern int32_t osTimerStart(void *timer, uint32_t ticks);           /* 0x449498 */

#define BOX_DETECT_OUT_DELAY_MS 3000u

void box_detect_set_in_case_4abfac(uint8_t in_case)
{
    g2_box_case_state[3] = in_case;
    audio_uart_case_force_out_apply_4ac798();
}

/* VBUS attached: cancel a pending out-of-box debounce and report in case. */
void box_detect_vbus_connected_4ac130(void)
{
    if (audio_box_detect_timer != 0 && osTimerIsRunning(audio_box_detect_timer) != 0u)
        (void)osTimerStop(audio_box_detect_timer);
    box_detect_set_in_case_4abfac(1u);
}

/* VBUS removed: the out-of-box state is only reported when the 3 s timer fires. */
void box_detect_vbus_removed_4ac154(void)
{
    if (audio_box_detect_timer != 0)
        (void)osTimerStart(audio_box_detect_timer, BOX_DETECT_OUT_DELAY_MS);
}

uint8_t box_detect_get_in_case_4ac59a(void)
{
    return g2_box_case_state[3];
}

void box_detect_set_soc_4ac718(uint8_t soc)
{
    g2_box_case_state[0] = soc;
    audio_uart_case_force_out_apply_4ac798();
}

void box_detect_set_charging_4ac72e(uint8_t charging)
{
    g2_box_case_state[1] = charging;
    audio_uart_case_force_out_apply_4ac798();
}

void box_detect_set_lid_open_4ac744(uint8_t lid_open)
{
    g2_box_case_state[2] = lid_open;
    audio_uart_case_force_out_apply_4ac798();
}

/* Local side counts as "at the case" when it is in the case or the lid is open. */
uint8_t box_detect_local_case_status_4ac75a(void)
{
    if (box_detect_get_in_case_4ac59a() == 1u || audio_uart_case_local_lid_4ac752() == 1u)
        return 1u;
    return 0u;
}

uint8_t box_detect_peer_in_case_4acac0(void)
{
    return audio_uart_case_sensor_a;
}
