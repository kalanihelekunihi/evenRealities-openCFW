#include <stdint.h>
extern void *audio_uart_nema_node_allocate_51416c(uint32_t);
extern void audio_uart_nema_vg_set_error_51565c(uint32_t);
extern void audio_uart_nema_matrix_identity_561810(void *);
/* Native514ebc..514f34: pre-check absolute store and sparse path initialization. */
void *audio_uart_nema_vg_path_create_514ebc(void) {
 void *cell=audio_uart_nema_node_allocate_51416c(136u);
 uint32_t address=(uint32_t)(uintptr_t)cell;
 *(volatile uint32_t *)(uintptr_t)(address+132u)=0;
 if(!cell){audio_uart_nema_vg_set_error_51565c(1u);return cell;}
 audio_uart_nema_matrix_identity_561810((void *)(uintptr_t)(address+96u));
 volatile uint32_t *path=cell;
 path[33]=0;path[2]=0;path[3]=0;path[0]=0;path[1]=0;
 path[4]=0x477fff00u;path[5]=0x477fff00u;path[6]=0xc77fff00u;path[7]=0xc77fff00u;
 path[20]=0;path[21]=0;path[9]=0;path[8]=0;path[11]=0;path[10]=0;
 path[13]=0;path[12]=0;path[15]=0;path[14]=0;path[22]=0;path[23]=0;
 path[16]=0x477fff00u;path[17]=0x477fff00u;path[18]=0xc77fff00u;path[19]=0xc77fff00u;
 return cell;
}
