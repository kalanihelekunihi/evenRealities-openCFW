/* Stock Main Cordio ATTS procedure table at initialized RAM 0x2000045c.
 * Row order follows pinned AmbiqSuite Cordio atts_main.c:98-118.
 * Handler bodies are separate C providers; the table stays relocatable.
 */
#include <stdint.h>
typedef void (*atts_proc)(void *,uint16_t,uint8_t *);
extern void attsProcMtuReq(void *,uint16_t,uint8_t *);
extern void attsProcFindInfoReq(void *,uint16_t,uint8_t *);
extern void attsProcFindTypeReq(void *,uint16_t,uint8_t *);
extern void attsProcReadTypeReq(void *,uint16_t,uint8_t *);
extern void attsProcReadReq(void *,uint16_t,uint8_t *);
extern void attsProcReadBlobReq(void *,uint16_t,uint8_t *);
extern void attsProcReadMultReq(void *,uint16_t,uint8_t *);
extern void attsProcReadGroupTypeReq(void *,uint16_t,uint8_t *);
extern void attsProcWrite(void *,uint16_t,uint8_t *);
extern void attsProcPrepWriteReq(void *,uint16_t,uint8_t *);
extern void attsProcExecWriteReq(void *,uint16_t,uint8_t *);
extern void attsProcValueCnf(void *,uint16_t,uint8_t *);
extern void attsProcReadMultiVarReq(void *,uint16_t,uint8_t *);

uint32_t audio_ble_atts_proc_table_2000045c[18]
    __attribute__((section(".g2_ram_2000045c"),used))={
    0u,
    (uint32_t)(uintptr_t)(atts_proc)attsProcMtuReq,
    (uint32_t)(uintptr_t)(atts_proc)attsProcFindInfoReq,
    (uint32_t)(uintptr_t)(atts_proc)attsProcFindTypeReq,
    (uint32_t)(uintptr_t)(atts_proc)attsProcReadTypeReq,
    (uint32_t)(uintptr_t)(atts_proc)attsProcReadReq,
    (uint32_t)(uintptr_t)(atts_proc)attsProcReadBlobReq,
    (uint32_t)(uintptr_t)(atts_proc)attsProcReadMultReq,
    (uint32_t)(uintptr_t)(atts_proc)attsProcReadGroupTypeReq,
    (uint32_t)(uintptr_t)(atts_proc)attsProcWrite,
    (uint32_t)(uintptr_t)(atts_proc)attsProcWrite,
    (uint32_t)(uintptr_t)(atts_proc)attsProcPrepWriteReq,
    (uint32_t)(uintptr_t)(atts_proc)attsProcExecWriteReq,
    0u,0u,
    (uint32_t)(uintptr_t)(atts_proc)attsProcValueCnf,
    (uint32_t)(uintptr_t)(atts_proc)attsProcReadMultiVarReq,
    0u
};
