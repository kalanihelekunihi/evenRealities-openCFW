#include <assert.h>
#include <stdint.h>
#include "../../../../components/gx8002/image_b_sram_candidate/backup_beamforming_process_band.c"
static void run(uint32_t bits, uint32_t want_index, uint32_t want_bytes) {
    uint32_t ctx[0x54/4]={0};
    ctx[0x08/4]=3; ctx[0x34/4]=bits; ctx[0x4c/4]=7; ctx[0x50/4]=51;
    struct gx8002_image_b_process_band out;
    gx8002_image_b_process_band_verified_chunk(ctx,&out);
    assert(out.active_stages==3);
    assert(out.band_index==want_index);
    assert(out.coefficient_bytes==want_bytes);
    assert(out.mode_count==(want_bytes==28?7u:9u));
}
int main(void) {
    run(0x3c23d70au,59,36); /* exactly .01 */
    run(0x3c23d70bu,89,36); /* next float above .01 */
    run(0x3cf5c28fu,89,36); /* exactly .03 */
    run(0x3cf5c290u,49,36);
    run(0x3d75c28fu,49,36); /* exactly .06 */
    run(0x3d75c290u,29,36);
    run(0x3db851ecu,29,36); /* exactly .09 */
    run(0x3db851edu,29,36);
    run(0x7fc00000u,51,28); /* NaN follows native unordered path */
    return 0;
}
