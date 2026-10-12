/* Native GSC create temporary-buffer allocation 0x1000d0a0..0x1000d0ca
 * with failure policy at 0x1000d1e2. Its unsigned size arithmetic follows
 * source words frame/shift/stages, then the real native zero writer clears
 * the buffer. A null allocation logs the authenticated stock diagnostic.
 */
#include <stdint.h>

extern int gx8002_image_b_heap_log_10009934(const char *format, ...);
extern void gx8002_image_b_zero_100113c4(
    void *destination, uint32_t value, uint32_t bytes);

void *gx8002_image_b_create_temp_verified_chunk(
    const uint32_t *ctx, void *(*allocate)(uint32_t bytes))
{
    uint32_t stages=ctx[0x08/4];
    uint32_t shift=ctx[0x10/4];
    uint32_t frame=ctx[0x0c/4];
    uint32_t bytes=((stages+2u)*shift+frame-shift)*4u;
    void *temporary=allocate(bytes);
    if (temporary == 0) {
        (void)gx8002_image_b_heap_log_10009934(
            "[error], malloc wtmp failed, %s, %d\n",
            "lvp/vma/lavaliermic/gsc.c", 443);
        return 0;
    }
    gx8002_image_b_zero_100113c4(temporary,0u,bytes);
    return temporary;
}
