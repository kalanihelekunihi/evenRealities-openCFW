/* Native nanopb repeated-field encoder 0x490690, including packed count pass. */
#include <stdint.h>
struct pb_ostream_candidate {
    uint32_t (*callback)(void *,const uint8_t *,uint32_t);
    void *state; uint32_t max_size,bytes_written; const char *errmsg;
};
struct pb_field_iter_candidate {
    const void *descriptor; void *message;
    uint16_t index,field_info_index,required_field_index,submessage_index;
    uint16_t tag,data_size,array_size; uint8_t type;
    void *field,*data,*size; const void *submessage_descriptor;
};
extern uint32_t audio_pb_encode_key_490d4a(struct pb_ostream_candidate *,uint32_t,uint32_t);
extern uint32_t audio_pb_encode_int_490eae(struct pb_ostream_candidate *,const struct pb_field_iter_candidate *);
extern uint32_t audio_pb_encode_fixed_490f72(struct pb_ostream_candidate *,const struct pb_field_iter_candidate *);
extern uint32_t audio_pb_encode_single_490a46(struct pb_ostream_candidate *,const struct pb_field_iter_candidate *);
extern uint32_t audio_pb_encode_tag_490d66(struct pb_ostream_candidate *,const struct pb_field_iter_candidate *);
extern uint32_t audio_pb_write_varint_490ce0(struct pb_ostream_candidate *,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_pb_stream_write_490616(struct pb_ostream_candidate *,const void *,uint32_t);
static const char pb_array_max_size_exceeded[]="array max size exceeded"; /* 0x779fac */
static const char pb_none_error[]="(none)"; /* 0x78de7c */
uint32_t audio_pb_encode_repeated_490690(struct pb_ostream_candidate *stream,const struct pb_field_iter_candidate *arg)
{
    struct pb_field_iter_candidate *iter=(struct pb_field_iter_candidate *)arg;
    uint16_t count=*(const uint16_t *)iter->size;
    uint32_t type=(uint32_t)iter->type;
    uint32_t low=type&15u;
    if (count==0u) return 1u;
    if ((type&0xc0u)!=0x80u && count>iter->array_size) {
        if (stream->errmsg==0) stream->errmsg=pb_array_max_size_exceeded;
        return 0u;
    }
    if (low<6u) {
        uint32_t payload_size;
        if (!audio_pb_encode_key_490d4a(stream,2u,iter->tag)) return 0u;
        if (low==4u) payload_size=(uint32_t)count*4u;
        else if (low==5u) payload_size=(uint32_t)count*8u;
        else {
            struct pb_ostream_candidate counter={0};
            void *original=iter->data;
            for (uint16_t i=0u;i<count;i++) {
                if (!audio_pb_encode_int_490eae(&counter,iter)) {
                    if (stream->errmsg==0)
                        stream->errmsg=counter.errmsg!=0?counter.errmsg:pb_none_error;
                    return 0u;
                }
                iter->data=(uint8_t *)iter->data+iter->data_size;
            }
            iter->data=original;
            payload_size=counter.bytes_written;
        }
        if (!audio_pb_write_varint_490ce0(stream,0u,payload_size,0u)) return 0u;
        if (stream->callback==0) return audio_pb_stream_write_490616(stream,0,payload_size);
        for (uint16_t i=0u;i<count;i++) {
            uint32_t ok=(low==4u || low==5u)
                ?audio_pb_encode_fixed_490f72(stream,iter)
                :audio_pb_encode_int_490eae(stream,iter);
            if (!ok) return 0u;
            iter->data=(uint8_t *)iter->data+iter->data_size;
        }
        return 1u;
    }
    for (uint16_t i=0u;i<count;i++) {
        uint32_t ok;
        if ((type&0xc0u)==0x80u && (low==6u || low==7u)) {
            void *saved=iter->data;
            iter->data=*(void **)saved;
            if (iter->data==0) {
                ok=audio_pb_encode_tag_490d66(stream,iter);
                if (ok) ok=audio_pb_write_varint_490ce0(stream,0u,0u,0u);
            } else ok=audio_pb_encode_single_490a46(stream,iter);
            iter->data=saved;
        } else ok=audio_pb_encode_single_490a46(stream,iter);
        if (!ok) return 0u;
        iter->data=(uint8_t *)iter->data+iter->data_size;
    }
    return 1u;
}
