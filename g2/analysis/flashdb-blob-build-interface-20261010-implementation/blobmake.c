#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdio.h>
#include <time.h>
#include "fdb_cfg.h"
#include "fdb_def.h"
fdb_blob_t fdb_blob_make(fdb_blob_t blob, const void *value_buf, size_t buf_len)
{
    blob->buf = (void *)value_buf;
    blob->size = buf_len;

    return blob;
}
