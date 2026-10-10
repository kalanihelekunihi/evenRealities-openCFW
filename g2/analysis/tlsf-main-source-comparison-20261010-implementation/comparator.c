#include "tlsf.c"
typedef char target_control_size[(sizeof(control_t)==0xc74)?1:-1];
typedef char target_pointer_size[(sizeof(void*)==4)?1:-1];
typedef char target_rows[(FL_INDEX_COUNT==24 && SL_INDEX_COUNT==32)?1:-1];
