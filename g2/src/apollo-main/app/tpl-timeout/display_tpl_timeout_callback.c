/* Native _rxNextPacketTimeout 0x4b8c6c, a scheduled TPL BLE handoff. */
#include <stdint.h>
extern uint8_t audio_ble_controller[]; /* direct native base 0x200727f0; live */
extern void *WsfMsgAlloc(uint16_t length); /* selected 0x4bf99e */
extern void WsfMsgSend(uint8_t handler, void *message); /* selected 0x4bf9ba */
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t); /* selected 0x439be4 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "prot.tran";
static const char source[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\transport_protocol\\transport_protocol.c";
static const char function[] = "_rxNextPacketTimeout";
static const char missing[] = "_rxNextPacketTimeout: pBleCb or handlerId is NULL";
static const char missing_short[] = "[prot.tran]_rxNextPacketTimeout: pBleCb or handlerId is NULL";
static const char forward[] = "_rxNextPacketTimeout: forwarding to BLE thread, serviceID=%d, syncID=%d, pipeID=%d";
static const char forward_short[] = "[prot.tran]_rxNextPacketTimeout: forwarding to BLE thread, serviceID=%d, syncID=%d, pipeID=%d";
static const char alloc_fail[] = "_rxNextPacketTimeout: failed to allocate message";
static const char alloc_fail_short[] = "[prot.tran]_rxNextPacketTimeout: failed to allocate message";

static uint8_t ext(void) { return (audio_log_level() & 2u) != 0u; }
static uint8_t compact(void)
{
    return (audio_log_level() & 1u) != 0u || (audio_log_level() & 4u) != 0u;
}

/* Stock 0x4B8C6C (_rxNextPacketTimeout) */
void audio_tpl_rx_next_packet_timeout(const uint8_t *ids)
{
    if (audio_ble_controller[0x56u] == 0u) {
        if (ext()) audio_log_extended(1u, module, source, function, 0x103u, missing);
        if (compact()) (void)compressed_log_output(0x04000000u, missing_short, missing_short);
        return;
    }
    if (ext())
        audio_log_extended(2u, module, source, function, 0x108u, forward,
                           ids[0], ids[1], ids[2]);
    if (compact())
        (void)compressed_log_output(0x08c00000u, forward_short, forward_short,
                                    ids[0], ids[1], ids[2]);
    uint8_t *message = WsfMsgAlloc(0x0fu);
    if (message == 0) {
        if (ext()) audio_log_extended(1u, module, source, function, 0x115u, alloc_fail);
        if (compact()) (void)compressed_log_output(0x04000000u, alloc_fail_short, alloc_fail_short);
        return;
    }
    message[0] = 0u;
    message[1] = 0u;
    message[2] = 0xb8u;
    uint32_t payload = (uint32_t)(uintptr_t)(message + 12u);
    __builtin_memcpy(message + 4u, &payload, 4u);
    (void)audio_queue_copy_bytes(message + 12u, ids, 3u);
    message[8] = 3u;
    message[9] = 0u;
    WsfMsgSend(audio_ble_controller[0x56u], message);
}
