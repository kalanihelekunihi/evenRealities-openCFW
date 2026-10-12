/* Native secCmacGenSubkey1 0x53653a, pinned Cordio sec_cmac_hci.c. */
#include <stdint.h>
extern void SecLeEncryptCmd(const uint8_t *key,const uint8_t *plain,
                            void *queue,uint8_t handler); /* native 0x5363ae */
void secCmacGenSubkey1(void *queue) {
    const uint8_t *p=(const uint8_t *)queue;
    const uint8_t *callback=*(const uint8_t *const *)(const void *)(p+0x30u);
    uint8_t zero[16]={0};
    SecLeEncryptCmd(callback+4u,zero,queue,callback[0x28u]);
}
