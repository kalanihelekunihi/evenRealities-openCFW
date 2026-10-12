#include <assert.h>
#include <stdint.h>
uint32_t opencfw_em9305_init_transition_random_317afc(void);
static uint32_t sample;
uint32_t opencfw_em9305_pal_random_step(void){return sample;}
int main(void)
{
    for(uint32_t v=0u;v<1024u;v++){
        sample=v;
        assert(opencfw_em9305_init_transition_random_317afc()==
            ((v&15u)+((v>>4u)&1u)));
    }
    sample=0xffffffffu;
    assert(opencfw_em9305_init_transition_random_317afc()==16u);
    return 0;
}
