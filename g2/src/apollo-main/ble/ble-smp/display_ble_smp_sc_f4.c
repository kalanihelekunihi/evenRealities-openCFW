/* Native SmpScCat 0x56cfc2 and SmpScCalcF4 0x56cf2c; pinned Cordio SC. */
#include <stdint.h>
extern void *memcpy(void *destination,const void *source,unsigned long length);
extern uint8_t *SmpScAlloc(uint8_t size, void *ccb, uint8_t *message);
extern void SmpScCmac(const uint8_t *key, uint8_t *text, uint8_t length,
                      void *ccb, uint8_t *message);
uint8_t *SmpScCat(uint8_t *destination,const uint8_t *source,uint8_t length) {
    memcpy(destination,source,length);
    return destination+length;
}
void SmpScCalcF4(void *ccb,uint8_t *message,const uint8_t *u,const uint8_t *v,
                 uint8_t z,const uint8_t *x) {
    uint8_t *text=SmpScAlloc(0x41u,ccb,message);
    if (text) {
        uint8_t *next=SmpScCat(text,u,0x20u);
        next=SmpScCat(next,v,0x20u);
        *next=z;
        SmpScCmac(x,text,0x41u,ccb,message);
    }
}
