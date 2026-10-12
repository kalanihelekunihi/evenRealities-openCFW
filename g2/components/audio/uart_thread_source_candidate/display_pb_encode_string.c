/* Native nanopb NUL-terminated string provider 0x490fe4. */
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
extern uint32_t audio_pb_write_length_delimited_490db6(struct pb_ostream_candidate *,const void *,uint32_t);
static const char pb_zero_length_string[]="zero-length string"; /* 0x7818b8 */
static const char pb_unterminated_string[]="unterminated string"; /* 0x7818cc */
uint32_t audio_pb_encode_string_490fe4(struct pb_ostream_candidate *stream,const struct pb_field_iter_candidate *iter)
{
    const char *str=(const char *)iter->data;
    uint32_t limit,length=0u;
    if ((iter->type&0xc0u)==0x80u) limit=0xffffffffu;
    else {
        if (iter->data_size==0u) {
            if (stream->errmsg==0) stream->errmsg=pb_zero_length_string;
            return 0u;
        }
        limit=(uint32_t)iter->data_size-1u;
    }
    if (str!=0) {
        while (length<limit && str[length]!=0) length++;
        if (str[length]!=0) {
            if (stream->errmsg==0) stream->errmsg=pb_unterminated_string;
            return 0u;
        }
    }
    return audio_pb_write_length_delimited_490db6(stream,str,length);
}
