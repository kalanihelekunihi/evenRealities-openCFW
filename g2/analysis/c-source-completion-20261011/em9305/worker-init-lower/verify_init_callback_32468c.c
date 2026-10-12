#include <assert.h>
#include <stdint.h>
extern uint32_t opencfw_em9305_init_callback_32468c(uint32_t);
static unsigned called;
uintptr_t opencfw_em9305_wsf_queue_remove(uintptr_t queue)
{assert(queue==0x805194u);++called;return 0x12345678u;}
int main(void)
{
    for (unsigned n=0;n<256u;++n)
        assert(opencfw_em9305_init_callback_32468c(n)==0x12345678u);
    assert(called==256u);
    return 0;
}
