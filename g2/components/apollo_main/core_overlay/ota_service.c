/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room implementation of the G2 OTA file service.  This preserves the
 * recovered C0/C1/C2/C3 command ABI, the 0x70-byte transfer record, the
 * 0x60-byte export record, 4 KiB sector/chunk policy, CRC-32C checks,
 * read-after-write verification, filesystem health recovery, and explicit
 * MRAM/filesystem/external-flash backend selection.
 */

#include <stddef.h>
#include <stdint.h>

#define OTA_IMPORT_CONTROL 0xC0U
#define OTA_IMPORT_DATA 0xC1U
#define OTA_EXPORT_CONTROL 0xC2U
#define OTA_EXPORT_ALT 0xC3U
#define OTA_CHUNK_BYTES 0x1000U
#define OTA_PATH_BYTES 64U
#define OTA_OK 0U
#define OTA_INVALID 1U
#define OTA_CRC_ERROR 2U
#define OTA_IO_ERROR 3U
#define OTA_VERIFY_ERROR 4U
#define OTA_SIZE_ERROR 5U
#define OTA_BACKEND_MRAM 0U
#define OTA_BACKEND_FILE 1U
#define OTA_BACKEND_XIP 2U

typedef struct {
    uint32_t handle;
    uint32_t address;
    uint32_t backend;
    uint32_t file_type;
    uint32_t file_size;
    uint32_t expected_crc;
    uint32_t running_crc;
    uint32_t chunk_length;
    uint32_t transferred;
    uint32_t remaining;
    uint8_t path[OTA_PATH_BYTES];
    uint8_t open;
    uint8_t active;
    uint8_t committed;
    uint8_t progress;
    uint32_t reserved;
} open_cfw_ota_transfer;

typedef struct {
    uint32_t handle;
    uint32_t file_size;
    uint32_t file_crc;
    uint32_t transferred;
    uint32_t remaining;
    uint8_t path[OTA_PATH_BYTES];
    uint8_t active;
    uint8_t command;
    uint8_t reserved[10];
} open_cfw_ota_export;

_Static_assert(sizeof(open_cfw_ota_transfer) == 0x70U,
    "G2 OTA transfer ABI must remain 112 bytes");
_Static_assert(sizeof(open_cfw_ota_export) == 0x60U,
    "G2 OTA export ABI must remain 96 bytes");

#ifndef OPEN_CFW_OTA_TRANSFER
#define OPEN_CFW_OTA_TRANSFER (*(open_cfw_ota_transfer *)(uintptr_t)0x20072730U)
#endif
#ifndef OPEN_CFW_OTA_EXPORT
#define OPEN_CFW_OTA_EXPORT (*(open_cfw_ota_export *)(uintptr_t)0x20071FF0U)
#endif
#ifndef OPEN_CFW_OTA_INTERFACE
#define OPEN_CFW_OTA_INTERFACE (*(volatile uint8_t *)(uintptr_t)0x20074FF3U)
#endif
#ifndef OPEN_CFW_OTA_BUFFER
#define OPEN_CFW_OTA_BUFFER ((uint8_t *)(uintptr_t)0x2034CC20U)
#endif

#ifndef OPEN_CFW_OTA_SEND
int8_t open_cfw_ota_service_send(uint8_t response, uint8_t command,
    const uint8_t *payload, uint16_t length);
