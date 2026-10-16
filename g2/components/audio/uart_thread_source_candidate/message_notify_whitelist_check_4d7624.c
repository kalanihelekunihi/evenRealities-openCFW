/* Stock Apollo PB_RxNotifWhitelistChk 0x4d7624. */
#include <stdint.h>

struct audio_message_notify_fault_4d7624 {
    uint32_t type;
    uint32_t detail;
    const char *path;
    const char *function;
    uint32_t line;
};
_Static_assert(sizeof(struct audio_message_notify_fault_4d7624) == 20u,
               "fault record ABI");

extern void audio_uart_checksum_copy(void *, const void *, uint32_t);
extern void audio_ring_pb_assert_509b48(const void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "pb.notif";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_notification\\pb_service_notification.c";
static const char function[] = "PB_RxNotifWhitelistChk";
static const char message[] = "POINT NULL";
static const char compact[] = "[pb.notif]POINT NULL";
static const struct audio_message_notify_fault_4d7624 fault_template = {
    0u, 0u, path, function, 0x128u
};

uint32_t audio_message_notify_rx_whitelist_check_4d7624(uint32_t id,
                                                           const void *body) {
    (void)id;
    if (body != 0)
        return 0u;
    struct audio_message_notify_fault_4d7624 fault;
    audio_uart_checksum_copy(&fault, &fault_template, sizeof fault);
    fault.detail = (fault.detail & 0xffff0000u) | 1u;
    audio_ring_pb_assert_509b48(&fault);
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module, path, function, 0x12au, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x04000000u, compact, compact);
    return 2u;
}
