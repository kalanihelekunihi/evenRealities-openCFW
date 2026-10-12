#include <assert.h>
#include <stdint.h>
uint32_t opencfw_em9305_callback_32922c(void),opencfw_em9305_callback_32a218(uint32_t),opencfw_em9305_callback_32ae3c(void);
static unsigned stage;
uint32_t opencfw_em9305_init_child_317498(void){assert(stage++==0);return 11;}
uint32_t opencfw_em9305_common_init_303008(uint32_t v){assert(stage++==0&&v==0xfeedbeef);return 22;}
uint32_t opencfw_em9305_init_child_31369c(uint32_t v){assert(stage++==1&&v==22);return 33;}
uint32_t opencfw_em9305_init_child_318ab8(uint32_t v){assert(stage++==2&&v==33);return 44;}
uint32_t opencfw_em9305_init_lower_30e42c(uint32_t v){assert(stage++==3&&v==44);return 55;}
uint32_t opencfw_em9305_common_init_302e90(void){assert(stage++==0);return 66;}
uint32_t opencfw_em9305_common_init_302ea4(void){assert(stage++==1);return 77;}
uint32_t opencfw_em9305_init_child_30a27c(void){assert(stage++==2);return 88;}
int main(void){stage=0;assert(opencfw_em9305_callback_32922c()==11&&stage==1);stage=0;assert(opencfw_em9305_callback_32a218(0xfeedbeef)==55&&stage==4);stage=0;assert(opencfw_em9305_callback_32ae3c()==88&&stage==3);return 0;}
