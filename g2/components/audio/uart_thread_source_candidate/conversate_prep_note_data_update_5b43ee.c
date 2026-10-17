/* Native conversate_prep_note_data_update 0x5b43ee..0x5b44d7. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);

/* The stock clear ranges overlap by four bytes; keep their address relation. */
__attribute__((used, section(".g2_conversate_prep_note_ram_200d7630")))
uint8_t audio_conversate_prep_note_ram_200d7630[0xb4b1];

static const char module[] = "conversate.data";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_comm_data.c";
static const char function[] = "conversate_prep_note_data_update";
static const char null_message[] = "prep_note is NULL";
static const char null_short[] = "[conversate.data]prep_note is NULL";
static const char update_message[] =
    "prep note update: title_size=%u, total_packets=%u";
static const char update_short[] =
    "[conversate.data]prep note update: title_size=%u, total_packets=%u";

void audio_conversate_prep_note_update_5b43ee(const void *input) {
    if (!input) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 264u, null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, null_short, null_short);
        return;
    }
    uint8_t *const data = audio_conversate_prep_note_ram_200d7630;
    (void)audio_queue_copy_bytes(data, input, 136u);
    const uint16_t title_size = (uint16_t)((uint16_t)data[0] |
                                            ((uint16_t)data[1] << 8));
    if (title_size < 128u)
        data[2u + title_size] = 0u;
    audio_uart_buffer_zero(data + 0x7e00u, 14001u, 0u);
    audio_uart_buffer_zero(data + 0x1094u, 28012u, 0u);
    const uint32_t packets = (uint32_t)data[0x84] |
        ((uint32_t)data[0x85] << 8) |
        ((uint32_t)data[0x86] << 16) |
        ((uint32_t)data[0x87] << 24);
    data[0x1094] = (uint8_t)packets;
    data[0x1095] = (uint8_t)(packets >> 8);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 278u, update_message,
                           title_size, packets);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0c800000u, update_short, update_short,
                         title_size, packets);
}
