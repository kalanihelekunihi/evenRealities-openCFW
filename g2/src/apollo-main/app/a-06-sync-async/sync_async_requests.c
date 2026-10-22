/* Stock D:\01_workspace\s200_ap510b_iar_git\framework\sync\sync_framework.c
 * (log tag "sync.module.framework"), deferred master-side requests.
 * Native rows:
 *   _AsyncReflashApplicationDataHandlerCb      0x45a9e6..0x45aaca
 *   AsyncRequestDisplayReflash                 0x45aaca..0x45abc4
 *   _AsyncSendInputEventToPeersDataHandlerCb   0x45abc4..0x45accc
 *   AsyncSendInputEventToPeers                 0x45accc..0x45adde
 * Literal pools 0x45b0fc..0x45b140, 0x45b580..0x45b584, 0x45b6d8..0x45b6e0,
 * 0x45b83c..0x45b848.
 *
 * Same pattern as AsyncRequestDisplayStartUp 0x45a8ee / its callback 0x45a80a
 * (app/system-alert): the submitter copies a little-endian delay word plus
 * payload into a heap packet and posts it to the work pool 0x491184; the
 * callback sleeps for the delay (0x454b4c), forwards to the sync-interface
 * API and frees the packet. */
#include <stdint.h>

typedef void (*sync_async_work_fn)(uint32_t, void *, uint32_t, uint32_t);

extern void *file_heap_allocate(uint32_t size);                     /* 0x474cd2 */
extern void file_heap_free(void *buffer);                           /* 0x474d16 */
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t); /* 0x439be4 memcpy */
extern uint32_t audio_uart_timeout_submit(sync_async_work_fn, uint32_t,
                                          void *, uint32_t, uint32_t); /* 0x491184 */
extern void audio_uart_task_delay(uint32_t ticks);                  /* 0x454b4c */
extern void audio_uart_master_display_refresh(uint32_t, const void *, uint16_t,
                                              uint32_t);            /* 0x464bb2 */
extern void audio_uart_master_input_event(uint32_t, uint32_t, uint32_t,
                                          uint32_t);                /* 0x465748 */
extern uint32_t audio_log_flags(void);                              /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);        /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module[] = "sync.module.framework"; /* ROM 0x77c07c */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c"; /* ROM 0x705fb8 */
static const char fn_reflash_cb[] = "_AsyncReflashApplicationDataHandlerCb"; /* ROM 0x74ea4c */
static const char fn_reflash[] = "AsyncRequestDisplayReflash";               /* ROM 0x77266c */
static const char fn_input_cb[] = "_AsyncSendInputEventToPeersDataHandlerCb"; /* ROM 0x743e60 */
static const char fn_input[] = "AsyncSendInputEventToPeers";                 /* ROM 0x772688 */
static const char e_null[] = "user data packet is null";                      /* ROM 0x772618 */
static const char c_null[] = "[sync.module.framework]user data packet is null"; /* ROM 0x738bf4 */
static const char e_delay[] = "delay_time = %d,restart appid = %d";           /* ROM 0x75a5cc */
static const char c_delay[] =
    "[sync.module.framework]delay_time = %d,restart appid = %d";             /* ROM 0x718f04 */
static const char e_alloc[] = "malloc %d bytes user data packet failed";      /* ROM 0x74e9fc */
static const char c_alloc[] =
    "[sync.module.framework]malloc %d bytes user data packet failed";        /* ROM 0x70f524 */
static const char e_alloc14[] = "malloc 14bytes user data packet failed";     /* ROM 0x74ea74 */
static const char c_alloc14[] =
    "[sync.module.framework]malloc 14bytes user data packet failed";         /* ROM 0x70f564 */
static const char e_submit[] = "submit work failed";                          /* ROM 0x783ba4 */
static const char c_submit[] = "[sync.module.framework]submit work failed";   /* ROM 0x743e34 */

static uint32_t read_le32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) | ((uint32_t)p[2] << 16u) |
           ((uint32_t)p[3] << 24u);
}

