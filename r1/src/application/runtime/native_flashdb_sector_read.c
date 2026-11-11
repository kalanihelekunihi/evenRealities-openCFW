#include <stdint.h>
typedef struct __attribute__((packed,may_alias)) {uint32_t value;} sector_word;
static uint32_t word(const volatile uint8_t *p)
{return ((const volatile sector_word *)p)->value;}
static void put(volatile uint8_t *p,uint32_t value)
{((volatile sector_word *)p)->value=value;}
extern uint32_t r1_fdb_native_get_status(const volatile uint8_t *,uint32_t);
/* Decode a complete sector header using the native field/status order. */
__attribute__((used,noinline)) static uint32_t sector_prepare_body(
 const volatile uint8_t *db,uint32_t address,volatile uint8_t *sector,
 volatile uint8_t *scratch)
{
 put(sector+4,address);
 uint32_t magic=word(scratch+12);put(sector+8,magic);
 if(magic!=UINT32_C(0x304c5354)){sector[0]=0;return 8;}
 sector[0]=1;
 sector[1]=(uint8_t)r1_fdb_native_get_status(scratch,4);
 put(sector+12,word(scratch+16));
 sector[24]=(uint8_t)r1_fdb_native_get_status(scratch+28,6);
 uint32_t second=(uint8_t)r1_fdb_native_get_status(scratch+56,6);
 sector[25]=(uint8_t)second;
 uint32_t first=sector[24];
 if(first==2){put(sector+16,word(scratch+20));put(sector+20,word(scratch+24));}
 else if(second==2){put(sector+16,word(scratch+48));put(sector+20,word(scratch+52));}
 else if(first==1 && second==1)return 1;
 uint32_t start=word(sector+4),cursor=start+80u;put(sector+32,cursor);
 uint32_t end=start+word(db+12);put(sector+36,end);put(sector+28,end-cursor);
 return 0;
}
__attribute__((used,noinline)) static uint32_t sector_advance_body(
 volatile uint8_t *sector,volatile uint8_t *scratch)
{
 put(sector+16,word(scratch+84));put(sector+20,word(scratch+92));
 put(sector+32,word(sector+32)+32u);
 uint32_t length=word(scratch+88),adjusted=length-((length+3u)&3u);
 put(sector+36,word(sector+36)-adjusted-3u);
 uint32_t cursor=word(scratch+92);length=word(scratch+88);
 put(scratch+92,cursor+32u);adjusted=length-((length+3u)&3u);
 uint32_t remaining=word(sector+28);
 if(adjusted+35u>=remaining)return 1;
 put(sector+28,remaining-adjusted-35u);return 0;
}

extern uint32_t r1_fdb_native_flash_read(const volatile uint8_t *,uint32_t,void *,uint32_t);
extern uint32_t r1_fdb_native_read_tsl(const volatile uint8_t *,volatile uint8_t *);
extern void *r1_fdb_native_db_path(const volatile uint8_t *);
extern int r1_native_printf(const char *,...);
const char r1_fdb_sector_function_name[] __attribute__((aligned(1),section(".r1.fdb.sector_function_name")))="read_sector_info";
static const char sector_prefix[]="[FlashDB][tsl]";
static const char sector_header[]="[%s][%s] ";
static const char sector_assert[]="(%s) has assert failed at %s.\n";
static const char sector_bounds[]="Error: this TSL (0x%08X) size (%u) is out of bound.\n";
static void sector_diagnostic(const volatile uint8_t *db)
{
 (void)r1_native_printf(sector_prefix);
 void *path=r1_fdb_native_db_path(db);
 (void)r1_native_printf(sector_header,word(db),path);
}
uint32_t r1_fdb_native_read_sector(const volatile uint8_t *db,uint32_t address,
 volatile uint8_t *sector,uint32_t traverse)
{
 if(!sector){sector_diagnostic(db);(void)r1_native_printf(sector_assert,"sector",r1_fdb_sector_function_name);for(;;){}}
 uint8_t scratch[104];for(uint32_t i=0;i<sizeof(scratch);i++)scratch[i]=UINT8_MAX;
 uint32_t error=r1_fdb_native_flash_read(db,address,scratch,80);
 if(error){sector[0]=0;return error;}
 uint32_t status=sector_prepare_body(db,address,sector,scratch);
 if(status==8)return 8;
 if(status==1){sector_diagnostic(db);(void)r1_native_printf(sector_assert,"0",r1_fdb_sector_function_name);for(;;){}}
 if(sector[1]!=2 || !traverse)return 0;
 put(scratch+92,word(sector+32));
 for(;;){
  error=r1_fdb_native_read_tsl(db,scratch+80);
  if(error){sector[0]=0;return error;}
  if(!scratch[80])return 0;
  if(sector_advance_body(sector,scratch)){
   sector_diagnostic(db);(void)r1_native_printf(sector_bounds,word(scratch+92),word(scratch+88));
   put(sector+28,0);return 2;
  }
 }
}
