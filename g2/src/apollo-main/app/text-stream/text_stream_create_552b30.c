/* Stock text-stream object creation at 0x552b30. */
#include <stdint.h>

extern void *codec_allocate(uint32_t);
extern void audio_file_heap_free(void *);
extern uint32_t audio_even_ai_mutex_create_44971c(const void *);
extern void audio_uart_mutex_delete(uint32_t);
extern uint32_t audio_text_stream_buffer_create_553338(void *, void *, void *, uint32_t);

struct text_stream_object {
    uint32_t first_buffer;       /* 0x00 */
    uint32_t second_buffer;      /* 0x04 */
    uint32_t interval;           /* 0x08 */
    uint32_t word_0c;
    uint32_t text_length;        /* 0x10 */
    uint8_t flag_14;
    uint8_t padding_15[3];
    uint32_t word_18;
    uint32_t word_1c;
    uint32_t mutex;              /* 0x20 */
    uint32_t first_capacity;     /* 0x24 */
    uint32_t second_capacity;    /* 0x28 */
    uint8_t flag_2c;
    uint8_t padding_2d[3];
};
_Static_assert(sizeof(struct text_stream_object) == 0x30u, "stock object extent");

struct text_stream_object *audio_text_stream_create_552b30(void) {
    struct text_stream_object *s = codec_allocate(0x30u);
    if (!s)
        return 0;
    s->first_buffer = 0u;
    s->second_buffer = 0u;
    s->interval = 100u;
    s->word_0c = 0u;
    s->text_length = 0u;
    s->flag_14 = 0u;
    s->word_18 = 0u;
    s->word_1c = 0u;
    s->first_capacity = 0u;
    s->second_capacity = 0u;
    s->flag_2c = 0u;
    s->mutex = audio_even_ai_mutex_create_44971c(0);
    if (!s->mutex) {
        audio_file_heap_free(s);
        return 0;
    }
    if (!audio_text_stream_buffer_create_553338(s, &s->first_buffer,
                                                 &s->first_capacity, 0x200u)) {
        audio_uart_mutex_delete(s->mutex);
        audio_file_heap_free(s);
        return 0;
    }
    if (!audio_text_stream_buffer_create_553338(s, &s->second_buffer,
                                                 &s->second_capacity, 0x200u)) {
        audio_uart_mutex_delete(s->mutex);
        audio_file_heap_free((void *)(uintptr_t)s->first_buffer);
        audio_file_heap_free(s);
        return 0;
    }
    *(uint8_t *)(uintptr_t)s->first_buffer = 0u;
    *(uint8_t *)(uintptr_t)s->second_buffer = 0u;
    return s;
}
