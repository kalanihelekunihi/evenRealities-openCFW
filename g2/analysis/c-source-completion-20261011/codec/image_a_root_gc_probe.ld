/* Source-root GC eligibility probe; no final placement or firmware image. */
SECTIONS {
 .gx8002_gc_xip_code : { KEEP(*(.text.gx8002_xip_*)) }
 .gx8002_gc_xip_data : { KEEP(*(.rodata.gx8002_xip_*)) KEEP(*(.gx8002.sample_name.*)) KEEP(*(.gx8002.flash_name.*)) KEEP(*(.gx8002.xip.*)) }
 .gx8002_gc_resident_code : { KEEP(*(.text.gx8002_resident_*)) KEEP(*(.rodata.gx8002_resident_*)) KEEP(*(.text)) }
 .gx8002_gc_native_tables : { KEEP(*(.gx8002.*)) }
}
