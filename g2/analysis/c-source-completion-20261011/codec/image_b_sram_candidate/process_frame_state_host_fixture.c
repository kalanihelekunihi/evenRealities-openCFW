#include <assert.h>
#include <stdint.h>
struct gx8002_image_b_process_frame_state {
    uint32_t band_byte_offset,coefficient_offset,coefficient_stride;
    uint32_t selected_offset,selected_stride,frame_index,frame_count;
};
extern int gx8002_image_b_process_frame_advance_verified_chunk(
    struct gx8002_image_b_process_frame_state *);
int main(void) {
    struct gx8002_image_b_process_frame_state s={
        .band_byte_offset=12,.coefficient_offset=100,
        .coefficient_stride=18,.selected_offset=200,
        .selected_stride=96,.frame_index=0,.frame_count=2};
    assert(gx8002_image_b_process_frame_advance_verified_chunk(&s)==1);
    assert(s.band_byte_offset==16 && s.coefficient_offset==118);
    assert(s.selected_offset==296 && s.frame_index==1);
    assert(gx8002_image_b_process_frame_advance_verified_chunk(&s)==0);
    assert(s.band_byte_offset==20 && s.coefficient_offset==136);
    assert(s.selected_offset==392 && s.frame_index==2);
    return 0;
}
