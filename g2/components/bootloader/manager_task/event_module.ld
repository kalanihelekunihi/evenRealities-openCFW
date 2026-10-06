ENTRY(opencfw_provider_42e53c)
PHDRS { source_text PT_LOAD FLAGS(5); queue_name PT_LOAD FLAGS(4); mutex_name PT_LOAD FLAGS(4); thread_name PT_LOAD FLAGS(4); }
opencfw_boot_event_runtime_init = opencfw_provider_42e53c;
opencfw_provider_416816 = 0x416817;
opencfw_provider_4163b2 = 0x4163b3;
opencfw_provider_416610 = 0x416611;
opencfw_provider_416200 = 0x416201;
opencfw_provider_4160fe = 0x4160ff;
opencfw_provider_4176ce = 0x4176cf;
SECTIONS {
 . = 0x10000; .text : { *(.text*) *(.rodata*) } :source_text
 .event_queue_name 0x433b3c : { KEEP(*(.event_queue_name)) } :queue_name
 .event_mutex_name 0x433b50 : { KEEP(*(.event_mutex_name)) } :mutex_name
 .event_thread_name 0x433f68 : { KEEP(*(.event_thread_name)) } :thread_name
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