#define OPEN_CFW_OTA_SEND(r,c,p,n) open_cfw_ota_service_send((r),(c),(p),(n))
#endif
#ifndef OPEN_CFW_OTA_FILE_OPEN
uint32_t open_cfw_ota_file_open(const uint8_t *path, uint32_t mode);
#define OPEN_CFW_OTA_FILE_OPEN(p,m) open_cfw_ota_file_open((p),(m))
#endif
#ifndef OPEN_CFW_OTA_FILE_CLOSE
int32_t open_cfw_ota_file_close(uint32_t handle);
#define OPEN_CFW_OTA_FILE_CLOSE(h) open_cfw_ota_file_close((h))
#endif
#ifndef OPEN_CFW_OTA_FILE_READ
uint32_t open_cfw_ota_file_read(void *data, uint32_t item_size, uint32_t count, uint32_t handle);
#define OPEN_CFW_OTA_FILE_READ(d,n,h) open_cfw_ota_file_read((d),1U,(n),(h))
#endif
#ifndef OPEN_CFW_OTA_FILE_WRITE
uint32_t open_cfw_ota_file_write(const void *data, uint32_t item_size, uint32_t count, uint32_t handle);
#define OPEN_CFW_OTA_FILE_WRITE(d,n,h) open_cfw_ota_file_write((d),1U,(n),(h))
#endif
#ifndef OPEN_CFW_OTA_FILE_SEEK
int32_t open_cfw_ota_file_seek(uint32_t handle, int32_t offset, uint32_t origin);
#define OPEN_CFW_OTA_FILE_SEEK(h,o) open_cfw_ota_file_seek((h),(int32_t)(o),0U)
#endif
#ifndef OPEN_CFW_OTA_FILE_SIZE
int32_t open_cfw_ota_file_size(uint32_t handle);
#define OPEN_CFW_OTA_FILE_SIZE(h) open_cfw_ota_file_size((h))
#endif
#ifndef OPEN_CFW_OTA_FILE_REMOVE
int32_t open_cfw_ota_file_remove(const uint8_t *path);
#define OPEN_CFW_OTA_FILE_REMOVE(p) open_cfw_ota_file_remove((p))
#endif
#ifndef OPEN_CFW_OTA_FLASH_ERASE
#define OPEN_CFW_OTA_NEEDS_FLASH_ADAPTER 1
int32_t open_cfw_ota_flash_erase(uint32_t backend, uint32_t address, uint32_t bytes);
#define OPEN_CFW_OTA_FLASH_ERASE(b,a,n) open_cfw_ota_flash_erase((b),(a),(n))
#endif
#ifndef OPEN_CFW_OTA_FLASH_READ
int32_t open_cfw_ota_flash_read(uint32_t backend, uint32_t address, void *data, uint32_t bytes);
#define OPEN_CFW_OTA_FLASH_READ(b,a,d,n) open_cfw_ota_flash_read((b),(a),(d),(n))
#endif
#ifndef OPEN_CFW_OTA_FLASH_WRITE
int32_t open_cfw_ota_flash_write(uint32_t backend, uint32_t address, const void *data, uint32_t bytes);
#define OPEN_CFW_OTA_FLASH_WRITE(b,a,d,n) open_cfw_ota_flash_write((b),(a),(d),(n))
#endif
#ifndef OPEN_CFW_OTA_CRC32C
void open_cfw_ota_crc32c(const uint8_t *data, uint32_t bytes, uint32_t *crc);
#define OPEN_CFW_OTA_CRC32C(d,n,c) open_cfw_ota_crc32c((d),(n),(c))
#endif
#ifndef OPEN_CFW_OTA_SECURE_COMMIT
uint32_t open_cfw_ota_secure_commit(uint32_t key, uint8_t image_magic, uint32_t *image);
#define OPEN_CFW_OTA_SECURE_COMMIT(a,n,c) \
    ((void)(n),(void)(c),(int32_t)open_cfw_ota_secure_commit(0x12344321U,0U,(uint32_t *)(uintptr_t)(a)))
#endif
#ifndef OPEN_CFW_OTA_STATUS_SYNC
#define OPEN_CFW_OTA_NEEDS_STATUS_ADAPTER 1
void open_cfw_ota_status_sync(uint32_t state, uint32_t progress, uint32_t detail);
#define OPEN_CFW_OTA_STATUS_SYNC(s,p,d) open_cfw_ota_status_sync((s),(p),(d))
#endif
#ifndef OPEN_CFW_OTA_FS_PROBE
int32_t open_cfw_ota_fs_probe(void);
#define OPEN_CFW_OTA_FS_PROBE() open_cfw_ota_fs_probe()
#endif
#ifndef OPEN_CFW_OTA_FS_HEAL
int32_t open_cfw_ota_fs_heal(void);
#define OPEN_CFW_OTA_FS_HEAL() open_cfw_ota_fs_heal()
#endif
typedef int (*open_cfw_ota_callback)(uint8_t, const uint8_t *, uint16_t);

