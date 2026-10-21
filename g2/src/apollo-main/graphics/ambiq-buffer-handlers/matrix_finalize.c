/* Apollo Nema 3x3 matrix inversion at 0x561b38..0x561c62. */
#include <stdint.h>

uint32_t audio_uart_nema_matrix_finalize_561b38(float *matrix) {
    const float a=matrix[0],b=matrix[1],c=matrix[2];
    const float d=matrix[3],e=matrix[4],f=matrix[5];
    const float g=matrix[6],h=matrix[7],i=matrix[8];
    const float q0=e*i-f*h;
    const float q3=f*g-d*i;
    const float q6=d*h-e*g;
    const float determinant=(q0*a+q3*b)+q6*c;
    if (!(__builtin_fabsf(determinant)>=0x1.4f8b5ap-17f))
        return 0xffffffffu;
    const float q1=c*h-b*i;
    const float q2=b*f-c*e;
    const float q4=a*i-c*g;
    const float q5=c*d-a*f;
    const float q7=b*g-a*h;
    const float q8=a*e-b*d;
    matrix[0]=q0;matrix[1]=q1;matrix[2]=q2;
    matrix[3]=q3;matrix[4]=q4;matrix[5]=q5;
    matrix[6]=q6;matrix[7]=q7;matrix[8]=q8;
    const float reciprocal=1.0f/determinant;
    for (uint32_t index=0;index<9u;++index) matrix[index]*=reciprocal;
    return 0u;
}
