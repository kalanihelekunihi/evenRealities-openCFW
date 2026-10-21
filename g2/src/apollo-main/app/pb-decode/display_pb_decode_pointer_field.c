/* Native nanopb pointer-field failure 0x48fb1c in this no-malloc build. */
#include <stdint.h>
struct pb_istream_candidate {
    uint32_t (*callback)(void *,void *,uint32_t);
    void *state;uint32_t bytes_left;const char *errmsg;
};
static const char pb_no_malloc_support[]="no malloc support"; /* ROM 0x781804 */
uint32_t audio_pb_decode_pointer_field_48fb1c(struct pb_istream_candidate *s,uint32_t wire,const void *iter)
{
    (void)wire;(void)iter;
    if (s->errmsg==0) s->errmsg=pb_no_malloc_support;
    return 0u;
}
