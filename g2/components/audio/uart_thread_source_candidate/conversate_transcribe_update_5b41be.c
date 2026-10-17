/* Native conversate_transcribe_data_update 0x5b41be..0x5b430d. */
#include <stdint.h>

extern uint8_t audio_conversate_prep_note_ram_200d7630[];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);

__attribute__((used, section(".g2_conversate_transcribe_output_200e2ae4")))
uint8_t audio_conversate_transcribe_output_200e2ae4[0x1008];
__attribute__((used, section(".g2_conversate_transcribe_length_2007439c")))
uint32_t audio_conversate_transcribe_length_2007439c;
__attribute__((used, section(".g2_conversate_transcribe_flag_20074fa2")))
uint8_t audio_conversate_transcribe_flag_20074fa2;

static const char module[] = "conversate.data";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_comm_data.c";
static const char function[] = "conversate_transcribe_data_update";
static const char null_message[] = "transcribe_data is NULL";
static const char null_short[] = "[conversate.data]transcribe_data is NULL";

static uint16_t half(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | (uint16_t)((uint16_t)p[1] << 8));
}

static void set_half(uint8_t *p, uint16_t value) {
    p[0] = (uint8_t)value;
    p[1] = (uint8_t)(value >> 8);
}

static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
        ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

void audio_conversate_transcribe_update_5b41be(const void *input) {
    if (!input) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 160u, null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, null_short, null_short);
        return;
    }
    const uint8_t *const data = input;
    uint8_t *const ring = audio_conversate_prep_note_ram_200d7630 + 0x88u;
    uint8_t *const index_cell = ring + 0x1008u;
    uint32_t index = *index_cell;
    uint8_t *slot = ring + index * 0x402u;
    if (audio_conversate_transcribe_flag_20074fa2 == 1u) {
        audio_conversate_transcribe_flag_20074fa2 = 0u;
        uint16_t prior_size = half(slot);
        if (prior_size < 0x401u) {
            slot[2u + prior_size] = 10u;
            set_half(slot, (uint16_t)(prior_size + 1u));
        }
        index = (index + 1u) % 4u;
        *index_cell = (uint8_t)index;
        slot = ring + index * 0x402u;
    }
    audio_uart_buffer_zero(slot, 0x402u, 0u);
    uint16_t size = half(data);
    (void)audio_queue_copy_bytes(slot + 2u, data + 2u, size);
    set_half(slot, size);
    if (word(data + 0x404u) == 1u)
        audio_conversate_transcribe_flag_20074fa2 = 1u;
    audio_uart_buffer_zero(audio_conversate_transcribe_output_200e2ae4,
                           0x1008u, 0u);
    audio_conversate_transcribe_length_2007439c = 0u;
    for (uint32_t i = 0u; i < 4u; ++i) {
        uint32_t next = (i + (uint32_t)(*index_cell) + 1u) % 4u;
        uint8_t *const item = ring + next * 0x402u;
        uint16_t item_size = half(item);
        if (item_size == 0u)
            continue;
        uint32_t offset = audio_conversate_transcribe_length_2007439c;
        (void)audio_queue_copy_bytes(audio_conversate_transcribe_output_200e2ae4 + offset,
                                     item + 2u, item_size);
        audio_conversate_transcribe_length_2007439c = offset + item_size;
    }
}
