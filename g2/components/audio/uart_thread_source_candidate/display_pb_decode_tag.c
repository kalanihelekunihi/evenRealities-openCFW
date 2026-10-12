/* Native nanopb input byte/varint/tag path, 0x48f454, 0x48f4b8, 0x48f66c.
 * Callback, stream, and native diagnostic effects are retained.
 */
#include <stdint.h>
struct pb_istream_candidate {
    uint32_t (*callback)(void *,void *,uint32_t);
    void *state;
    uint32_t bytes_left;
    const char *errmsg;
};
_Static_assert(sizeof(struct pb_istream_candidate)==16u,"native input stream size");
static const char pb_end_of_stream[]="end-of-stream"; /* ROM 0x787c70 */
static const char pb_io_error[]="io error"; /* ROM 0x78b690 */
static const char pb_varint_overflow[]="varint overflow"; /* ROM 0x787c80 */
static void pb_set_error(struct pb_istream_candidate *s,const char *error)
{ if (s->errmsg==0) s->errmsg=error; }

uint32_t audio_pb_read_byte_48f454(struct pb_istream_candidate *s,uint8_t *out)
{
    if (s->bytes_left==0u) { pb_set_error(s,pb_end_of_stream); return 0u; }
    if (!s->callback(s,out,1u)) { pb_set_error(s,pb_io_error); return 0u; }
    --s->bytes_left;
    return 1u;
}

uint32_t audio_pb_read_varint_48f4b8(struct pb_istream_candidate *s,uint32_t *out,uint8_t *eof)
{
    uint8_t byte;
    uint32_t result,shift;
    if (!audio_pb_read_byte_48f454(s,&byte)) {
        if (s->bytes_left==0u && eof!=0) *eof=1u;
        return 0u;
    }
    result=byte&127u;
    if ((byte&128u)!=0u) {
        shift=7u;
        do {
            if (!audio_pb_read_byte_48f454(s,&byte)) return 0u;
            if (shift<32u) {
                if (shift==28u) {
                    if ((byte&0x70u)!=0u && (byte&0x78u)!=0x78u) {
                        pb_set_error(s,pb_varint_overflow);return 0u;
                    }
                    result|=(uint32_t)byte<<28;
                } else result|=((uint32_t)byte&127u)<<shift;
            } else {
                uint8_t limit=shift<63u?255u:1u;
                if (shift>63u || !((byte&127u)==0u ||
                    ((int32_t)result<0 && byte==limit))) {
                    pb_set_error(s,pb_varint_overflow);return 0u;
                }
            }
            shift+=7u;
        } while ((byte&128u)!=0u);
    }
    *out=result;
    return 1u;
}

uint32_t audio_pb_read_tag_48f66c(struct pb_istream_candidate *s,uint8_t *wire_type,uint32_t *tag,uint8_t *eof)
{
    uint32_t raw;
    *eof=0u;*wire_type=0u;*tag=0u;
    if (!audio_pb_read_varint_48f4b8(s,&raw,eof)) return 0u;
    *tag=raw>>3;
    *wire_type=(uint8_t)(raw&7u);
    return 1u;
}
