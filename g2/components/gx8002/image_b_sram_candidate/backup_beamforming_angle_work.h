#ifndef GX8002_IMAGE_B_BEAMFORMING_ANGLE_WORK_H
#define GX8002_IMAGE_B_BEAMFORMING_ANGLE_WORK_H

#include <stdint.h>

struct gx8002_image_b_angle_work {
    void *angle_vector;
    void *mic_vector_a;
    void *mic_vector_b;
    void *mic_vector_c;
    void *mic_angle_matrix;
    void *angle_vector_b;
    uint32_t mic_count;
    uint32_t angle_count;
    uint32_t mic_angle_count;
    float frame_ratio;
    float gain;
    float distance;
    float alpha;
    uint32_t state_word_0x18;
    uint32_t state_word_0x30;
};

struct gx8002_image_b_angle_geometry {
    float increment;
    float steering_radians;
};

#endif
