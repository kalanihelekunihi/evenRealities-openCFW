/* SPDX-License-Identifier: MIT */
/* Named target layout recovered against NationalChip GX_FLASH_DEV.
 * Uses reconstructed implementation types, not a drop-in SDK API. */
#ifndef OPEN_CFW_GX8002_FLASH_INTERFACE_TABLE_H
#define OPEN_CFW_GX8002_FLASH_INTERFACE_TABLE_H
#include <stdint.h>
#include <stddef.h>
extern void *open_cfw_gx8002_flash_interface_initialize(void);
extern int open_cfw_gx8002_flash_read(unsigned address,void *buffer,unsigned length);
extern int open_cfw_gx8002_flash_chip_erase(void);
extern int open_cfw_gx8002_flash_erase(unsigned address,unsigned length);
extern int open_cfw_gx8002_flash_page_program(unsigned address,const void *buffer,unsigned length);
extern int open_cfw_gx8002_flash_sync(void);
extern int open_cfw_gx8002_flash_block_range(uint32_t address,uint32_t length, volatile uint32_t *start, volatile uint32_t *end);
extern char *open_cfw_gx8002_flash_gettype(void);
extern int open_cfw_gx8002_flash_getinfo(unsigned selector);
extern int open_cfw_gx8002_flash_write_protect_mode(void);
extern int open_cfw_gx8002_flash_write_protect_status(unsigned *length);
extern int open_cfw_gx8002_flash_write_protect_lock(unsigned requested);
extern int open_cfw_gx8002_flash_write_protect_unlock(void);
extern int open_cfw_gx8002_flash_otp_lock(void);
extern int open_cfw_gx8002_flash_otp_status(uint8_t *locked);
extern int open_cfw_gx8002_flash_otp_erase(void);
extern int open_cfw_gx8002_flash_otp_write(unsigned offset,const uint8_t *buffer,unsigned length);
extern int open_cfw_gx8002_flash_otp_read(unsigned offset,uint8_t *buffer,unsigned length);
extern int open_cfw_gx8002_flash_otp_get_region(unsigned *count);
extern int open_cfw_gx8002_flash_otp_set_region(unsigned region);
extern int open_cfw_gx8002_flash_otp_get_current_region(unsigned *region);
extern int open_cfw_gx8002_flash_otp_get_region_size(unsigned *size);
extern int open_cfw_gx8002_flash_uid_read(uint8_t *buffer,int requested,volatile int *actual);

struct open_cfw_gx8002_flash_interface_table {
    __typeof__(open_cfw_gx8002_flash_interface_initialize) *init;
    __typeof__(open_cfw_gx8002_flash_read) *readdata;
    __typeof__(open_cfw_gx8002_flash_chip_erase) *chiperase;
    __typeof__(open_cfw_gx8002_flash_erase) *erasedata;
    __typeof__(open_cfw_gx8002_flash_page_program) *pageprogram;
    __typeof__(open_cfw_gx8002_flash_sync) *sync;
    void (*test)(int argc, char *argv[]);
    __typeof__(open_cfw_gx8002_flash_block_range) *calcblockrange;
    int (*badinfo)(void);
    int (*pageprogram_yaffs2)(unsigned int addr, unsigned char *data, unsigned int len);
    int (*readoob)(unsigned int addr, unsigned char *data, unsigned int len);
    int (*writeoob)(unsigned int addr, unsigned char *data, unsigned int len);
    __typeof__(open_cfw_gx8002_flash_gettype) *gettype;
    __typeof__(open_cfw_gx8002_flash_getinfo) *getinfo;
    __typeof__(open_cfw_gx8002_flash_write_protect_mode) *write_protect_mode;
    __typeof__(open_cfw_gx8002_flash_write_protect_status) *write_protect_status;
    __typeof__(open_cfw_gx8002_flash_write_protect_lock) *write_protect_lock;
    __typeof__(open_cfw_gx8002_flash_write_protect_unlock) *write_protect_unlock;
    __typeof__(open_cfw_gx8002_flash_otp_lock) *otp_lock;
    __typeof__(open_cfw_gx8002_flash_otp_status) *otp_status;
    __typeof__(open_cfw_gx8002_flash_otp_erase) *otp_erase;
    __typeof__(open_cfw_gx8002_flash_otp_write) *otp_write;
    __typeof__(open_cfw_gx8002_flash_otp_read) *otp_read;
    __typeof__(open_cfw_gx8002_flash_otp_get_region) *otp_get_region;
    __typeof__(open_cfw_gx8002_flash_otp_set_region) *otp_set_region;
    __typeof__(open_cfw_gx8002_flash_otp_get_current_region) *otp_get_current_region;
    __typeof__(open_cfw_gx8002_flash_otp_get_region_size) *otp_get_region_size;
    int (*block_isbad)(unsigned int addr);
    int (*calc_phy_offset)(unsigned int start, unsigned int logic_offset, unsigned int *phy_offset);
    __typeof__(open_cfw_gx8002_flash_uid_read) *uid_read;
};
_Static_assert(sizeof(struct open_cfw_gx8002_flash_interface_table)==120,"flash interface size");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,init)==0,"init offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,readdata)==4,"readdata offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,chiperase)==8,"chiperase offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,erasedata)==12,"erasedata offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,pageprogram)==16,"pageprogram offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,sync)==20,"sync offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,test)==24,"test offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,calcblockrange)==28,"calcblockrange offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,badinfo)==32,"badinfo offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,pageprogram_yaffs2)==36,"pageprogram_yaffs2 offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,readoob)==40,"readoob offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,writeoob)==44,"writeoob offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,gettype)==48,"gettype offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,getinfo)==52,"getinfo offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,write_protect_mode)==56,"write_protect_mode offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,write_protect_status)==60,"write_protect_status offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,write_protect_lock)==64,"write_protect_lock offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,write_protect_unlock)==68,"write_protect_unlock offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,otp_lock)==72,"otp_lock offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,otp_status)==76,"otp_status offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,otp_erase)==80,"otp_erase offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,otp_write)==84,"otp_write offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,otp_read)==88,"otp_read offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,otp_get_region)==92,"otp_get_region offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,otp_set_region)==96,"otp_set_region offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,otp_get_current_region)==100,"otp_get_current_region offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,otp_get_region_size)==104,"otp_get_region_size offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,block_isbad)==108,"block_isbad offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,calc_phy_offset)==112,"calc_phy_offset offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_interface_table,uid_read)==116,"uid_read offset");
extern struct open_cfw_gx8002_flash_interface_table open_cfw_gx8002_flash_interface;
#endif
