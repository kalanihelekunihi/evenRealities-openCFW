/* SPDX-License-Identifier: MIT */
/* Recovered package 0x17d18. The five-byte OTP query uses a zeroed local. */
#include <stdint.h>
#include <stddef.h>
extern unsigned open_cfw_gx8002_clock_frequency(unsigned);
extern void *(* volatile open_cfw_gx8002_flash_otp_probe)(unsigned,unsigned,unsigned,unsigned);
extern int open_cfw_gx8002_flash_otp_read_api(const void *,unsigned,uint8_t *,unsigned);
extern int printf(const char *,...);
extern int strncmp(const char *,const char *,size_t);
extern const char open_cfw_gx8002_flash_otp_error[];
extern const char open_cfw_gx8002_flash_otp_signature[];
int open_cfw_gx8002_flash_otp_configuration(uint32_t *configuration)
{
    *configuration=0x8002;
    unsigned frequency=open_cfw_gx8002_clock_frequency(13);
    void *device=open_cfw_gx8002_flash_otp_probe(0,0,frequency>>1,2048);
    if (!device) return -1;
    uint8_t content[5]={0};
    if (open_cfw_gx8002_flash_otp_read_api(device,0,content,5)<0) {
        printf(open_cfw_gx8002_flash_otp_error);
        return -1;
    }
    /* Share the diagnostic address literal; the signature starts 22 bytes
     * later. Explicit target address formation avoids a second literal pool
     * cell crossing into the adjacent function. No firmware bytes embedded. */
    const char *signature;
    __asm__("lrw %0, open_cfw_gx8002_flash_otp_error\n\taddi %0, %0, 22"
            : "=r"(signature));
    if (!strncmp((const char *)content,signature,
                 5u /* recovered signature is exactly "8003A" */))
        *configuration=0x8003a;
    return 0;
}
