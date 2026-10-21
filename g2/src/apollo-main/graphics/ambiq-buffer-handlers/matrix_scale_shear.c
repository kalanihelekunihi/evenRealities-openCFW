/* Apollo Nema 3x3 scale and shear at 0x5618b8..0x561962. */
#include <stdint.h>

void audio_uart_nema_matrix_scale_5618b8(float x,float y,float *matrix)
    __attribute__((pcs("aapcs-vfp")));
void audio_uart_nema_matrix_shear_561902(float x,float y,float *matrix)
    __attribute__((pcs("aapcs-vfp")));

void audio_uart_nema_matrix_scale_5618b8(float x,float y,float *matrix) {
    matrix[0]*=x;matrix[1]*=x;matrix[2]*=x;
    matrix[3]*=y;matrix[4]*=y;matrix[5]*=y;
}

void audio_uart_nema_matrix_shear_561902(float x,float y,float *matrix) {
    const float a=matrix[0],b=matrix[1],c=matrix[2];
    const float d=matrix[3],e=matrix[4],f=matrix[5];
    matrix[0]=a+d*x;matrix[1]=b+e*x;matrix[2]=c+f*x;
    matrix[3]=d+a*y;matrix[4]=e+b*y;matrix[5]=f+c*y;
}
