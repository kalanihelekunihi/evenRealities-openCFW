/* Stock td_record_elapsed_get at 0x59769c. */
#include <stdint.h>

extern uint8_t *audio_td_current_record(uint32_t session);
extern uint32_t audio_uart_ring_rtc_refresh(void);

uint32_t audio_td_record_elapsed_get_59769c(uint32_t session,
                                              uint32_t *elapsed) {
    if (elapsed == 0)
        return 0u;
    *elapsed = 0u;
    const uint8_t *record = audio_td_current_record(session);
    if (record == 0)
        return 0u;
    uint32_t start = *(const uint32_t *)(const void *)(record + 0x88u);
    if (start == 0u)
        return 0u;
    uint32_t now = audio_uart_ring_rtc_refresh();
    if (now < start)
        return 0u;
    *elapsed = now - start;
    return 1u;
}
