/* Apollo Nema 3x3 perspective point at 0x561ad4..0x561b34. */
#include <stdint.h>

void audio_uart_nema_matrix_point_561ad4(const float *matrix,
                                          float *x_pointer,float *y_pointer) {
    const float x=*x_pointer;
    const float y=*y_pointer;
    const float divisor=(matrix[6]*x+matrix[7]*y)+matrix[8];
    const float transformed_x=(matrix[0]*x+matrix[1]*y)+matrix[2];
    *x_pointer=transformed_x/divisor;
    const float transformed_y=(matrix[3]*x+matrix[4]*y)+matrix[5];
    *y_pointer=transformed_y/divisor;
}
