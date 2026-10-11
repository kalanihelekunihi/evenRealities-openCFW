case_vector_pendsv_0102 = 0x08000103;
case_vector_systick_8420 = 0x08008421;
case_vector_irq_3bc8 = 0x08003bc9;
case_vector_irq_3c2c = 0x08003c2d;
case_vector_irq_3d24 = 0x08003d25;
case_irq_child_4330 = 0x08004331;
case_irq_child_5a52 = 0x08005a53;
case_irq_child_5c90 = 0x08005c91;
case_irq_child_5f50 = 0x08005f51;
case_crt_initial_data = 0x0800d95c;
case_application_entry_a598 = 0x0800a599;
SECTIONS { . = 0x08000000; .isr_vector : { *(.isr_vector) } . = 0x08001000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
