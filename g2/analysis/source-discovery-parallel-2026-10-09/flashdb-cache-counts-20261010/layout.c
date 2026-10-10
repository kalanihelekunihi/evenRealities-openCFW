#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include "fdb_cfg.h"
#include "fdb_def.h"
const unsigned evidence[]={sizeof(struct fdb_kvdb),offsetof(struct fdb_kvdb,kv_cache_table),offsetof(struct fdb_kvdb,sector_cache_table),sizeof(struct kv_cache_node),sizeof(struct kvdb_sec_info),offsetof(struct kv_cache_node,addr),offsetof(struct kvdb_sec_info,addr),offsetof(struct fdb_kvdb,user_data)};
