#include <stddef.h>
#define FDB_KV_NAME_ERR 5
void diagnostic(void);
#define FDB_INFO(...) diagnostic()
size_t strlen(const char*s){const char*p=s;while(*p)p++;return p-s;}
int name_guard(const char*key){
    if (strlen(key) > FDB_KV_NAME_MAX) {
        FDB_INFO("Error: The KV name length is more than %d\n", FDB_KV_NAME_MAX);
        return FDB_KV_NAME_ERR;
    }

return 0;
}
