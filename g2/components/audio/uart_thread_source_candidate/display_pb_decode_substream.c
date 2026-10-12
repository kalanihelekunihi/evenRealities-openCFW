/* Native nanopb bounded substream begin/end 0x48f77e/0x48f7ca. */
#include <stdint.h>
struct pb_istream_candidate { uint32_t (*callback)(void *,void *,uint32_t);void *state;uint32_t bytes_left;const char *errmsg; };
_Static_assert(sizeof(struct pb_istream_candidate)==16u,"native stream size");
extern uint32_t audio_pb_read_varint_48f4b8(struct pb_istream_candidate *,uint32_t *,uint8_t *);
extern uint32_t audio_pb_read_stream_48f3be(struct pb_istream_candidate *,void *,uint32_t);
static const char pb_parent_short[]="parent stream too short"; /* ROM 0x779f64 */
uint32_t audio_pb_substream_begin_48f77e(struct pb_istream_candidate *parent,struct pb_istream_candidate *sub)
{
    uint32_t n;
    if (!audio_pb_read_varint_48f4b8(parent,&n,0)) return 0u;
    *sub=*parent;
    if (sub->bytes_left<n) {
        if (parent->errmsg==0) parent->errmsg=pb_parent_short;
        return 0u;
    }
    sub->bytes_left=n;
    parent->bytes_left-=n;
    return 1u;
}
uint32_t audio_pb_substream_end_48f7ca(struct pb_istream_candidate *parent,struct pb_istream_candidate *sub)
{
    if (sub->bytes_left!=0u && !audio_pb_read_stream_48f3be(sub,0,sub->bytes_left)) return 0u;
    parent->state=sub->state;
    parent->errmsg=sub->errmsg;
    return 1u;
}