static void write_le32(uint8_t *p, uint32_t value)
{
    p[0] = (uint8_t)value;
    p[1] = (uint8_t)(value >> 8u);
    p[2] = (uint8_t)(value >> 16u);
    p[3] = (uint8_t)(value >> 24u);
}

/* Packet: delay(le32) then the refresh payload; length 4 means no payload. */
void async_reflash_application_data_handler_cb_45a9e6(uint32_t application,
                                                      void *packet,
                                                      uint32_t length,
                                                      uint32_t unused)
{
    (void)unused;
    if (packet == 0) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, fn_reflash_cb, 233u, e_null);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compress_log_output(0x08000000u, c_null, c_null);
        return;
    }
    const uint8_t *bytes = packet;
    uint32_t delay = read_le32(bytes);
    audio_uart_task_delay(delay);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, fn_reflash_cb, 239u, e_delay, delay,
                           application);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x0c800000u, c_delay, c_delay, delay, application);
    if (length == 4u)
        audio_uart_master_display_refresh((uint16_t)application, 0, 0u, 0u);
    else
        audio_uart_master_display_refresh((uint16_t)application, bytes + 4u,
                                          (uint16_t)(length - 4u), 0u);
    file_heap_free(packet);
}

/* Returns 0 when queued, -1 on allocation or submit failure. */
int32_t async_request_display_reflash_45aaca(uint32_t application,
                                             const void *payload,
                                             uint32_t length, uint32_t delay)
{
    uint8_t *packet = file_heap_allocate(length + 4u);
    if (packet == 0) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, fn_reflash, 251u, e_alloc, length);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compress_log_output(0x08400000u, c_alloc, c_alloc, length);
        return -1;
    }
    write_le32(packet, delay);
    (void)audio_queue_copy_bytes(packet + 4u, payload, length);
    if (audio_uart_timeout_submit(async_reflash_application_data_handler_cb_45a9e6,
                                  application, packet, length + 4u, 0u) == 0u)
        return 0;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(2u, module, path, fn_reflash, 261u, e_submit);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x08000000u, c_submit, c_submit);
    file_heap_free(packet);
    return -1;
}

/* Packet (14 bytes): +0 delay le32, +4 event le16, +6 arg0 le32, +10 arg1 le32. */
void async_send_input_event_to_peers_data_handler_cb_45abc4(uint32_t application,
                                                            void *packet,
                                                            uint32_t length,
                                                            uint32_t unused)
{
    (void)length;
    (void)unused;
    if (packet == 0) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, fn_input_cb, 274u, e_null);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compress_log_output(0x08000000u, c_null, c_null);
        return;
    }
    const uint8_t *bytes = packet;
    uint32_t delay = read_le32(bytes);
    uint16_t event = (uint16_t)(bytes[4] | ((uint32_t)bytes[5] << 8u));
    uint32_t arg0 = read_le32(bytes + 6u);
    uint32_t arg1 = read_le32(bytes + 10u);
    audio_uart_task_delay(delay);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, fn_input_cb, 282u, e_delay, delay,
                           application);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x0c800000u, c_delay, c_delay, delay, application);
    audio_uart_master_input_event(event, arg0, arg1, 0u);
    file_heap_free(packet);
}

/* Submitted with application id 0; returns 0 when queued, -1 on failure. */
int32_t async_send_input_event_to_peers_45accc(uint16_t event, uint32_t arg0,
                                               uint32_t arg1, uint32_t delay)
{
    uint8_t *packet = file_heap_allocate(14u);
    if (packet == 0) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, fn_input, 290u, e_alloc14);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compress_log_output(0x08000000u, c_alloc14, c_alloc14);
        return -1;
    }
    write_le32(packet, delay);
    packet[4] = (uint8_t)event;
    packet[5] = (uint8_t)(event >> 8u);
    write_le32(packet + 6u, arg0);
    write_le32(packet + 10u, arg1);
    if (audio_uart_timeout_submit(async_send_input_event_to_peers_data_handler_cb_45abc4,
                                  0u, packet, 14u, 0u) == 0u)
        return 0;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(2u, module, path, fn_input, 310u, e_submit);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x08000000u, c_submit, c_submit);
    file_heap_free(packet);
    return -1;
}
