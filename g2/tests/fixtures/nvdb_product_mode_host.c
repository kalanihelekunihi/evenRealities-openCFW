#include <string.h>
#include "nvdb_product_mode_host.h"
unsigned char open_cfw_test_nvdb_product_mode_record[4];
unsigned char open_cfw_test_nvdb_product_mode_stored[4];
unsigned char open_cfw_test_nvdb_product_mode_written[4];
unsigned int open_cfw_test_nvdb_product_mode_writes;
unsigned int open_cfw_test_nvdb_product_mode_diags;
int open_cfw_test_nvdb_product_mode_read_result;
unsigned short open_cfw_test_nvdb_product_mode_crc(const unsigned char *p,unsigned int n,const unsigned short *s){unsigned short c=s?*s:0xffffu;unsigned int i,j;for(i=0;i<n;i++){c^=(unsigned short)(p[i]<<8);for(j=0;j<8;j++)c=(unsigned short)((c&0x8000u)?(c<<1)^0x1021u:c<<1);}return c;}
int open_cfw_test_nvdb_product_mode_read(const char *k,void *p,unsigned short n){if(strcmp(k,"nvProdMode")||n!=4)return -9;memcpy(p,open_cfw_test_nvdb_product_mode_stored,4);return open_cfw_test_nvdb_product_mode_read_result;}
int open_cfw_test_nvdb_product_mode_write(const char *k,const void *p,unsigned short n){if(strcmp(k,"nvProdMode")||n!=4)return -9;memcpy(open_cfw_test_nvdb_product_mode_written,p,4);open_cfw_test_nvdb_product_mode_writes++;return 0;}
void open_cfw_test_nvdb_product_mode_diag(unsigned char m){(void)m;open_cfw_test_nvdb_product_mode_diags++;}
void open_cfw_test_nvdb_product_mode_reset(void){unsigned char d[4]={1,0,0,0};memcpy(open_cfw_test_nvdb_product_mode_record,d,4);memset(open_cfw_test_nvdb_product_mode_stored,0,4);memset(open_cfw_test_nvdb_product_mode_written,0,4);open_cfw_test_nvdb_product_mode_writes=0;open_cfw_test_nvdb_product_mode_diags=0;open_cfw_test_nvdb_product_mode_read_result=0;}
void open_cfw_test_nvdb_product_mode_set_stored(const unsigned char *p,int r){memcpy(open_cfw_test_nvdb_product_mode_stored,p,4);open_cfw_test_nvdb_product_mode_read_result=r;}