/*
 * The authenticated EFS and OTA translation units both exported a local
 * helper named _fileCaculateCRC.  Selector leaves share one flat overlay
 * namespace, so retain the recovered OTA ABI in ordinary/host builds while
 * giving its production leaf an unambiguous source-owned symbol.
 */
#if defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD)
#define _fileCaculateCRC OTA_FileCaculateCRC
#endif

uint32_t OtaSelectFlashOps(uint32_t);
int32_t OtaFileSize(uint32_t);
int32_t OtaEraseRange(uint32_t,uint32_t);
uint8_t _evenOtaSetFwAddr(uint32_t,uint32_t,uint32_t,uint32_t);
int32_t _verifyFlashContent(uint32_t,uint32_t,const uint8_t *,uint32_t);
int32_t OtaBufferedFlashWrite(uint32_t,const uint8_t *,uint32_t,uint32_t);
int32_t OtaCommitDescriptor(void);
void _evenOtaReplyToAPP(uint8_t,uint8_t,uint8_t,uint32_t);
void _RPC_SystemOtaStatusSync(uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t OtaParseHexAddress(const uint8_t *,uint32_t,uint32_t,uint32_t);
int32_t _evenOtaBootloaderWriteFile2MRAM(const uint8_t *,uint32_t,uint32_t,uint32_t);
int32_t _otaFsHealthProbe(void);
int32_t _otaFsHealthCheckAndHeal(uint32_t,uint32_t,uint32_t,uint32_t);
void _fileCmdParse(uint8_t,const uint8_t *,uint16_t,uint32_t);
void _fileRawDataParse(const uint8_t *,uint16_t);
uint32_t _fileCaculateCRC(uint32_t *,const uint8_t *,uint32_t *,uint32_t *);
void _exportFileParse(uint8_t,const uint8_t *,uint16_t,uint32_t);
int OTA_FrameDispatch(uint8_t,const uint8_t *,uint16_t);
uint32_t OTA_ResetExportState(void);
uint32_t OTA_NotifyStatus4(uint8_t);
uint32_t OTA_NotifyStatus3(uint8_t);
uint32_t OTA_NotifyStatus5(uint8_t);
uint32_t OTA_CancelExport(void);
uint8_t OTA_TransferActive(void);
void OTA_SetInterface(uint32_t,uint32_t,open_cfw_ota_callback,uint32_t);

static __attribute__((unused)) inline void ota_zero(void *raw, uint32_t bytes) {
    uint8_t *p = raw; while (bytes-- != 0U) *p++ = 0U;
}
static __attribute__((unused)) inline void ota_copy(void *raw_dst, const void *raw_src, uint32_t bytes) {
    uint8_t *d=raw_dst; const uint8_t *s=raw_src; while (bytes-- != 0U) *d++=*s++;
}
static __attribute__((unused)) inline uint32_t ota_load32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1]<<8) | ((uint32_t)p[2]<<16) | ((uint32_t)p[3]<<24);
}
static __attribute__((unused)) inline void ota_store32(uint8_t *p,uint32_t v) {
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);
}
static __attribute__((unused)) inline uint32_t ota_round_sector(uint32_t n) {
    return (n + OTA_CHUNK_BYTES - 1U) & ~(OTA_CHUNK_BYTES - 1U);
}
static __attribute__((unused)) inline uint32_t ota_div32(uint32_t numerator,uint32_t denominator) {
    uint32_t quotient=0U,remainder=0U,index;if(denominator==0U)return 0U;
    for(index=0U;index<32U;index++){remainder=(remainder<<1U)|(numerator>>31U);numerator<<=1U;quotient<<=1U;if(remainder>=denominator){remainder-=denominator;quotient|=1U;}}
    return quotient;
}
static __attribute__((unused)) inline uint8_t ota_path_copy(uint8_t *dst,const uint8_t *src,uint32_t n) {
    uint32_t i;if (src==0 || n==0U || n>=OTA_PATH_BYTES) return 0U;
    for(i=0;i<n && src[i]!=0U;i++) dst[i]=src[i];
    if(i==OTA_PATH_BYTES) return 0U;dst[i]=0U;return 1U;
}
static __attribute__((unused)) inline void ota_reply(uint8_t command,uint8_t sub,uint8_t status) {
    uint8_t p[2];p[0]=sub;p[1]=status;
    if (OPEN_CFW_OTA_INTERFACE != 1U) (void)OPEN_CFW_OTA_SEND(1U,command,p,2U);
}
static __attribute__((unused)) inline void ota_close_transfer(void) {
    if (OPEN_CFW_OTA_TRANSFER.handle!=0U) (void)OPEN_CFW_OTA_FILE_CLOSE(OPEN_CFW_OTA_TRANSFER.handle);
    OPEN_CFW_OTA_TRANSFER.handle=0U;OPEN_CFW_OTA_TRANSFER.open=0U;
}
static __attribute__((unused)) inline void ota_reset_transfer(void) {
    ota_close_transfer();ota_zero(&OPEN_CFW_OTA_TRANSFER,sizeof(OPEN_CFW_OTA_TRANSFER));
}
static __attribute__((unused)) inline void ota_reset_export(void) {
    if (OPEN_CFW_OTA_EXPORT.handle!=0U) (void)OPEN_CFW_OTA_FILE_CLOSE(OPEN_CFW_OTA_EXPORT.handle);
    ota_zero(&OPEN_CFW_OTA_EXPORT,sizeof(OPEN_CFW_OTA_EXPORT));
}

