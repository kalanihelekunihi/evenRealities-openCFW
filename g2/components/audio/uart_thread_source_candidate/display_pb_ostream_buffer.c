/* Native nanopb pb_ostream_from_buffer 0x4905f4. */
#include <stdint.h>
struct pb_ostream_candidate {void *callback;void *state;uint32_t max_size;uint32_t bytes_written;const char *errmsg;};
_Static_assert(sizeof(struct pb_ostream_candidate)==20u,"nanopb ostream ABI");
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */
uint32_t audio_pb_buffer_write(void *stream_ptr,const uint8_t *source,uint32_t count) {
    struct pb_ostream_candidate *stream=(struct pb_ostream_candidate *)stream_ptr;
    uint8_t *destination=(uint8_t *)stream->state;
    stream->state=destination+count;
    (void)audio_queue_copy_bytes(destination,source,count);
    return 1u;
}
void audio_pb_ostream_from_buffer(struct pb_ostream_candidate *out,void *buffer,uint32_t length) {
    out->callback=(void *)audio_pb_buffer_write;
    out->state=buffer;
    out->max_size=length;
    out->bytes_written=0u;
    out->errmsg=0;
}
