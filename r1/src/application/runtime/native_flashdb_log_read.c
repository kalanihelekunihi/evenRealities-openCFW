#include <stdint.h>
typedef struct __attribute__((packed,may_alias)) { uint32_t value; } r1_fdb_wire_word;
uint32_t r1_fdb_native_flash_read(const volatile uint8_t *,uint32_t,void *,uint32_t);
uint32_t r1_fdb_native_get_status(const volatile uint8_t *,uint32_t);
static uint32_t tsl_word(const volatile uint8_t *p)
{return ((const volatile r1_fdb_wire_word *)p)->value;}
static void tsl_put(volatile uint8_t *p,uint32_t value)
{((volatile r1_fdb_wire_word *)p)->value=value;}
/* Native 0x3f03e maps any negative partition result to read error 2.
 * Read the FILE_MODE byte before touching the partition pointer. */
extern int32_t r1_fdb_native_partition_read(void *,uint32_t,void *,uint32_t);
__attribute__((noinline,section(".text.r1_fdb_native_flash_read"),aligned(2)))
uint32_t r1_fdb_native_flash_read(const volatile uint8_t *db,uint32_t address,
                                 void *destination,uint32_t size)
{
    if(db[25])return 2;
    uint32_t partition=((const volatile r1_fdb_wire_word *)(db+8))->value;
    int32_t result=r1_fdb_native_partition_read((void *)(uintptr_t)partition,
                                               address,destination,size);
    return size>INT32_MAX || result!=(int32_t)size ? 2u:0u;
}
/* Native 0x3f076 scans byte zero of descending four-byte status slots.
 * The two shifts intentionally retain the native 32-bit offset truncation. */
uint32_t r1_fdb_native_get_status(const volatile uint8_t *status,uint32_t count)
{
    uint32_t last = count - 1u;
    uint32_t index = last, nonzero = 0;
    while (index != 0) {
        --index;
        uint32_t offset = (index << 5) >> 3;
        if (*(const volatile uint8_t *)((uintptr_t)status + offset) == 0) break;
        ++nonzero;
    }
    return last - nonzero;
}
/* Successful native record decoding, with defined scratch and error admission.
 * A failed/incomplete read leaves the caller's record untouched. */
uint32_t r1_fdb_native_read_tsl(const volatile uint8_t *db,volatile uint8_t *tsl)
{
 uint8_t scratch[32];
 for(uint32_t i=0;i<sizeof(scratch);i++)scratch[i]=UINT8_MAX;
 uint32_t address=tsl_word(tsl+12);
 uint32_t error=r1_fdb_native_flash_read(db,address,scratch,sizeof(scratch));
 if(error)return error;
 uint32_t status=(uint8_t)r1_fdb_native_get_status(scratch,6);
 tsl[0]=(uint8_t)status;
 if(status==0 || status==1){
  tsl_put(tsl+8,tsl_word(db+88));tsl_put(tsl+16,UINT32_MAX);tsl_put(tsl+4,0);
 }else{
  tsl_put(tsl+8,tsl_word(scratch+24));tsl_put(tsl+16,tsl_word(scratch+28));tsl_put(tsl+4,tsl_word(scratch+20));
 }
 return 0;
}
