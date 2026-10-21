/* Stock SendDataToBothExt, 0x464f76..0x4651aa. */
#include <stdint.h>

extern void *g2_uart_send_queue; /* 0x200749cc */
extern void *g2_uart_thread_event; /* 0x20074b10 */
extern void *audio_uart_alloc_retry(uint32_t); /* 0x4646f0 */
extern void audio_file_heap_free(void *); /* 0x474d16 */
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t); /* 0x439be4 */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* 0x43c0e4 */
extern int32_t audio_cmsis_queue_put(void *, const void *, uint8_t, uint32_t); /* 0x449abe */
extern uint32_t g2_log_event_set_task(uint32_t, uint32_t); /* 0x4495e4 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

typedef struct {
    uint32_t id;
    uint16_t type;
    uint16_t size;
    uint8_t *payload;
} both_node;
_Static_assert(sizeof(both_node) == 12u, "native sync send node size");

static const char module[] = "sync.module.api";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_interface_api.c";
static const char function[] = "SendDataToBothExt";
static const char queue_missing[] = "uart send queue is NULL !!!";
static const char alloc_failure[] = "malloc failed after retries!";
static const char queued[] = "_pSyncPacketStruct = %p";
static const char enqueue_failure[] = "send msg to g_syncScheduleMgr_queue failed,errno = %d";
static const char queue_missing_short[] = "[sync.module.api]uart send queue is NULL !!!";
static const char alloc_failure_short[] = "[sync.module.api]malloc failed after retries!";
static const char queued_short[] = "[sync.module.api]_pSyncPacketStruct = %p";
static const char enqueue_failure_short[] = "[sync.module.api]send msg to g_syncScheduleMgr_queue failed,errno = %d";

static void log_error(uint32_t line, const char *message, const char *short_message)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(1u, module, path, function, line, message);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x04000000u, short_message, short_message);
}

uint32_t audio_sync_send_to_both_ext_464f76(uint32_t app, const void *bytes,
                                             uint32_t length, uint32_t id,
                                             uint32_t event)
{
    if (g2_uart_send_queue == 0) {
        log_error(0xc0u, queue_missing, queue_missing_short);
        return UINT32_MAX;
    }
    both_node *node = audio_uart_alloc_retry(12u);
    if (node == 0) {
        log_error(0xc8u, alloc_failure, alloc_failure_short);
        return UINT32_MAX;
    }
    audio_uart_buffer_zero(node, 12u, 0u);
    const uint16_t n = (uint16_t)length;
    node->payload = audio_uart_alloc_retry((uint32_t)n + 8u);
    if (node->payload == 0) {
        log_error(0xceu, alloc_failure, alloc_failure_short);
        audio_file_heap_free(node);
        return UINT32_MAX;
    }
    node->id = id;
    node->type = 1u;
    node->size = (uint16_t)(n + 8u);
    uint8_t *packet = node->payload;
    packet[0] = 1u;
    packet[1] = 9u;
    packet[2] = (uint8_t)app;
    packet[3] = (uint8_t)(app >> 8);
    packet[4] = (uint8_t)event;
    packet[5] = (uint8_t)(event >> 8);
    packet[6] = (uint8_t)n;
    packet[7] = (uint8_t)(n >> 8);
    (void)audio_queue_copy_bytes(packet + 8u, bytes, n);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 0xe1u, queued, node);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, queued_short, queued_short, node);
    int32_t status = audio_cmsis_queue_put(g2_uart_send_queue, &node, 0u, 2000u);
    if (status != 0) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, function, 0xe4u,
                               enqueue_failure, status);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08400000u, enqueue_failure_short,
                                        enqueue_failure_short, status);
        audio_file_heap_free(node->payload);
        audio_file_heap_free(node);
        return UINT32_MAX;
    }
    (void)g2_log_event_set_task((uint32_t)(uintptr_t)g2_uart_thread_event, 2u);
    return 0u;
}
