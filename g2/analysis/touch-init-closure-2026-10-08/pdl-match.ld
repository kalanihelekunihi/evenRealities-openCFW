__aeabi_uidivmod = 0xa7cd; memcpy = 0xaa2d; memset = 0xa9d5; Cy_Flash_WriteRow = 0x8d51;
SECTIONS {
 .match_read_size 0x4780 : { *(.text.mtb_block_storage_pdl_read_size) }
 .match_program_size 0x4784 : { *(.text.mtb_block_storage_pdl_program_size) }
 .match_erase_size 0x4788 : { *(.text.mtb_block_storage_pdl_erase_size) }
 .match_erase_value 0x478c : { *(.text.mtb_block_storage_pdl_erase_value) }
 .match_is_in_range 0x4790 : { *(.text.mtb_block_storage_pdl_is_in_range) }
 .match_is_erase_required 0x47aa : { *(.text.mtb_block_storage_pdl_is_erase_required) }
 .match_erase 0x47b0 : { *(.text.mtb_block_storage_pdl_erase) }
 .match_program 0x4810 : { *(.text.mtb_block_storage_pdl_program) }
 .match_read 0x4860 : { *(.text.mtb_block_storage_pdl_read) }
 .match_create 0x486c : { *(.text.mtb_block_storage_create_pdl) }
 /DISCARD/ : { *(*) }
}
