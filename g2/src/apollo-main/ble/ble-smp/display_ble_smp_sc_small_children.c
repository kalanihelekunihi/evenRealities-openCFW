/* Native 0x56cfdc/0x56d150/0x537c00, pinned Cordio SMP utilities. */
#include <stdint.h>
extern void Calc128Cpy(uint8_t *destination,uint8_t *source);
uint8_t *SmpScCat128(uint8_t *destination,uint8_t *source) {
    Calc128Cpy(destination,source);
    return destination+16u;
}
uint8_t smpGetPkBit(const uint8_t *ccb) {
    const uint8_t *sc=*(const uint8_t *const *)(const void *)(ccb+0x48u);
    const uint8_t *scratch=*(const uint8_t *const *)(const void *)(sc+0x14u);
    uint8_t position=sc[3u];
    uint8_t index=(uint8_t)(15u-(position>>3u));
    return (scratch[0x20u+index] & (uint8_t)(1u<<(position&7u))) ? 0x81u : 0x80u;
}
