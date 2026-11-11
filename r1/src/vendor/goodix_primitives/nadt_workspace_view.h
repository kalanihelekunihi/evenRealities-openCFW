#ifndef OPENR1_GOODIX_NADT_WORKSPACE_VIEW_H
#define OPENR1_GOODIX_NADT_WORKSPACE_VIEW_H
#include <stddef.h>
#include <stdint.h>

/* Non-owning four-bank view shared by the typed core and the native owner. */
typedef struct {
    int32_t *primary_raw;
    int32_t *primary_filtered;
    int16_t *configuration_markers;
    int16_t *secondary_history;
    size_t primary_capacity;
    size_t secondary_capacity;
} goodix_primitives_nadt_stream_workspace_view;

#endif
