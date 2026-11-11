#include <stdint.h>
/* Native FlashDB control, 0x63694. Preserve whole-byte initialization tests,
 * callback-pointer words, and the native R0 result on each returning route. */
typedef struct __attribute__((packed,may_alias)) { uint32_t value; } r1_control_word;
static uint32_t word(const volatile uint8_t *p)
{ return ((const volatile r1_control_word *)p)->value; }
static void put(volatile uint8_t *p,uint32_t v)
{ ((volatile r1_control_word *)p)->value=v; }
extern void *r1_fdb_native_db_path(const volatile uint8_t *);
extern int r1_native_printf(const char *,...);
extern const char r1_fdb_control_function_name[],r1_fdb_control_filemode_error[];
static void prefix(const volatile uint8_t *db)
{
    (void)r1_native_printf("[FlashDB][tsl]");
    void *path=r1_fdb_native_db_path(db);
    (void)r1_native_printf("[%s][%s] ",(const char *)(uintptr_t)word(db),path);
}
__attribute__((noinline)) static void failed(const volatile uint8_t *db,const char *condition)
{
    prefix(db);
    (void)r1_native_printf("(%s) has assert failed at %s.\n",condition,r1_fdb_control_function_name);
    for (;;) {}
}
uint32_t r1_health_sync_provider_00063694(volatile uint8_t *db,uint32_t command,
                                        volatile uint8_t *argument)
{
    if (!db) failed(db,"db");
    uint32_t value;
    switch (command) {
    case 0:
        if (db[24]) failed(db,"db->parent.init_ok == false");
        value=word(argument);put(db+12,value);return value;
    case 1:
        value=word(db+12);put(argument,value);return value;
    case 2: put(db+28,(uint32_t)(uintptr_t)argument);return (uint32_t)(uintptr_t)db;
    case 3: put(db+32,(uint32_t)(uintptr_t)argument);return (uint32_t)(uintptr_t)db;
    case 4:
        if (db[24]!=1) failed(db,"db->parent.init_ok == true");
        value=argument[0];db[92]=(uint8_t)value;return value;
    case 5:
        value=db[92];argument[0]=(uint8_t)value;return value;
    case 6:
        value=word(db+80);put(argument,value);return value;
    case 9:
        prefix(db);return (uint32_t)r1_native_printf(r1_fdb_control_filemode_error);
    case 11:
        if (db[24]) failed(db,"db->parent.init_ok == false");
        value=argument[0];db[26]=(uint8_t)value;return value;
    default: return (uint32_t)(uintptr_t)db;
    }
}
const char r1_fdb_control_function_name[] __attribute__((aligned(1),section(".r1.fdb.control_name")))="fdb_tsdb_control";
const char r1_fdb_control_filemode_error[] __attribute__((aligned(1),section(".r1.fdb.control_filemode_error")))="Error: set file mode Failed. Please defined the FDB_USING_FILE_MODE macro.";
