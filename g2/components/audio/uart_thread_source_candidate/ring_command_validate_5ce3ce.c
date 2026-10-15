/* Stock Apollo PB_RxRingEvent validation 0x5ce3ce. */
#include <stdint.h>

struct ring_fault_record {
    uint32_t code;
    uint32_t detail;
    const char *path;
    const char *function;
    uint32_t line;
};
_Static_assert(sizeof(struct ring_fault_record) == 20u, "fault record ABI");

extern void audio_ring_pb_assert_509b48(void *); /* 0x509b48 */
extern void audio_uart_checksum_copy(void *,const void *,uint32_t); /* 0x439c04 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module[] = "pb.ring";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_ring\\pb_service_ring.c";
static const char function[] = "PB_RxRingEvent";
static const char null_message[] = "POINTER NULL";
static const char null_short[] = "[pb.ring]POINTER NULL";
static const char event_message[] = "pEvent:event_id = %d, event_param = %d, ring_mac size = %d";
static const char event_short[] = "[pb.ring]pEvent:event_id = %d, event_param = %d, ring_mac size = %d";
static const char unknown_message[] = "Unknown event_id: %d";
static const char unknown_short[] = "[pb.ring]Unknown event_id: %d";

uint32_t audio_ring_command_validate_5ce3ce(uint32_t unused, const void *event) {
    (void)unused;
    if(event == 0) {
        static const struct ring_fault_record template={0u,0u,path,function,0x58u};
        struct ring_fault_record record;
        audio_uart_checksum_copy(&record,&template,20u);
        record.detail=1u;
        audio_ring_pb_assert_509b48(&record);
        if((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 0x5au, null_message);
        if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04000000u, null_short, null_short);
        return 2u;
    }
    const uint8_t *bytes = event;
    uint32_t id = (uint32_t)bytes[0] | ((uint32_t)bytes[1] << 8u);
    uint32_t value = (uint32_t)bytes[12] | ((uint32_t)bytes[13] << 8u) |
                     ((uint32_t)bytes[14] << 16u) | ((uint32_t)bytes[15] << 24u);
    uint32_t size = bytes[8];
    if((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x5fu,
                           event_message, size, value, id);
    if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0cc00000u, event_short, event_short,
                                    size, value, id);
    if(size != 1u) {
        if((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, function, 0x79u,
                               unknown_message, size);
        if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08400000u, unknown_short,
                                        unknown_short, size);
    }
    return 0u;
}
