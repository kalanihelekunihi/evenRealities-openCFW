#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdio.h>
#include <time.h>
#include "fdb_cfg.h"
#include "fdb_def.h"
typedef char blob_size[(sizeof(struct fdb_blob)==20)?1:-1];
typedef char saved_len_offset[(offsetof(struct fdb_blob,saved.len)==16)?1:-1];
typedef char kvdb_stride[(sizeof(struct fdb_kvdb)==0x8ac)?1:-1];
