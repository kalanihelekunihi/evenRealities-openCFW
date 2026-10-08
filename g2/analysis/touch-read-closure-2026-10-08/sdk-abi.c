#include "cy_em_eeprom.h"
#include <stddef.h>
const unsigned abi[]={sizeof(cy_stc_eeprom_context_t),offsetof(cy_stc_eeprom_context_t,secSize),offsetof(cy_stc_eeprom_context_t,eepromSize),offsetof(cy_stc_eeprom_context_t,bd),sizeof(mtb_block_storage_t),offsetof(mtb_block_storage_t,read),offsetof(mtb_block_storage_t,is_erase_required)};
