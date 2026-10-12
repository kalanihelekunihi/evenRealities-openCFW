#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_init_callback_31ae84(uintptr_t);
int main(void)
{
    uint8_t *root=mmap((void *)0x805000u,8192u,PROT_READ|PROT_WRITE,
                       MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *config=mmap((void *)0x806000u,4096u,PROT_READ|PROT_WRITE,
                         MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *incoming=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                           MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(root!=(void *)-1&&config!=(void *)-1&&incoming!=(void *)-1);
    incoming[1]=0x5au;
    for (unsigned count=0;count<=64u;++count) {
        memset(root+0x184u,0,64u*12u);
        for (unsigned n=0;n<64u;++n) {
            uint8_t *record=root+0x184u+12u*n;
            record[0]=(n%3u)==0u?0u:1u;
            record[1]=(n%2u)==0u?0x5au:0x33u;
        }
        *(uint32_t *)(root+0xcacu)=0x806000u;
        config[13u]=(uint8_t)count;
        assert(opencfw_em9305_init_callback_31ae84((uintptr_t)incoming)==0x810000u);
        for (unsigned n=0;n<64u;++n) {
            const uint8_t *record=root+0x184u+12u*n;
            if (n<count && (n%3u)!=0u && (n%2u)==0u)
                assert(record[0]==0u&&record[1]==0u);
            else {
                assert(record[0]==((n%3u)==0u?0u:1u));
                assert(record[1]==((n%2u)==0u?0x5au:0x33u));
            }
        }
    }
    return 0;
}