#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_SELECT_ONLY)
uint32_t OtaSelectFlashOps(uint32_t file_type) {
    if (file_type==0U || file_type==1U) return OTA_BACKEND_MRAM;
    if (file_type==2U || file_type==3U || file_type==4U || file_type==5U) return OTA_BACKEND_FILE;
    return OTA_BACKEND_XIP;
}
#endif /* OtaSelectFlashOps */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_FILE_SIZE_ONLY)
int32_t OtaFileSize(uint32_t handle) { return handle==0U ? -1 : OPEN_CFW_OTA_FILE_SIZE(handle); }
#endif /* OtaFileSize */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_ERASE_ONLY)
int32_t OtaEraseRange(uint32_t address,uint32_t bytes) {
    if (bytes==0U || address+bytes<address) return -1;
    return OPEN_CFW_OTA_FLASH_ERASE(OPEN_CFW_OTA_TRANSFER.backend,address,ota_round_sector(bytes));
}
#endif /* OtaEraseRange */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_SET_ADDR_ONLY)
uint8_t _evenOtaSetFwAddr(uint32_t file_type,uint32_t address,uint32_t bytes,uint32_t flags) {
    uint32_t backend=OtaSelectFlashOps(file_type);(void)flags;
    if (bytes==0U || bytes>0x02000000U || address+bytes<address) return 0U;
    if (backend==OTA_BACKEND_MRAM && (address<0x00410000U || address+bytes>0x00794324U)) return 0U;
    OPEN_CFW_OTA_TRANSFER.backend=backend;OPEN_CFW_OTA_TRANSFER.address=address;
    return backend==OTA_BACKEND_FILE || OtaEraseRange(address,bytes)==0;
}
#endif /* _evenOtaSetFwAddr */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_VERIFY_ONLY)
int32_t _verifyFlashContent(uint32_t backend,uint32_t address,const uint8_t *expected,uint32_t bytes) {
    uint8_t *scratch=OPEN_CFW_OTA_BUFFER;uint32_t done=0U,i,n;
    if(expected==0 || scratch==0) return -1;
    while(done<bytes){n=bytes-done;if(n>OTA_CHUNK_BYTES)n=OTA_CHUNK_BYTES;
        if(OPEN_CFW_OTA_FLASH_READ(backend,address+done,scratch,n)!=0)return -1;
        for(i=0;i<n;i++)if(scratch[i]!=expected[done+i])return -1;done+=n;}
    return 0;
}
#endif /* _verifyFlashContent */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_BUFFERED_WRITE_ONLY)
int32_t OtaBufferedFlashWrite(uint32_t address,const uint8_t *data,uint32_t bytes,uint32_t backend) {
    if(data==0 || bytes==0U || bytes>OTA_CHUNK_BYTES)return -1;
    if(OPEN_CFW_OTA_FLASH_WRITE(backend,address,data,bytes)!=0)return -1;
    return _verifyFlashContent(backend,address,data,bytes);
}
#endif /* OtaBufferedFlashWrite */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_COMMIT_ONLY)
int32_t OtaCommitDescriptor(void) {
    open_cfw_ota_transfer *t=&OPEN_CFW_OTA_TRANSFER;
    if(!t->active || t->transferred!=t->file_size || t->running_crc!=t->expected_crc)return -1;
    if(t->backend==OTA_BACKEND_MRAM && OPEN_CFW_OTA_SECURE_COMMIT(t->address,t->file_size,t->running_crc)!=0)return -1;
    t->committed=1U;return 0;
}
#endif /* OtaCommitDescriptor */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_REPLY_ONLY)
void _evenOtaReplyToAPP(uint8_t command,uint8_t subcommand,uint8_t status,uint32_t reserved) {
    (void)reserved;ota_reply(command,subcommand,status);
}
#endif /* _evenOtaReplyToAPP */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_RPC_STATUS_ONLY)
void _RPC_SystemOtaStatusSync(uint32_t state,uint32_t progress,uint32_t detail,uint32_t reserved) {
    (void)reserved;OPEN_CFW_OTA_STATUS_SYNC(state,progress,detail);
}
#endif /* _RPC_SystemOtaStatusSync */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_PARSE_HEX_ONLY)
uint32_t OtaParseHexAddress(const uint8_t *text,uint32_t length,uint32_t fallback,uint32_t reserved) {
    uint32_t value=0U,i;uint8_t c;(void)reserved;if(text==0 || length==0U)return fallback;
    for(i=0;i<length;i++){c=text[i];if(c==0U)break;if(c>='0'&&c<='9')c=(uint8_t)(c-'0');
        else if(c>='a'&&c<='f')c=(uint8_t)(c-'a'+10U);else if(c>='A'&&c<='F')c=(uint8_t)(c-'A'+10U);else return fallback;
        if(value>0x0FFFFFFFU)return fallback;value=(value<<4)|c;}return value;
}
#endif /* OtaParseHexAddress */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_BOOT_MRAM_ONLY)
int32_t _evenOtaBootloaderWriteFile2MRAM(const uint8_t *path,uint32_t address,uint32_t expected_size,uint32_t expected_crc) {
    uint32_t h,done=0U,n,crc=0U;int32_t size;uint8_t *buffer=OPEN_CFW_OTA_BUFFER;
    if(path==0 || buffer==0)return -1;h=OPEN_CFW_OTA_FILE_OPEN(path,1U);if(h==0U)return -1;
    size=OtaFileSize(h);if(size<0 || (expected_size!=0U && (uint32_t)size!=expected_size)){(void)OPEN_CFW_OTA_FILE_CLOSE(h);return -1;}
    OPEN_CFW_OTA_TRANSFER.backend=OTA_BACKEND_MRAM;if(OtaEraseRange(address,(uint32_t)size)!=0){(void)OPEN_CFW_OTA_FILE_CLOSE(h);return -1;}
    while(done<(uint32_t)size){n=(uint32_t)size-done;if(n>OTA_CHUNK_BYTES)n=OTA_CHUNK_BYTES;
        if(OPEN_CFW_OTA_FILE_READ(buffer,n,h)!=n || OtaBufferedFlashWrite(address+done,buffer,n,OTA_BACKEND_MRAM)!=0){(void)OPEN_CFW_OTA_FILE_CLOSE(h);return -1;}
        OPEN_CFW_OTA_CRC32C(buffer,n,&crc);done+=n;}
    (void)OPEN_CFW_OTA_FILE_CLOSE(h);if(expected_crc!=0U && crc!=expected_crc)return -1;
    return OPEN_CFW_OTA_SECURE_COMMIT(address,(uint32_t)size,crc);
}
#endif /* _evenOtaBootloaderWriteFile2MRAM */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_FS_PROBE_ONLY)
int32_t _otaFsHealthProbe(void) { return OPEN_CFW_OTA_FS_PROBE(); }
#endif /* _otaFsHealthProbe */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_FS_HEAL_ONLY)
int32_t _otaFsHealthCheckAndHeal(uint32_t reason,uint32_t arg1,uint32_t arg2,uint32_t arg3) {
    (void)reason;(void)arg1;(void)arg2;(void)arg3;if(_otaFsHealthProbe()==0)return 0;
    return OPEN_CFW_OTA_FS_HEAL()==0 && _otaFsHealthProbe()==0 ? 0 : -1;
}
#endif /* _otaFsHealthCheckAndHeal */

