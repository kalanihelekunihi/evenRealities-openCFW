
undefined4 gx8002_snpu_initialize(void)

{
  undefined4 *puVar1;
  
  puVar1 = DAT_10205d34;
  gx8002_snpu_device_init(0);
  puVar1[0x171] = 0;
  puVar1[0x172] = 0;
  puVar1[0x173] = DAT_10205d38;
  puVar1[0x16d] = 0;
  puVar1[0x16c] = 0;
  gx8002_snpu_tcb_init();
  gx8002_snpu_request_irq(PTR_gx8002_snpu_isr_10205d3c,0);
  *puVar1 = 2;
  return 0;
}

