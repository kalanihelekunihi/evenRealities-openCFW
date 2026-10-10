#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdio.h>
#include <time.h>
#include "fdb_low_lvl.h"
volatile uint32_t read_address, read_count;
bool find_kv(fdb_kvdb_t d,const char*k,fdb_kv_t v){for(unsigned i=0;i<sizeof(*v);i++)((volatile unsigned char*)v)[i]=0xa7;v->value_len=8;v->addr.value=0xabc400;__asm volatile("movw r1,#0\nmovt r1,#0x2002" ::: "r1");return true;}
fdb_err_t _fdb_flash_read(fdb_db_t d,uint32_t a,void*b,size_t n){read_address=a;read_count=n;return FDB_READ_ERR;}
fdb_err_t _fdb_flash_write(fdb_db_t d,uint32_t a,const void*b,size_t n,bool sync){return FDB_NO_ERR;}
fdb_err_t _fdb_write_status(fdb_db_t d,uint32_t a,uint8_t*t,size_t n,size_t i,bool sync){return FDB_NO_ERR;}
void diagnostic(void){__asm volatile("bkpt #0");}
