/* Apollo Nema matrix command upload at 0x5226e8..0x522846. */
#include <stdint.h>

extern void *audio_uart_nema_cl_get_space_514aec(uint32_t);

static uint32_t matrix_upload_bits(float value) {
    union {float f;uint32_t u;} bits={.f=value};
    return bits.u;
}

void audio_uart_nema_matrix_upload_5226e8(float *matrix) {
    const float epsilon=0x1.ad7f2ap-24f;
    const float negative_epsilon=-0x1.ad7f28p-24f;
    const float perspective_x=matrix[6];
    const float perspective_y=matrix[7];
    uint32_t affine=(perspective_x<epsilon &&
                     perspective_x>=negative_epsilon &&
                     perspective_y<epsilon &&
                     perspective_y>=negative_epsilon);
    if (affine) {
        const float shifted=perspective_x-1.0f;
        if (shifted>=epsilon) affine=0u;
        else if (shifted<negative_epsilon) {
            const float divisor=matrix[8];
            for (uint32_t i=0;i<6u;++i) matrix[i]/=divisor;
        }
    }
    uint32_t *const command=(uint32_t *)audio_uart_nema_cl_get_space_514aec(
        affine?6u:9u);
    if (command==0) return;
    command[0]=0x174u;command[1]=matrix_upload_bits(matrix[5]);
    command[2]=0x168u;command[3]=matrix_upload_bits(matrix[2]);
    uint32_t index=4u;
    if (!affine) {
        command[index++]=0x178u;command[index++]=matrix_upload_bits(matrix[6]);
        command[index++]=0x17cu;command[index++]=matrix_upload_bits(matrix[7]);
        command[index++]=0x180u;command[index++]=matrix_upload_bits(matrix[8]);
    }
    command[index++]=0x160u;command[index++]=matrix_upload_bits(matrix[0]);
    command[index++]=0x164u;command[index++]=matrix_upload_bits(matrix[1]);
    command[index++]=0x16cu;command[index++]=matrix_upload_bits(matrix[3]);
    command[index++]=0x170u;command[index++]=matrix_upload_bits(matrix[4]);
}