#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_COMMAND_ONLY)
void _fileCmdParse(uint8_t subcommand,const uint8_t *data,uint16_t length,uint32_t reserved) {
    open_cfw_ota_transfer *t=&OPEN_CFW_OTA_TRANSFER;uint8_t status=OTA_INVALID;uint32_t path_len;(void)reserved;
    if(subcommand==0U){ota_reset_transfer();if(data!=0 && length>=17U){t->file_type=data[0];t->file_size=ota_load32(data+1);t->expected_crc=ota_load32(data+5);t->address=ota_load32(data+9);path_len=ota_load32(data+13);
        if(path_len<=((uint32_t)length-17U) && ota_path_copy(t->path,data+17,path_len) && _evenOtaSetFwAddr(t->file_type,t->address,t->file_size,0U)){
            if(t->backend==OTA_BACKEND_FILE){(void)OPEN_CFW_OTA_FILE_REMOVE(t->path);t->handle=OPEN_CFW_OTA_FILE_OPEN(t->path,2U);t->open=t->handle!=0U;if(!t->open)goto reply;}
            t->remaining=t->file_size;t->active=1U;status=OTA_OK;_RPC_SystemOtaStatusSync(1U,0U,t->file_type,0U);}
        }}
    else if(subcommand==1U){status=t->active?OTA_OK:OTA_INVALID;}
    else if(subcommand==2U){if(!t->active)status=OTA_INVALID;else if(t->transferred!=t->file_size)status=OTA_SIZE_ERROR;else if(t->running_crc!=t->expected_crc)status=OTA_CRC_ERROR;else if(OtaCommitDescriptor()!=0)status=OTA_VERIFY_ERROR;else{status=OTA_OK;_RPC_SystemOtaStatusSync(2U,100U,t->file_type,0U);}}
    else if(subcommand==3U){ota_reset_transfer();status=OTA_OK;_RPC_SystemOtaStatusSync(0U,0U,0U,0U);}
reply:_evenOtaReplyToAPP(OTA_IMPORT_CONTROL,subcommand,status,0U);
}
#endif /* _fileCmdParse */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_RAW_ONLY)
void _fileRawDataParse(const uint8_t *data,uint16_t length) {
    open_cfw_ota_transfer *t=&OPEN_CFW_OTA_TRANSFER;uint8_t status=OTA_OK;uint32_t written;
    if(data==0 || length==0U || length>OTA_CHUNK_BYTES || !t->active || length>t->remaining){ota_reply(OTA_IMPORT_DATA,1U,OTA_INVALID);return;}
    if(t->backend==OTA_BACKEND_FILE){written=OPEN_CFW_OTA_FILE_WRITE(data,length,t->handle);if(written!=length)status=OTA_IO_ERROR;}
    else if(OtaBufferedFlashWrite(t->address+t->transferred,data,length,t->backend)!=0)status=OTA_VERIFY_ERROR;
    if(status==OTA_OK){OPEN_CFW_OTA_CRC32C(data,length,&t->running_crc);t->transferred+=length;t->remaining-=length;t->chunk_length=length;t->progress=(uint8_t)ota_div32(t->transferred*100U,t->file_size);_RPC_SystemOtaStatusSync(1U,t->progress,t->file_type,0U);}
    else{t->active=0U;ota_close_transfer();}_evenOtaReplyToAPP(OTA_IMPORT_DATA,1U,status,0U);
}
#endif /* _fileRawDataParse */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_CRC_ONLY)
uint32_t _fileCaculateCRC(uint32_t *handle,const uint8_t *path,uint32_t *size_out,uint32_t *crc_out) {
    uint8_t *buffer=OPEN_CFW_OTA_BUFFER;int32_t size;uint32_t n,remain;
    if(handle==0||path==0||size_out==0||crc_out==0||buffer==0)return 0U;*handle=OPEN_CFW_OTA_FILE_OPEN(path,1U);if(*handle==0U)return 0U;
    size=OPEN_CFW_OTA_FILE_SIZE(*handle);if(size<0)goto fail;*size_out=(uint32_t)size;*crc_out=0U;remain=(uint32_t)size;
    while(remain!=0U){n=remain>OTA_CHUNK_BYTES?OTA_CHUNK_BYTES:remain;if(OPEN_CFW_OTA_FILE_READ(buffer,n,*handle)!=n)goto fail;OPEN_CFW_OTA_CRC32C(buffer,n,crc_out);remain-=n;}
    (void)OPEN_CFW_OTA_FILE_SEEK(*handle,0U);return 1U;
fail:(void)OPEN_CFW_OTA_FILE_CLOSE(*handle);*handle=0U;return 0U;
}
#endif /* _fileCaculateCRC */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_EXPORT_ONLY)
void _exportFileParse(uint8_t subcommand,const uint8_t *data,uint16_t length,uint32_t reserved) {
    open_cfw_ota_export *e=&OPEN_CFW_OTA_EXPORT;uint8_t meta[9];uint8_t status=OTA_INVALID;uint32_t n;(void)reserved;
    if(subcommand==0U){ota_reset_export();if(data!=0 && length>0U && ota_path_copy(e->path,data,length) && _fileCaculateCRC(&e->handle,e->path,&e->file_size,&e->file_crc)){e->remaining=e->file_size;e->active=1U;meta[0]=0U;ota_store32(meta+1,e->file_size);ota_store32(meta+5,e->file_crc);(void)OPEN_CFW_OTA_SEND(1U,OTA_EXPORT_CONTROL,meta,9U);return;}
    }
    else if(subcommand==1U && e->active){n=e->remaining>OTA_CHUNK_BYTES?OTA_CHUNK_BYTES:e->remaining;if(n==0U){status=OTA_OK;ota_reset_export();}else if(OPEN_CFW_OTA_FILE_READ(OPEN_CFW_OTA_BUFFER,n,e->handle)==n){(void)OPEN_CFW_OTA_SEND(1U,OTA_EXPORT_ALT,OPEN_CFW_OTA_BUFFER,(uint16_t)n);e->transferred+=n;e->remaining-=n;return;}else{status=OTA_IO_ERROR;ota_reset_export();}}
    else if(subcommand==2U || subcommand==3U){ota_reset_export();status=OTA_OK;}
    ota_reply(OTA_EXPORT_CONTROL,subcommand,status);
}
#endif /* _exportFileParse */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_DISPATCH_ONLY)
int OTA_FrameDispatch(uint8_t command,const uint8_t *payload,uint16_t length) {
    if(payload==0 || length==0U)return -1;if(command==OTA_IMPORT_CONTROL){_fileCmdParse(payload[0],payload+1,(uint16_t)(length-1U),0U);return 0;}
    if(command==OTA_IMPORT_DATA){_fileRawDataParse(payload,length);return 0;}if(command==OTA_EXPORT_CONTROL||command==OTA_EXPORT_ALT){_exportFileParse(payload[0],payload+1,(uint16_t)(length-1U),0U);return 0;}return -1;
}
#endif /* OTA_FrameDispatch */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_RESET_EXPORT_ONLY)
uint32_t OTA_ResetExportState(void) { ota_reset_export();return 0U; }
#endif /* OTA_ResetExportState */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_STATUS4_ONLY)
uint32_t OTA_NotifyStatus4(uint8_t command){uint8_t p[2]={2U,4U};return (uint32_t)(uint8_t)OPEN_CFW_OTA_SEND(1U,command,p,2U);}
#endif /* OTA_NotifyStatus4 */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_STATUS3_ONLY)
uint32_t OTA_NotifyStatus3(uint8_t command){uint8_t p[2]={2U,3U};return (uint32_t)(uint8_t)OPEN_CFW_OTA_SEND(1U,command,p,2U);}
#endif /* OTA_NotifyStatus3 */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_STATUS5_ONLY)
uint32_t OTA_NotifyStatus5(uint8_t command){uint8_t p[2]={2U,5U};return (uint32_t)(uint8_t)OPEN_CFW_OTA_SEND(1U,command,p,2U);}
#endif /* OTA_NotifyStatus5 */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_CANCEL_ONLY)
uint32_t OTA_CancelExport(void){ota_reset_export();_RPC_SystemOtaStatusSync(0U,0U,0U,0U);return 0U;}
#endif /* OTA_CancelExport */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_ACTIVE_ONLY)
uint8_t OTA_TransferActive(void){return (uint8_t)(OPEN_CFW_OTA_TRANSFER.active||OPEN_CFW_OTA_EXPORT.active);}
#endif /* OTA_TransferActive */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_INTERFACE_ONLY)
void OTA_SetInterface(uint32_t interface,uint32_t service,open_cfw_ota_callback callback,uint32_t enabled){(void)service;(void)callback;(void)enabled;OPEN_CFW_OTA_INTERFACE=(uint8_t)interface;}
#endif /* OTA_SetInterface */

