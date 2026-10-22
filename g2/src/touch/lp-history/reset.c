/* Independent stock7e04..7e14. Clear tuner state, history gate and baseline
 * metadata; retain history, slot/count/frame fields and scan counter. */
#include "history.h"
/* Stock 0x00007E04 (touch_sub_4b04) */
void touch_lp_history_reset(uint8_t *c){uint8_t *common=*(uint8_t **)(c+4);*(uint16_t *)(common+2)=0;common[6]=0;*(uint16_t *)(common+22)=0;common[28]=0;}
