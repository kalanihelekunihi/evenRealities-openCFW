/* Stock Apollo RingDataRelay_common_data_handler 0x5ce690. */
#include <stdint.h>

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern uint32_t audio_ring_data_relay_5ce1dc(const void *, uint16_t);

static const char module[] = "pb.ring";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_ring\\pb_service_ring.c";
static const char function[] = "RingDataRelay_common_data_handler";
static const char received[] = "ring recv eventType = %d, len = %d";
static const char received_short[] = "[pb.ring]ring recv eventType = %d, len = %d";
static const char unknown[] = "Unknown event type: %d";
static const char unknown_short[] = "[pb.ring]Unknown event type: %d";

uint32_t audio_uart_registry_callback_5ce690(uint32_t event,
                                               uint32_t payload,
                                               uint32_t length) {
    if((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 0x105u,
                           received, event, length);
    if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10800000u, received_short,
                                    received_short, event, length);
    if(event == 0u) {
        (void)audio_ring_data_relay_5ce1dc((const void *)(uintptr_t)payload,
                                            (uint16_t)length);
    } else {
        if((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, function, 0x113u,
                               unknown, event);
        if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08400000u, unknown_short,
                                        unknown_short, event);
    }
    return 0u;
}