#if defined(OPEN_CFW_OTA_NEEDS_FLASH_ADAPTER)
int32_t open_cfw_ota_nor_erase(uint32_t address,uint32_t bytes,uint32_t unused0,uint32_t unused1);
int32_t open_cfw_ota_nor_write(uint32_t address,const void *data,uint32_t bytes,uint32_t unused);
int32_t open_cfw_ota_nor_read(uint32_t address,void *data,uint32_t bytes,uint32_t unused);
void open_cfw_ota_mram_program(void *destination,const void *source,uint32_t bytes);

#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_FLASH_ERASE_ADAPTER_ONLY)
__attribute__((used,noinline))
int32_t open_cfw_ota_flash_erase(uint32_t backend,uint32_t address,uint32_t bytes){
    if(backend==OTA_BACKEND_MRAM)return 0;
    if(backend==OTA_BACKEND_XIP)return open_cfw_ota_nor_erase(address,bytes,0U,0U);
    return -1;
}
#endif /* open_cfw_ota_flash_erase */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_FLASH_READ_ADAPTER_ONLY)
__attribute__((used,noinline))
int32_t open_cfw_ota_flash_read(uint32_t backend,uint32_t address,void *data,uint32_t bytes){
    uint32_t i;if(data==0)return -1;if(backend==OTA_BACKEND_XIP)return open_cfw_ota_nor_read(address,data,bytes,0U);
    if(backend!=OTA_BACKEND_MRAM)return -1;for(i=0;i<bytes;i++)((uint8_t*)data)[i]=((volatile const uint8_t*)(uintptr_t)address)[i];return 0;
}
#endif /* open_cfw_ota_flash_read */
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_FLASH_WRITE_ADAPTER_ONLY)
__attribute__((used,noinline))
int32_t open_cfw_ota_flash_write(uint32_t backend,uint32_t address,const void *data,uint32_t bytes){
    if(data==0)return -1;if(backend==OTA_BACKEND_XIP)return open_cfw_ota_nor_write(address,data,bytes,0U);
    if(backend!=OTA_BACKEND_MRAM)return -1;open_cfw_ota_mram_program((void *)(uintptr_t)address,data,bytes);return 0;
}
#endif /* open_cfw_ota_flash_write */
#endif

#if defined(OPEN_CFW_OTA_NEEDS_STATUS_ADAPTER)
int32_t open_cfw_ota_rpc_post(uint32_t service,const void *payload,uint32_t bytes,uint32_t reserved);
#if !defined(OPEN_CFW_OTA_SERVICE_SELECTOR_BUILD) || defined(OPEN_CFW_OTA_SERVICE_STATUS_ADAPTER_ONLY)
__attribute__((used,noinline))
void open_cfw_ota_status_sync(uint32_t state,uint32_t progress,uint32_t detail){
    uint8_t payload[8];payload[0]=(uint8_t)state;payload[1]=(uint8_t)progress;
    payload[2]=(uint8_t)detail;payload[3]=OPEN_CFW_OTA_INTERFACE;
    ota_store32(payload+4,OPEN_CFW_OTA_TRANSFER.file_type);
    (void)open_cfw_ota_rpc_post(0x103U,payload,8U,0U);
}
#endif /* open_cfw_ota_status_sync */
#endif
