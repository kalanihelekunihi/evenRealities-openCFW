/* Native nanopb callback scalar payload copier 0x48f6ea. */
#include <stdint.h>
struct pb_istream_candidate { uint32_t (*callback)(void *,void *,uint32_t);void *state;uint32_t bytes_left;const char *errmsg; };
extern uint32_t audio_pb_read_stream_48f3be(struct pb_istream_candidate *,void *,uint32_t);
static const char pb_varint_overflow[]="varint overflow"; /* ROM 0x787c80 */
static const char pb_invalid_wire_type[]="invalid wire_type"; /* ROM 0x7817dc */
uint32_t audio_pb_callback_payload_48f6ea(struct pb_istream_candidate *s,uint32_t wire,void *buffer,uint32_t *length)
{
    uint8_t *out=(uint8_t *)buffer;
    uint32_t capacity=*length;
    if ((uint8_t)wire==0u) {
        *length=0u;
        do {
            ++*length;
            if (capacity<*length) {
                if (s->errmsg==0) s->errmsg=pb_varint_overflow;
                return 0u;
            }
            if (!audio_pb_read_stream_48f3be(s,out,1u)) return 0u;
        } while ((*out++&128u)!=0u);
        return 1u;
    }
    if ((uint8_t)wire==1u) { *length=8u;return audio_pb_read_stream_48f3be(s,buffer,8u); }
    if ((uint8_t)wire==5u) { *length=4u;return audio_pb_read_stream_48f3be(s,buffer,4u); }
    if (s->errmsg==0) s->errmsg=pb_invalid_wire_type;
    return 0u;
}
