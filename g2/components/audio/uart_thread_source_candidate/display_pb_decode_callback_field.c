/* Native nanopb callback-storage field decoder 0x48fb30. */
#include <stdint.h>
struct pb_istream_candidate { uint32_t (*callback)(void *,void *,uint32_t);void *state;uint32_t bytes_left;const char *errmsg; };
struct pb_msgdesc_candidate { const uint32_t *field_info;const struct pb_msgdesc_candidate *const *submsg_info;const uint8_t *default_value;uint32_t (*field_callback)(struct pb_istream_candidate *,void *,void *);uint16_t field_count,required_field_count,largest_tag; };
struct pb_field_iter_candidate { const struct pb_msgdesc_candidate *descriptor;void *message;uint16_t index,field_info_index,required_field_index,submessage_index;uint16_t tag,data_size,array_size;uint8_t type;void *field,*data,*size;const struct pb_msgdesc_candidate *submessage_descriptor; };
_Static_assert(sizeof(struct pb_field_iter_candidate)==40u,"native iterator size");
extern uint32_t audio_pb_skip_wire_48f6a0(struct pb_istream_candidate *,uint32_t);
extern uint32_t audio_pb_substream_begin_48f77e(struct pb_istream_candidate *,struct pb_istream_candidate *);
extern uint32_t audio_pb_substream_end_48f7ca(struct pb_istream_candidate *,struct pb_istream_candidate *);
extern uint32_t audio_pb_callback_payload_48f6ea(struct pb_istream_candidate *,uint32_t,void *,uint32_t *);
extern void audio_uart_pb_stream_init(struct pb_istream_candidate *,const void *,uint32_t);
static const char pb_callback_failed[]="callback failed"; /* ROM 0x787cc0 */

uint32_t audio_pb_decode_callback_field_48fb30(struct pb_istream_candidate *s,uint32_t wire,struct pb_field_iter_candidate *it)
{
    uint32_t (*callback)(struct pb_istream_candidate *,void *,void *)=it->descriptor->field_callback;
    if (callback==0) return audio_pb_skip_wire_48f6a0(s,(uint8_t)wire);
    if ((uint8_t)wire==2u) {
        struct pb_istream_candidate sub;
        if (!audio_pb_substream_begin_48f77e(s,&sub)) return 0u;
        for (;;) {
            uint32_t before=sub.bytes_left;
            if (!callback(&sub,0,it)) {
                if (s->errmsg==0) s->errmsg=sub.errmsg!=0?sub.errmsg:pb_callback_failed;
                return 0u;
            }
            if (sub.bytes_left==0u || sub.bytes_left>=before) break;
        }
        return audio_pb_substream_end_48f7ca(s,&sub);
    }
    {
        uint32_t len=10u;
        uint8_t payload[12];
        struct pb_istream_candidate copy;
        if (!audio_pb_callback_payload_48f6ea(s,(uint8_t)wire,payload,&len)) return 0u;
        audio_uart_pb_stream_init(&copy,payload,len);
        return callback(&copy,0,it);
    }
}
