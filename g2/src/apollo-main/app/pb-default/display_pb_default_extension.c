/* Native nanopb default extension 0x490bc8 and iterator setup 0x4d93a4. */
#include <stdint.h>
struct pb_ostream_candidate {
    uint32_t (*callback)(void *,const uint8_t *,uint32_t);
    void *state; uint32_t max_size,bytes_written; const char *errmsg;
};
struct pb_msgdesc_candidate {
    const uint32_t *field_info; const void *submsg_info,*default_value,*field_callback;
    uint16_t field_count,required_field_count,largest_tag;
};
struct pb_extension_type_candidate {
    const void *descriptor;
    uint32_t (*encode)(void *,const void *);
    const struct pb_msgdesc_candidate *field_descriptor;
};
struct pb_extension_candidate {
    const struct pb_extension_type_candidate *type;
    void *dest;
    const struct pb_extension_candidate *next;
    uint32_t found;
};
struct pb_field_iter_candidate {
    const void *descriptor; void *message;
    uint16_t index,field_info_index,required_field_index,submessage_index;
    uint16_t tag,data_size,array_size; uint8_t type;
    void *field,*data,*size; const void *submessage_descriptor;
};
extern uint32_t audio_pb_iter_begin_4d94ba(struct pb_field_iter_candidate *,const void *,const void *);
extern uint32_t audio_pb_encode_field_490b1e(void *,struct pb_field_iter_candidate *);
static const char pb_invalid_extension[]="invalid extension"; /* 0x781868 via 0x4910cc */
uint32_t audio_pb_extension_iter_4d93a4(struct pb_field_iter_candidate *iter,const struct pb_extension_candidate *ext)
{
    const struct pb_msgdesc_candidate *desc=ext->type->field_descriptor;
    const void *message=(((desc->field_info[0]>>8)&0xc0u)==0x80u)
        ?(const void *)&ext->dest:ext->dest;
    uint32_t ok=audio_pb_iter_begin_4d94ba(iter,desc,message);
    iter->size=(void *)&ext->found;
    return ok;
}
uint32_t audio_pb_encode_default_extension_490bc8(struct pb_ostream_candidate *stream,const struct pb_extension_candidate *ext)
{
    struct pb_field_iter_candidate iter;
    if (!audio_pb_extension_iter_4d93a4(&iter,ext)) {
        if (stream->errmsg==0) stream->errmsg=pb_invalid_extension;
        return 0u;
    }
    return audio_pb_encode_field_490b1e(stream,&iter);
}
