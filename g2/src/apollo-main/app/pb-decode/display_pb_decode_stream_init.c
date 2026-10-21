/* Native nanopb buffer-backed input stream constructor 0x48f49c. */
#include <stdint.h>
struct pb_istream_candidate {
    uint32_t (*callback)(void *,void *,uint32_t);
    void *state;uint32_t bytes_left;const char *errmsg;
};
_Static_assert(sizeof(struct pb_istream_candidate)==16u,"native stream size");
extern uint32_t audio_pb_buffer_read_48f3a4(void *,void *,uint32_t);
void audio_uart_pb_stream_init(struct pb_istream_candidate *s,const void *buffer,uint32_t size)
{
    s->callback=audio_pb_buffer_read_48f3a4;
    s->state=(void *)buffer;
    s->bytes_left=size;
    s->errmsg=0;
}
