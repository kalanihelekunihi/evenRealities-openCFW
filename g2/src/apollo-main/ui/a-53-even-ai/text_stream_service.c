/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenAI\text_stream_service.c
 * Native rows 0x552be6..0x552c1f (destroy), 0x552cdc..0x552ce7, 0x552cf8..0x552d0f
 * (accessors), 0x552d74..0x552db1 (stop/delete timer) and 0x5531a8..0x553273
 * (copy one UTF-8 character). The rest of this stock file lives in
 * app/text-stream/ and rtos/text-stream/.
 *
 * A stream holds the text already shown ("current") and the full target text
 * ("pending"); a periodic timer reveals the pending text one UTF-8 character
 * at a time and passes the current text to the update callback. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    char *current;            /* +0x00 shown text */
    char *pending;            /* +0x04 target text */
    uint32_t interval;        /* +0x08 ms per step */
    int32_t current_length;   /* +0x0c */
    int32_t pending_length;   /* +0x10 */
    uint8_t stopped;          /* +0x14 */
    uint8_t reserved_15[3];
    void (*update_cb)(const char *text); /* +0x18 */
    void *timer;              /* +0x1c osTimerId_t */
    void *mutex;              /* +0x20 osMutexId_t */
    uint32_t current_capacity; /* +0x24 */
    uint32_t pending_capacity; /* +0x28 */
    uint8_t flag_2c;
    uint8_t reserved_2d[3];
} g2_text_stream_t;
_Static_assert(sizeof(g2_text_stream_t) == 0x30, "stock object extent");
_Static_assert(offsetof(g2_text_stream_t, mutex) == 0x20, "mutex at +0x20");

extern const char audio_text_stream_empty_552cf4[1]; /* ROM 0x552cf4 "" */

extern int32_t osMutexAcquire(void *mutex, uint32_t timeout); /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                   /* 0x44981c */
extern int32_t osMutexDelete(void *mutex);                    /* 0x44986e */
extern int32_t osTimerStop(void *timer);
extern int32_t osTimerDelete(void *timer);                    /* 0x44953e */
extern void file_heap_free(void *buffer);                     /* 0x474d16 */
/* ensure_text_capacity: grows *buffer to at least size bytes, nonzero on success. */
extern uint32_t audio_text_stream_buffer_create_553338(void *stream, void *buffer, void *capacity, uint32_t size);

void text_stream_stop_and_delete_animation(g2_text_stream_t *stream);

void text_stream_destroy(g2_text_stream_t *stream)
{
    if (stream == NULL)
        return;
    text_stream_stop_and_delete_animation(stream);
    if (stream->mutex != NULL)
        (void)osMutexDelete(stream->mutex);
    if (stream->current != NULL)
        file_heap_free(stream->current);
    if (stream->pending != NULL)
        file_heap_free(stream->pending);
    file_heap_free(stream);
}

const char *text_stream_current_text(const g2_text_stream_t *stream)
{
    if (stream == NULL)
        return audio_text_stream_empty_552cf4;
    return stream->current;
}

int32_t text_stream_current_length(const g2_text_stream_t *stream)
{
    if (stream == NULL)
        return 0;
    return stream->current_length;
}

int32_t text_stream_pending_length(const g2_text_stream_t *stream)
{
    if (stream == NULL)
        return 0;
    return stream->pending_length;
}

void text_stream_stop_and_delete_animation(g2_text_stream_t *stream)
{
    if (stream == NULL)
        return;
    stream->stopped = 1u;
    if (stream->mutex == NULL || osMutexAcquire(stream->mutex, 0xffffffffu) != 0)
        return;
    if (stream->timer != NULL) {
        (void)osTimerStop(stream->timer);
        (void)osTimerDelete(stream->timer);
        stream->timer = NULL;
    }
    (void)osMutexRelease(stream->mutex);
}

/* Appends the next whole UTF-8 character (1..4 bytes by lead byte, truncated
 * at the pending length) of the pending text to the current text; with
 * notify set, then reports the current text to the update callback. */
void text_stream_copy_until_boundary(g2_text_stream_t *stream, uint8_t notify)
{
    if (stream == NULL)
        return;
    if (stream->mutex != NULL && osMutexAcquire(stream->mutex, 0xffffffffu) == 0) {
        if (stream->current_length < stream->pending_length) {
            if (audio_text_stream_buffer_create_553338(stream, &stream->current, &stream->current_capacity,
                                                       (uint32_t)stream->pending_length + 1u) == 0u) {
                (void)osMutexRelease(stream->mutex);
                return;
            }
            uint32_t width = 1u;
            uint8_t lead = (uint8_t)stream->pending[stream->current_length];
            if (lead >= 0x80u) {
                if ((lead & 0xe0u) == 0xc0u)
                    width = 2u;
                else if ((lead & 0xf0u) == 0xe0u)
                    width = 3u;
                else if ((lead & 0xf8u) == 0xf0u)
                    width = 4u;
            }
            for (uint32_t i = 0u; i < width && (int32_t)(i + (uint32_t)stream->current_length) < stream->pending_length;
                 i++)
                stream->current[i + (uint32_t)stream->current_length] =
                    stream->pending[i + (uint32_t)stream->current_length];
            stream->current[width + (uint32_t)stream->current_length] = '\0';
            stream->current_length = (int32_t)(width + (uint32_t)stream->current_length);
        }
        (void)osMutexRelease(stream->mutex);
    }
    if (notify != 0u && stream->update_cb != NULL)
        stream->update_cb(stream->current);
}
