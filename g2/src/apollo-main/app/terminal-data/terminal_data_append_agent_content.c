/* Native terminal_data_append_agent_content 0x597a96. */
#include <stdint.h>

extern uint8_t audio_td_state[0xa1dcu]; /* native base 0x2010fd20 */
extern void audio_td_session_ring_reset(void);
extern uint32_t audio_td_session_find_by_id(uint8_t *, uint32_t, uint16_t *);
extern uint32_t audio_td_ring_index_wrap(uint8_t *, uint16_t);
extern uint32_t audio_td_record_build_from_event(uint8_t *, const uint8_t *,
                                                 uint32_t, uint32_t);
extern uint8_t *audio_td_session_ring_append(uint8_t, uint8_t *);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[]="terminal.data";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_data.c";
static const char function[]="terminal_data_append_agent_content";
static const char absent[]="ignore replace content: id=%u not found";
static const char absent_short[]="[terminal.data]ignore replace content: id=%u not found";

static uint16_t load16(const uint8_t *p) {
    return (uint16_t)p[0] | (uint16_t)((uint16_t)p[1] << 8);
}
static uint32_t load32(const uint8_t *p) {
    return (uint32_t)p[0] | (uint32_t)p[1] << 8 |
           (uint32_t)p[2] << 16 | (uint32_t)p[3] << 24;
}
static void store16(uint8_t *p, uint16_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8);
}
static void store32(uint8_t *p, uint32_t v) {
    for (unsigned i = 0; i < 4u; ++i) p[i] = (uint8_t)(v >> (i*8u));
}

/* Stock 0x597A96 (terminal_data_append_agent_content) */
uint8_t audio_terminal_data_append_agent_content(const void *payload,
                                                  uint16_t *out_index) {
    uint8_t *ring = audio_td_state + 0x1054u; /* RAM 0x20110d74 */
    if (out_index != 0) *out_index = 0xffffu;
    if (payload == 0) return 0u;
    const uint8_t *packet = (const uint8_t *)payload;
    if (load32(ring + 0x8504u) == 0u) audio_td_session_ring_reset();
    uint32_t session = load32(packet + 0x208u);
    uint8_t is_new = packet[0x204u] == 1u;
    if (!is_new || session == 0u) {
        uint8_t kind = 0u;
        uint8_t *row = audio_td_session_ring_append(is_new, &kind);
        if (row == 0) return 0u;
        (void)audio_td_record_build_from_event(row, packet, session, 0u);
        if (kind == 3u && out_index != 0 && load16(ring + 0x8500u) != 0u)
            *out_index = (uint16_t)(load16(ring + 0x8500u) - 1u);
        return kind;
    }
    uint16_t logical_index = 0u;
    if (audio_td_session_find_by_id(ring, session, &logical_index) == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u,module,path,function,0x279u,absent,session);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x8400000u,absent_short,absent_short,session);
        return 0u;
    }
    uint16_t physical_index = (uint16_t)audio_td_ring_index_wrap(ring, logical_index);
    uint8_t *row = ring + (uint32_t)physical_index * 0x214u;
    uint32_t tail_210 = load32(row + 0x210u);
    uint32_t tail_20c = load32(row + 0x20cu);
    uint16_t tail_206 = load16(row + 0x206u);
    audio_uart_buffer_zero(row, 0x214u, 0u);
    store32(row + 0x210u, tail_210);
    store32(row + 0x20cu, tail_20c);
    store16(row + 0x206u, tail_206);
    (void)audio_td_record_build_from_event(row, packet, session, 0u);
    if (out_index != 0) *out_index = logical_index;
    return 3u;
}
