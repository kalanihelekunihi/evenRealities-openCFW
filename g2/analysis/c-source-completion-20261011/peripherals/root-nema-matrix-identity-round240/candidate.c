#include <stdint.h>
/* Native561810..561830: exact IEEE754 identity words, ordered32bit stores. */
void audio_uart_nema_matrix_identity_561810(void *cell) {
 volatile uint32_t *matrix=cell;
 matrix[0]=0x3f800000u;matrix[1]=0;matrix[2]=0;matrix[3]=0;
 matrix[4]=0x3f800000u;matrix[5]=0;matrix[6]=0;matrix[7]=0;matrix[8]=0x3f800000u;
}
