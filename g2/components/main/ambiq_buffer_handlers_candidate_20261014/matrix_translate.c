/* Apollo Nema 3x3 matrix translation at 0x561856..0x5618b6. */
#include <stdint.h>

void audio_uart_nema_matrix_translate_561856(float x,float y,float *matrix)
    __attribute__((pcs("aapcs-vfp")));
void audio_uart_nema_matrix_translate_561856(float x,float y,float *matrix) {
    matrix[0]+=x*matrix[6];
    matrix[1]+=x*matrix[7];
    matrix[2]+=x*matrix[8];
    matrix[3]+=y*matrix[6];
    matrix[4]+=y*matrix[7];
    matrix[5]+=y*matrix[8];
}
