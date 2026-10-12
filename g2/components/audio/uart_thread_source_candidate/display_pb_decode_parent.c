/* Native nanopb message decoder 0x48fe98. Full field/unknown/required path.
 * The extension-list decoder remains an authentic typed child import.
 */
#include <stdint.h>
struct pb_istream_candidate { uint32_t (*callback)(void *,void *,uint32_t);void *state;uint32_t bytes_left;const char *errmsg; };
struct pb_msgdesc_candidate { const uint32_t *field_info;const struct pb_msgdesc_candidate *const *submsg_info;const uint8_t *default_value;void *field_callback;uint16_t field_count,required_field_count,largest_tag; };
struct pb_field_iter_candidate { const struct pb_msgdesc_candidate *descriptor;void *message;uint16_t index,field_info_index,required_field_index,submessage_index;uint16_t tag,data_size,array_size;uint8_t type;void *field,*data,*size;const struct pb_msgdesc_candidate *submessage_descriptor; };
_Static_assert(sizeof(struct pb_field_iter_candidate)==40u,"native iterator size");
extern uint32_t audio_pb_iter_begin_4d94ba(struct pb_field_iter_candidate *,const void *,const void *);
extern uint32_t audio_pb_default_fields_48fdf2(struct pb_field_iter_candidate *);
extern uint32_t audio_pb_read_tag_48f66c(struct pb_istream_candidate *,uint8_t *,uint32_t *,uint8_t *);
extern uint32_t audio_pb_iter_find_tag_4d93f8(struct pb_field_iter_candidate *,uint32_t);
extern uint32_t audio_pb_iter_find_extension_4d946e(struct pb_field_iter_candidate *);
extern uint32_t audio_pb_decode_field_48fbe4(struct pb_istream_candidate *,uint32_t,struct pb_field_iter_candidate *);
extern uint32_t audio_pb_decode_extension_unknown_48fc88(struct pb_istream_candidate *,uint32_t,uint32_t,void *);
extern uint32_t audio_pb_skip_wire_48f6a0(struct pb_istream_candidate *,uint32_t);
static const char pb_failed_defaults[]="failed to set defaults"; /* ROM 0x779f7c */
static const char pb_zero_tag[]="zero tag"; /* ROM 0x78b69c */
static const char pb_wrong_fixed_count[]="wrong size for fixed count field"; /* ROM 0x757668 */
static const char pb_missing_required[]="missing required field"; /* ROM 0x779f94 */
static void set_error(struct pb_istream_candidate *s,const char *p) { if (s->errmsg==0) s->errmsg=p; }

uint32_t audio_pb_decode_parent_48fe98(struct pb_istream_candidate *s,const struct pb_msgdesc_candidate *desc,void *message,uint32_t flags)
{
    uint32_t required_mask[2]={0u,0u};
    struct pb_field_iter_candidate it;
    uint32_t extension_threshold=0u;
    void *extension_head=0;
    int32_t fixed_index=-1;
    uint16_t fixed_count=0u,expected_count=0u;
    uint8_t wire=0u,eof=0u;
    uint32_t tag=0u;
    uint32_t init=audio_pb_iter_begin_4d94ba(&it,desc,message);
    if (init!=0u && (flags&1u)==0u && !audio_pb_default_fields_48fdf2(&it)) {
        set_error(s,pb_failed_defaults);
        return 0u;
    }
    for (;;) {
        if (s->bytes_left==0u) break;
        if (!audio_pb_read_tag_48f66c(s,&wire,&tag,&eof)) {
            if (eof==0u) return 0u;
            break;
        }
        if (tag==0u) {
            if ((flags&4u)!=0u) break;
            set_error(s,pb_zero_tag);
            return 0u;
        }
        if (audio_pb_iter_find_tag_4d93f8(&it,tag) && (it.type&15u)!=10u) {
            if ((it.type&0x30u)==0x20u && it.size==&it.array_size) {
                if (fixed_index!=(int32_t)it.index) {
                    if (fixed_index!=-1 && fixed_count!=expected_count) {
                        set_error(s,pb_wrong_fixed_count);
                        return 0u;
                    }
                    fixed_count=0u;
                    expected_count=it.array_size;
                    fixed_index=it.index;
                }
                it.size=&fixed_count;
            }
            if ((it.type&0x30u)==0u && it.required_field_index<64u)
                required_mask[it.required_field_index>>5]|=1u<<(it.required_field_index&31u);
            if (!audio_pb_decode_field_48fbe4(s,wire,&it)) return 0u;
            continue;
        }
        if (extension_threshold==0u) {
            if (audio_pb_iter_find_extension_4d946e(&it)) {
                extension_head=*(void **)it.data;
                extension_threshold=it.tag;
            }
            if (extension_head==0) extension_threshold=UINT32_MAX;
        }
        if (extension_threshold<=tag) {
            uint32_t before=s->bytes_left;
            if (!audio_pb_decode_extension_unknown_48fc88(s,tag,wire,extension_head)) return 0u;
            if (before!=s->bytes_left) continue;
        }
        if (!audio_pb_skip_wire_48f6a0(s,wire)) return 0u;
    }
    if (fixed_index!=-1 && fixed_count!=expected_count) {
        set_error(s,pb_wrong_fixed_count);
        return 0u;
    }
    {
        uint32_t required=it.descriptor->required_field_count;
        if (required>64u) required=64u;
        for (uint32_t i=0;i<(required>>5);++i) {
            if (required_mask[i]!=UINT32_MAX) { set_error(s,pb_missing_required);return 0u; }
        }
        if ((required&31u)!=0u && required_mask[required>>5]!=(UINT32_MAX>>(32u-(required&31u)))) {
            set_error(s,pb_missing_required);return 0u;
        }
    }
    return 1u;
}
