#include <stdint.h>
#include <string.h>
typedef struct { const char *key; const void *value; uint32_t value_length; } open_cfw_kvdb_default_node;
typedef struct { const open_cfw_kvdb_default_node *nodes; uint32_t count; } open_cfw_kvdb_defaults;
#define OPEN_CFW_KVDB_TYPES_DEFINED 1
static uint8_t values[12][32]; static open_cfw_kvdb_default_node nodes[12];
static uint32_t magic,boot; static int init_rc,magic_rc,reads,writes,controls,migrations;
static int rd(uint32_t i,const char*k,void*v,uint16_t z){++reads;if(i)return 0;if(!strcmp(k,"kvMagic")){if(magic_rc)memcpy(v,&magic,z);return magic_rc;}if(!strcmp(k,"kvbooCount")){memcpy(v,&boot,z);return 1;}return 1;}
static int wr(uint32_t i,const char*k,const void*v,uint16_t z){++writes;if(i)return 0;if(!strcmp(k,"kvbooCount"))memcpy(&boot,v,z);return 1;}
static void *get(uint32_t i){return i?0:values;} static int ctl(void*d,uint32_t c,void*a){(void)d;(void)c;(void)a;++controls;return 0;}
static int init(void*d,const char*n,const char*p,const open_cfw_kvdb_defaults*f,void*u){(void)d;(void)n;(void)p;(void)f;(void)u;return init_rc;}
static __attribute__((used)) int setdef(void*d){(void)d;return 0;}
#define OPEN_CFW_KVDB_DEFAULT_TABLE_ADDRESS ((uintptr_t)nodes)
#define OPEN_CFW_KVDB_MAGIC_KEY "kvMagic"
#define OPEN_CFW_KVDB_PARTITION_NAME "kvdb"
#define OPEN_CFW_KVDB_DATABASE_NAME "sysenv"
#define OPEN_CFW_KVDB_BOOT_COUNT_KEY "kvbooCount"
#define OPEN_CFW_KVDB_DB_READ rd
#define OPEN_CFW_KVDB_DB_WRITE wr
#define OPEN_CFW_KVDB_DB_GET get
#define OPEN_CFW_KVDB_DB_CONTROL ctl
#define OPEN_CFW_KVDB_DB_INIT init
#define OPEN_CFW_KVDB_DB_SET_DEFAULT setdef
#define MIG(n) void open_cfw_kvdb_migrate_##n(void){++migrations;}
MIG(1) MIG(2) MIG(3) MIG(4) MIG(5) MIG(6) MIG(7) MIG(8) MIG(9) MIG(10) MIG(11)
#define OPEN_CFW_SELECTOR 0
#include "../../components/apollo_main/core_overlay/service_kvdb.c"
void host_reset(void){uint32_t i;memset(values,0,sizeof(values));memset(nodes,0,sizeof(nodes));for(i=0;i<12;++i){nodes[i].key="x";nodes[i].value=values[i];nodes[i].value_length=1;}magic=0x5a000020u;boot=4;init_rc=0;magic_rc=1;reads=writes=controls=migrations=0;}
void host_magic(uint32_t v,int rc){magic=v;magic_rc=rc;} void host_init_rc(int v){init_rc=v;}
uint32_t host_boot(void){return boot;} int host_reads(void){return reads;} int host_writes(void){return writes;} int host_controls(void){return controls;} int host_migrations(void){return migrations;}
