/* Apollo Nema 3x3 matrix rotation at 0x561964..0x5619f0. */
#include <stdint.h>

extern float audio_uart_nema_cos_524130(float)
    __attribute__((pcs("aapcs-vfp")));
extern float audio_uart_nema_sin_52405c(float)
    __attribute__((pcs("aapcs-vfp")));
void audio_uart_nema_matrix_rotate_561964(float angle,float *matrix)
    __attribute__((pcs("aapcs-vfp")));

void audio_uart_nema_matrix_rotate_561964(float angle,float *matrix) {
    const float cosine=audio_uart_nema_cos_524130(angle);
    const float sine=audio_uart_nema_sin_52405c(angle);
    const float a=matrix[0],b=matrix[1],c=matrix[2];
    const float d=matrix[3],e=matrix[4],f=matrix[5];
    matrix[0]=cosine*a-sine*d;
    matrix[1]=cosine*b-sine*e;
    matrix[2]=cosine*c-sine*f;
    matrix[3]=sine*a+cosine*d;
    matrix[4]=sine*b+cosine*e;
    matrix[5]=sine*c+cosine*f;
}
