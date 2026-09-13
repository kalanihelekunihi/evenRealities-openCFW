/* SPDX-License-Identifier: MIT */
/* Recovered backup package 0x4e014. The five-byte OTP query uses a zeroed local. */
#include <stdint.h>
#include <stddef.h>
extern unsigned open_cfw_gx8002_clock_frequency(unsigned);
extern void *(* volatile open_cfw_gx8002_flash_otp_probe)(unsigned,unsigned,unsigned,unsigned);
extern int open_cfw_gx8002_flash_otp_read_api(const void *,unsigned,uint8_t *,unsigned);
extern int printf(const char *,...);
extern size_t strlen(const char *);
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
    const char *signature=open_cfw_gx8002_flash_otp_signature;
    if (!strncmp((const char *)content,signature,strlen(signature)))
        *configuration=0x8003a;
    return 0;
}
