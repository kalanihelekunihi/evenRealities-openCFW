#include <stdint.h>
#include <stdbool.h>
struct fdb_tsdb;struct fdb_tsl;
/* Native traversal leaves, 0x6a158..0x6a1cb. Each field load remains ordered
 * and conditional; arithmetic and comparisons use the native unsigned words. */
typedef struct __attribute__((packed,may_alias)) { uint32_t value; } r1_fdb_iterator_word;
static uint32_t word(const volatile uint8_t *p)
{ return ((const volatile r1_fdb_iterator_word *)p)->value; }

extern uint32_t r1_fdb_native_read_sector(const volatile uint8_t *,uint32_t,volatile uint8_t *,uint32_t);
extern uint32_t r1_fdb_native_read_tsl(const volatile uint8_t *,volatile uint8_t *);
extern void *r1_native_memory_move(void *,const void *,uint32_t);
extern void *r1_fdb_native_db_path(const volatile uint8_t *);
extern int r1_native_printf(const char *,...);
uint32_t r1_fdb_native_last_sector(const volatile uint8_t *,const volatile uint8_t *,uint32_t);
uint32_t r1_fdb_native_next_sector(const volatile uint8_t *,const volatile uint8_t *,uint32_t);
uint32_t r1_fdb_native_last_tsl(const volatile uint8_t *,const volatile uint8_t *);
uint32_t r1_fdb_native_next_tsl(const volatile uint8_t *,const volatile uint8_t *);
static void put(volatile uint8_t *p,uint32_t value)
{((volatile r1_fdb_iterator_word *)p)->value=value;}
/* Stock0x63ad8 search/traversal, retaining signed time/address comparisons.
 * Failed TSL reads leave through the live unlock callback before decoding. */
void r1_health_sync_provider_00063ad8(struct fdb_tsdb *database,int32_t from,int32_t to,
 bool (*callback)(struct fdb_tsl *,void *),void *argument)
{
 const volatile uint8_t *db=(const volatile uint8_t *)database;
 uint8_t sector[40]={0},entry[20]={0},probe[20]={0};
 uint32_t traversed=0;bool started=false;
 if(!db[24]){
  (void)r1_native_printf("[FlashDB][tsl]");
  void *path=r1_fdb_native_db_path(db);
  (void)r1_native_printf("[%s][%s] ",word(db),path);
  (void)r1_native_printf("Error: TSL (%s) isn't initialize OK.\n",word(db));
 }
 uint32_t start=word(db+(from<=to?20:44)),address=start;
 uint32_t (*next_sector)(const volatile uint8_t *,const volatile uint8_t *,uint32_t)=
  from<=to?r1_fdb_native_next_sector:r1_fdb_native_last_sector;
 uint32_t (*next_entry)(const volatile uint8_t *,const volatile uint8_t *)=
  from<=to?r1_fdb_native_next_tsl:r1_fdb_native_last_tsl;
 if(!callback)return;
 uintptr_t lock=word(db+28);if(lock)((void (*)(const volatile uint8_t *))lock)(db);
 for(;;){
  traversed+=word(db+12);
  /* Define the fallback cursor even if a sector read cannot populate it. */
  put(sector+4,address);
  if(r1_fdb_native_read_sector(db,address,sector,0))goto next_sector;
  if(sector[1]==2)(void)r1_native_memory_move(sector,(const void *)(uintptr_t)(db+40),40);
  else if(sector[1]!=3){if(sector[1]==1)break;goto next_sector;}
  if(!started){
   if(from<=to){
    if(!(address==start && (int32_t)word(sector+12)>=from) && (int32_t)word(sector+16)<from)goto next_sector;
   }else if(!(address==start && (int32_t)word(sector+16)<=from) && (int32_t)word(sector+12)>from)goto next_sector;
  }
  started=true;
  uint32_t low=word(sector+4)+80u,high=word(sector+20);bool exact=false;
  for(;;){
   int32_t half=(int32_t)(high-low)/2;
   uint32_t middle=low+(uint32_t)half-((31u+(uint32_t)half)&31u)+31u;
   put(probe+12,middle);
   if(r1_fdb_native_read_tsl(db,probe))goto unlock;
   int32_t time=(int32_t)word(probe+4);
   if(time<from)low=word(probe+12)+32u;
   else if(time>from)high=word(probe+12)-32u;
   else{low=word(probe+12);exact=true;break;}
   if((int32_t)low>(int32_t)high)break;
  }
  if(from>to && !exact){
   put(probe+12,low);
   if(r1_fdb_native_read_tsl(db,probe))goto unlock;
   if((int32_t)word(probe+4)>from)low-=32u;
  }
  put(entry+12,low);
  for(;;){
   if(r1_fdb_native_read_tsl(db,entry))goto unlock;
   if(entry[0]){
    int32_t time=(int32_t)word(entry+4);
    if(from<=to){if(time<from || time>to)goto unlock;}
    else if(time>from || time<to)goto unlock;
    if(callback((struct fdb_tsl *)entry,argument))goto unlock;
   }
   uint32_t next=next_entry(sector,entry);put(entry+12,next);
   if(next==UINT32_MAX)break;
  }
 next_sector:
  address=next_sector(db,sector,traversed);
  if(address==UINT32_MAX)break;
 }
 unlock:;
 uintptr_t release=word(db+32);if(release)((void (*)(const volatile uint8_t *))release)(db);
}
uint32_t r1_fdb_native_last_sector(const volatile uint8_t *db,
                                  const volatile uint8_t *sector,uint32_t traversed)
{
    uint32_t size=word(db+12),limit=word(db+16);
    if (traversed+size>limit) return UINT32_MAX;
    uint32_t address=word(sector+4);
    return address>=size ? address-size : limit-size;
}
uint32_t r1_fdb_native_last_tsl(const volatile uint8_t *sector,
                               const volatile uint8_t *entry)
{
    if (sector[1]==1) return UINT32_MAX;
    uint32_t address=word(entry+12);
    uint32_t first=word(sector+4)+112u;
    return address<first ? UINT32_MAX : address-32u;
}
uint32_t r1_fdb_native_next_sector(const volatile uint8_t *db,
                                  const volatile uint8_t *sector,uint32_t traversed)
{
    uint32_t size=word(db+12);
    uint32_t advanced=traversed+size;
    uint32_t limit=word(db+16);
    if (advanced>limit) return UINT32_MAX;
    uint32_t next=word(sector+4)+size;
    return next<limit ? next : 0u;
}
uint32_t r1_fdb_native_next_tsl(const volatile uint8_t *sector,
                               const volatile uint8_t *entry)
{
    if (sector[1]==1) return UINT32_MAX;
    uint32_t address=word(entry+12);
    uint32_t last=word(sector+20);
    uint32_t next=address+32u;
    return next<=last ? next : UINT32_MAX;
}
