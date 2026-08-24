#include <stddef.h>
#include <stdint.h>

void *open_cfw_test_callback_alloc(size_t size);
void open_cfw_test_callback_free(void *allocation);

#define OPEN_CFW_CALLBACK_MGR_ALLOC(size) \
    open_cfw_test_callback_alloc((size_t)(size))
#define OPEN_CFW_CALLBACK_MGR_FREE(allocation) \
    open_cfw_test_callback_free((allocation))
