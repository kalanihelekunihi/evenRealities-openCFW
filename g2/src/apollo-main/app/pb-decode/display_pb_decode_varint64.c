/* Native nanopb 64-bit varint, zigzag, and sized integer fields:
 * 0x48f5b8, 0x490150, 0x4901d6.
 */
#include <stdint.h>
struct pb_istream_candidate { uint32_t (*callback)(void *,void *,uint32_t);void *state;uint32_t bytes_left;const char *errmsg; };
struct pb_field_iter_candidate { const void *descriptor;void *message;uint16_t index,field_info_index,required_field_index,submessage_index;uint16_t tag,data_size,array_size;uint8_t type;void *field,*data,*size;const void *submessage_descriptor; };
_Static_assert(sizeof(struct pb_field_iter_candidate)==40u,"native iterator size");
extern uint32_t audio_pb_read_byte_48f454(struct pb_istream_candidate *,uint8_t *);
static const char pb_varint_overflow[]="varint overflow"; /* ROM 0x787c80 */
static const char pb_invalid_data_size[]="invalid data_size"; /* ROM 0x78182c */
static const char pb_integer_too_large[]="integer too large"; /* ROM 0x781840 */
static void set_error(struct pb_istream_candidate *s,const char *p) { if (s->errmsg==0) s->errmsg=p; }

uint32_t audio_pb_read_varint64_48f5b8(struct pb_istream_candidate *s,uint64_t *out)
{
    uint64_t result=0u;
    uint32_t shift=0u;
    uint8_t byte;
    for (;;) {
        if (!audio_pb_read_byte_48f454(s,&byte)) return 0u;
        if (shift>62u && (byte&0xfeu)!=0u) {
            set_error(s,pb_varint_overflow);return 0u;
        }
        result|=((uint64_t)(byte&127u))<<shift;
        shift+=7u;
        if ((byte&128u)==0u) { *out=result;return 1u; }
    }
}

uint32_t audio_pb_read_zigzag64_490150(struct pb_istream_candidate *s,int64_t *out)
{
    uint64_t encoded;
    if (!audio_pb_read_varint64_48f5b8(s,&encoded)) return 0u;
    *out=(int64_t)((encoded>>1)^((uint64_t)0-(encoded&1u)));
    return 1u;
}

uint32_t audio_pb_decode_varint_4901d6(struct pb_istream_candidate *s,struct pb_field_iter_candidate *it)
{
    uint64_t value,stored;
    int64_t signed_value;
    uint16_t size=it->data_size;
    if ((it->type&15u)==3u) {
        if (!audio_pb_read_zigzag64_490150(s,&signed_value)) return 0u;
        value=(uint64_t)signed_value;
    } else {
        if (!audio_pb_read_varint64_48f5b8(s,&value)) return 0u;
        if ((it->type&15u)!=2u && size!=8u)
            value=(uint64_t)(int64_t)(int32_t)value;
    }
    if (size==8u) { *(uint64_t *)it->data=value; stored=*(uint64_t *)it->data; }
    else if (size==4u) {
        *(uint32_t *)it->data=(uint32_t)value;
        stored=((it->type&15u)==2u)?*(uint32_t *)it->data:(uint64_t)(int64_t)*(int32_t *)it->data;
    } else if (size==2u) {
        *(uint16_t *)it->data=(uint16_t)value;
        stored=((it->type&15u)==2u)?*(uint16_t *)it->data:(uint64_t)(int64_t)*(int16_t *)it->data;
    } else if (size==1u) {
        *(uint8_t *)it->data=(uint8_t)value;
        stored=((it->type&15u)==2u)?*(uint8_t *)it->data:(uint64_t)(int64_t)*(int8_t *)it->data;
    } else {
        set_error(s,pb_invalid_data_size);return 0u;
    }
    if (stored==value) return 1u;
    set_error(s,pb_integer_too_large);
    return 0u;
}
