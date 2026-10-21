/* Native nanopb extension-list encoder 0x490bf8. */
#include <stdint.h>
struct pb_extension_type_candidate {
    const void *descriptor;
    uint32_t (*encode)(void *stream,const void *extension);
    const void *field_descriptor; /* native type+8, used by 0x4d93a4 */
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
    void *field,*data,*size;
    const void *submessage_descriptor;
};
_Static_assert(sizeof(struct pb_field_iter_candidate)==40u,"native iterator size");
extern uint32_t audio_pb_encode_default_extension_490bc8(void *stream,const struct pb_extension_candidate *extension);
uint32_t audio_pb_encode_extension_490bf8(void *stream,const struct pb_field_iter_candidate *iter)
{
    const struct pb_extension_candidate *extension=*(const struct pb_extension_candidate *const *)iter->data;
    while (extension!=0) {
        uint32_t ok=extension->type->encode!=0
            ?extension->type->encode(stream,extension)
            :audio_pb_encode_default_extension_490bc8(stream,extension);
        if (!ok) return 0u;
        extension=extension->next;
    }
    return 1u;
}
