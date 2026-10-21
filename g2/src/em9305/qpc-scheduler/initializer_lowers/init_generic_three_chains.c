#include <stdint.h>
extern uint32_t opencfw_em9305_init_child_317498(void);
extern uint32_t opencfw_em9305_common_init_303008(uint32_t);
extern uint32_t opencfw_em9305_init_child_31369c(uint32_t);
extern uint32_t opencfw_em9305_init_child_318ab8(uint32_t);
extern uint32_t opencfw_em9305_init_lower_30e42c(uint32_t);
extern uint32_t opencfw_em9305_common_init_302e90(void);
extern uint32_t opencfw_em9305_common_init_302ea4(void);
extern uint32_t opencfw_em9305_init_child_30a27c(void);
/* Full native32922c is a tail branch to full317498. */
uint32_t opencfw_em9305_callback_32922c(void){return opencfw_em9305_init_child_317498();}
/* Full native32a218..32a22c; four BL calls pass each returned R0. */
uint32_t opencfw_em9305_callback_32a218(uint32_t incoming){
 uint32_t value=opencfw_em9305_common_init_303008(incoming);
 value=opencfw_em9305_init_child_31369c(value);
 value=opencfw_em9305_init_child_318ab8(value);
 return opencfw_em9305_init_lower_30e42c(value);
}
/* Full native32ae3c..32ae4c; selected first two registrations replaceR0. */
uint32_t opencfw_em9305_callback_32ae3c(void){
 (void)opencfw_em9305_common_init_302e90();
 (void)opencfw_em9305_common_init_302ea4();
 return opencfw_em9305_init_child_30a27c();
}
