/* Stock Apollo Quicklist_common_data_handler 0x4ffb38. */
#include <stdint.h>

extern uint32_t audio_quicklist_data_mutex_init_4ffa70(void);
extern uint32_t audio_quicklist_frame_process_55894c(const void *, uint16_t);
extern uint32_t audio_quicklist_decode_558b3c(void);
extern void audio_quicklist_refresh_4f5e84(void);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module[] = "quicklist.page";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\quicklist\\quicklist.c";
static const char function[] = "Quicklist_common_data_handler";
static const char message[] = "Unknown event type: %d";
static const char compact[] = "[quicklist.page]Unknown event type: %d";

uint32_t audio_uart_registry_callback_4ffb38(uint32_t event,
                                               uint32_t payload,
                                               uint32_t length) {
    (void)audio_quicklist_data_mutex_init_4ffa70();
    if(event == 0u) {
        if(audio_quicklist_frame_process_55894c((const void *)(uintptr_t)payload,
                                                  (uint16_t)length) == 0u &&
           audio_quicklist_decode_558b3c() == 0u)
            audio_quicklist_refresh_4f5e84();
    } else {
        if((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, function, 105u, message, event);
        if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08400000u, compact, compact, event);
    }
    return 0u;
}
