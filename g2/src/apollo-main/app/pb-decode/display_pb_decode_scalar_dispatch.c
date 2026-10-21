/* Native nanopb scalar/submessage field decoder 0x48f7f4. */
#include <stdint.h>
struct pb_istream_candidate { uint32_t (*callback)(void *,void *,uint32_t);void *state;uint32_t bytes_left;const char *errmsg; };
struct pb_field_iter_candidate { const void *descriptor;void *message;uint16_t index,field_info_index,required_field_index,submessage_index;uint16_t tag,data_size,array_size;uint8_t type;void *field,*data,*size;const void *submessage_descriptor; };
_Static_assert(sizeof(struct pb_field_iter_candidate)==40u,"native iterator size");
extern uint32_t audio_pb_decode_bool_4901cc(struct pb_istream_candidate *,struct pb_field_iter_candidate *);
extern uint32_t audio_pb_decode_varint_4901d6(struct pb_istream_candidate *,struct pb_field_iter_candidate *);
extern uint32_t audio_pb_decode_fixed32_490190(struct pb_istream_candidate *,void *);
extern uint32_t audio_pb_decode_fixed64_4901ac(struct pb_istream_candidate *,void *);
extern uint32_t audio_pb_decode_bytes_490358(struct pb_istream_candidate *,struct pb_field_iter_candidate *);
extern uint32_t audio_pb_decode_string_4903ea(struct pb_istream_candidate *,struct pb_field_iter_candidate *);
extern uint32_t audio_pb_decode_submessage_49048c(struct pb_istream_candidate *,struct pb_field_iter_candidate *);
extern uint32_t audio_pb_decode_extension_49053c(struct pb_istream_candidate *,struct pb_field_iter_candidate *);
static const char pb_wrong_wire_type[]="wrong wire type"; /* ROM 0x787ca0 */
static const char pb_invalid_field_type[]="invalid field type"; /* ROM 0x7817f0 */
static uint32_t wrong_wire(struct pb_istream_candidate *s) { if (!s->errmsg) s->errmsg=pb_wrong_wire_type; return 0u; }
uint32_t audio_pb_decode_scalar_48f7f4(struct pb_istream_candidate *s,uint32_t wire,struct pb_field_iter_candidate *iter)
{
    uint32_t type=iter->type&15u;
    uint8_t w=(uint8_t)wire;
    if (type==0u) {
        if (w!=0u && w!=255u) return wrong_wire(s);
        return audio_pb_decode_bool_4901cc(s,iter);
    }
    if (type>=1u && type<=3u) {
        if (w!=0u && w!=255u) return wrong_wire(s);
        return audio_pb_decode_varint_4901d6(s,iter);
    }
    if (type==4u) {
        if (w!=5u && w!=255u) return wrong_wire(s);
        return audio_pb_decode_fixed32_490190(s,iter->data);
    }
    if (type==5u) {
        if (w!=1u && w!=255u) return wrong_wire(s);
        return audio_pb_decode_fixed64_4901ac(s,iter->data);
    }
    if (type==6u) {
        if (w!=2u) return wrong_wire(s);
        return audio_pb_decode_bytes_490358(s,iter);
    }
    if (type==7u) {
        if (w!=2u) return wrong_wire(s);
        return audio_pb_decode_string_4903ea(s,iter);
    }
    if (type==8u || type==9u) {
        if (w!=2u) return wrong_wire(s);
        return audio_pb_decode_submessage_49048c(s,iter);
    }
    if (type==11u) {
        if (w!=2u) return wrong_wire(s);
        return audio_pb_decode_extension_49053c(s,iter);
    }
    if (!s->errmsg) s->errmsg=pb_invalid_field_type;
    return 0u;
}
