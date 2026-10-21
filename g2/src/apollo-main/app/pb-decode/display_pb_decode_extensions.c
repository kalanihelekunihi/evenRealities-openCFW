/* Native nanopb extension-list decoder 0x48fc88 and default extension
 * handler 0x48fc26. Extension type callbacks are genuine source pointers.
 */
#include <stdint.h>
struct pb_istream_candidate { uint32_t (*callback)(void *,void *,uint32_t);void *state;uint32_t bytes_left;const char *errmsg; };
struct pb_field_iter_candidate { const void *descriptor;void *message;uint16_t index,field_info_index,required_field_index,submessage_index;uint16_t tag,data_size,array_size;uint8_t type;void *field,*data,*size;const void *submessage_descriptor; };
struct pb_extension_candidate;
struct pb_extension_type_candidate { uint32_t (*decode)(struct pb_istream_candidate *,struct pb_extension_candidate *,uint32_t,uint32_t);void *encode;const void *field_descriptor; };
struct pb_extension_candidate { const struct pb_extension_type_candidate *type;void *dest;struct pb_extension_candidate *next;uint32_t found; };
_Static_assert(sizeof(struct pb_field_iter_candidate)==40u,"native iterator size");
extern uint32_t audio_pb_extension_iter_4d93a4(struct pb_field_iter_candidate *,const struct pb_extension_candidate *);
extern uint32_t audio_pb_decode_field_48fbe4(struct pb_istream_candidate *,uint32_t,struct pb_field_iter_candidate *);
static const char pb_invalid_extension[]="invalid extension"; /* ROM 0x781818 */

uint32_t audio_pb_decode_default_extension_48fc26(struct pb_istream_candidate *s,struct pb_extension_candidate *ext,uint32_t tag,uint32_t wire)
{
    struct pb_field_iter_candidate it;
    if (!audio_pb_extension_iter_4d93a4(&it,ext)) {
        if (s->errmsg==0) s->errmsg=pb_invalid_extension;
        return 0u;
    }
    if (it.tag==tag && it.message!=0) {
        *(uint8_t *)&ext->found=1u;
        return audio_pb_decode_field_48fbe4(s,(uint8_t)wire,&it);
    }
    return 1u;
}
uint32_t audio_pb_decode_extension_unknown_48fc88(struct pb_istream_candidate *s,uint32_t tag,uint32_t wire,struct pb_extension_candidate *ext)
{
    uint32_t before=s->bytes_left;
    while (ext!=0 && before==s->bytes_left) {
        uint32_t ok=ext->type->decode!=0
            ?ext->type->decode(s,ext,tag,(uint8_t)wire)
            :audio_pb_decode_default_extension_48fc26(s,ext,tag,(uint8_t)wire);
        if (!ok) return 0u;
        ext=ext->next;
    }
    return 1u;
}
