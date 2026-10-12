/* Native DmSmpEncryptReq 0x55bbc4; pinned Cordio dm_sec_master.c. */
#include <stdint.h>
extern uint8_t *dmConnCcbById(uint8_t connection);
extern const uint8_t calc128Zeros[16]; /* authenticated zero RAND source */
extern void HciLeStartEncryptionCmd(uint16_t handle,const uint8_t *random,
                                     uint16_t ediv,const uint8_t *key);
void DmSmpEncryptReq(uint8_t connection,uint8_t security_level,const uint8_t *key)
{
    uint8_t *ccb=dmConnCcbById(connection);
    if (!ccb) return;
    ccb[0x18u]=security_level;
    ccb[0x12u]=0u;
    uint16_t handle=(uint16_t)ccb[0x0cu]|((uint16_t)ccb[0x0du]<<8u);
    HciLeStartEncryptionCmd(handle,calc128Zeros,0u,key);
}
