#include <stdint.h>
#include <stdio.h>
#include <string.h>

static uint8_t flash[0x8000], file_data[0x8000], wire[0x2000];
static uint32_t file_size_value, file_position, wire_len, erase_count;
static uint32_t sync_state, sync_progress, commit_count;
static uint8_t transfer_raw[0x70], export_raw[0x60], chunk[0x1000], interface_value;

#define OPEN_CFW_OTA_TRANSFER (*(open_cfw_ota_transfer *)transfer_raw)
#define OPEN_CFW_OTA_EXPORT (*(open_cfw_ota_export *)export_raw)
#define OPEN_CFW_OTA_INTERFACE interface_value
#define OPEN_CFW_OTA_BUFFER chunk
#define OPEN_CFW_OTA_SEND(r,c,p,n) host_send((r),(c),(p),(n))
#define OPEN_CFW_OTA_FILE_OPEN(p,m) host_open((p),(m))
#define OPEN_CFW_OTA_FILE_CLOSE(h) host_close(h)
#define OPEN_CFW_OTA_FILE_READ(d,n,h) host_read((d),(n),(h))
#define OPEN_CFW_OTA_FILE_WRITE(d,n,h) host_write((d),(n),(h))
#define OPEN_CFW_OTA_FILE_SEEK(h,o) host_seek((h),(o))
#define OPEN_CFW_OTA_FILE_SIZE(h) host_size(h)
#define OPEN_CFW_OTA_FILE_REMOVE(p) host_remove(p)
#define OPEN_CFW_OTA_FLASH_ERASE(b,a,n) host_erase((b),(a),(n))
#define OPEN_CFW_OTA_FLASH_READ(b,a,d,n) host_flash_read((b),(a),(d),(n))
#define OPEN_CFW_OTA_FLASH_WRITE(b,a,d,n) host_flash_write((b),(a),(d),(n))
#define OPEN_CFW_OTA_CRC32C(d,n,c) host_crc((d),(n),(c))
#define OPEN_CFW_OTA_SECURE_COMMIT(a,n,c) host_commit((a),(n),(c))
#define OPEN_CFW_OTA_STATUS_SYNC(s,p,d) host_sync((s),(p),(d))
#define OPEN_CFW_OTA_FS_PROBE() host_probe()
#define OPEN_CFW_OTA_FS_HEAL() host_heal()

static int8_t host_send(uint8_t r,uint8_t c,const uint8_t*p,uint16_t n){(void)r;wire[0]=c;memcpy(wire+1,p,n);wire_len=n+1;return 0;}
static uint32_t host_open(const uint8_t*p,uint32_t m){(void)p;if(m==2U){file_size_value=0;file_position=0;}else file_position=0;return 1;}
static int32_t host_close(uint32_t h){(void)h;return 0;}
static uint32_t host_read(void*d,uint32_t n,uint32_t h){(void)h;if(file_position+n>file_size_value)n=file_size_value-file_position;memcpy(d,file_data+file_position,n);file_position+=n;return n;}
static uint32_t host_write(const void*d,uint32_t n,uint32_t h){(void)h;memcpy(file_data+file_position,d,n);file_position+=n;if(file_position>file_size_value)file_size_value=file_position;return n;}
static int32_t host_seek(uint32_t h,uint32_t o){(void)h;file_position=o;return 0;}
static int32_t host_size(uint32_t h){(void)h;return (int32_t)file_size_value;}
static int32_t host_remove(const uint8_t*p){(void)p;file_size_value=0;file_position=0;return 0;}
static int32_t host_erase(uint32_t b,uint32_t a,uint32_t n){(void)b;if(a<0x410000U||a-0x410000U+n>sizeof(flash))return -1;memset(flash+a-0x410000U,0xff,n);erase_count++;return 0;}
static int32_t host_flash_read(uint32_t b,uint32_t a,void*d,uint32_t n){(void)b;memcpy(d,flash+a-0x410000U,n);return 0;}
static int32_t host_flash_write(uint32_t b,uint32_t a,const void*d,uint32_t n){(void)b;memcpy(flash+a-0x410000U,d,n);return 0;}
static void host_crc(const uint8_t*d,uint32_t n,uint32_t*c){uint32_t i;for(i=0;i<n;i++)*c=(*c*33U)^d[i];}
static int32_t host_commit(uint32_t a,uint32_t n,uint32_t c){(void)a;(void)n;(void)c;commit_count++;return 0;}
static void host_sync(uint32_t s,uint32_t p,uint32_t d){(void)d;sync_state=s;sync_progress=p;}
static int32_t host_probe(void){return 0;}
static int32_t host_heal(void){return 0;}

#include "../../components/apollo_main/core_overlay/ota_service.c"

static int require(int value,const char*name){if(!value){fprintf(stderr,"FAIL %s\n",name);return 1;}return 0;}
int main(void){
 uint8_t meta[17+4]={0,4,0,0,0,0,0,0,0,0,0x10,0x41,0,4,0,0,0,'t','e','s','t'};
 uint8_t data[4]={1,2,3,4};uint32_t crc=0;uint8_t frame[22];
 host_crc(data,4,&crc);meta[5]=(uint8_t)crc;meta[6]=(uint8_t)(crc>>8);meta[7]=(uint8_t)(crc>>16);meta[8]=(uint8_t)(crc>>24);
 memcpy(frame+1,meta,sizeof(meta));frame[0]=0;
 if(require(OTA_FrameDispatch(OTA_IMPORT_CONTROL,frame,sizeof(frame))==0,"dispatch start"))return 1;
 if(require(erase_count==1 && OPEN_CFW_OTA_TRANSFER.active,"erase active"))return 1;
 if(require(OTA_FrameDispatch(OTA_IMPORT_DATA,data,4)==0,"dispatch data"))return 1;
 if(require(!memcmp(flash+0x1000,data,4) && sync_progress==100,"write verify progress"))return 1;
 _fileCmdParse(2,0,0,0);
 if(require(commit_count==1 && sync_state==2 && wire[2]==OTA_OK,"commit"))return 1;
 file_size_value=4;file_position=0;memcpy(file_data,data,4);_exportFileParse(0,(const uint8_t*)"log",3,0);
 if(require(OPEN_CFW_OTA_EXPORT.active && wire_len==10,"export meta"))return 1;
 _exportFileParse(1,0,0,0);if(require(wire[0]==OTA_EXPORT_ALT && wire_len==5,"export chunk"))return 1;
 if(require(OtaParseHexAddress((const uint8_t*)"410000",6,0,0)==0x410000U,"hex"))return 1;
 OTA_SetInterface(2,7,OTA_FrameDispatch,1);if(require(interface_value==2,"interface"))return 1;
 if(require(_otaFsHealthCheckAndHeal(0,0,0,0)==0,"fs health"))return 1;
 puts("ota service host: PASS");return 0;
}
