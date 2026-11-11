/* R1 0x3f05a: C policy around the four-word FAL seam.
 * The public SDK sync parameter remains unused in this FAL-only product. */
#ifndef R1_NATIVE_FLASH_WRITE_H
#define R1_NATIVE_FLASH_WRITE_H
#include <stddef.h>
_Static_assert(offsetof(struct fdb_db,file_mode)==25 &&
 offsetof(struct fdb_db,storage.part)==8 && sizeof(size_t)==4 &&
 FDB_READ_ERR==2 && FDB_WRITE_ERR==3,"native flash-write layout/status");
__attribute__((noinline,section(".text.r1_fdb_flash_write"),aligned(2)))
fdb_err_t _fdb_flash_write(fdb_db_t db,uint32_t address,const void *buffer,
                          size_t size,bool sync __attribute__((unused)))
{
 uint32_t flag=((const volatile struct fdb_db *)db)->file_mode;
 if(flag)return FDB_READ_ERR;
 const struct fal_partition *partition=((const volatile struct fdb_db *)db)->storage.part;
 int result=fal_partition_write(partition,address,(uint8_t *)buffer,size);
 return result<0?FDB_WRITE_ERR:FDB_NO_ERR;
}

#endif
