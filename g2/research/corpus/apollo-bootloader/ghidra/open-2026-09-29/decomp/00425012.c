
longlong device_configure_init_call(void)

{
  int unaff_r4;
  int unaff_r5;
  uint in_stack_00000000;
  
  mspi_device_configure();
  *(undefined1 *)(unaff_r5 + 0xd) = 0;
  *(undefined1 *)(unaff_r5 + 0xc) = *(undefined1 *)(unaff_r4 + 0xb);
  *(undefined4 *)(unaff_r5 + 0x10) = 10000;
  mspi_get_xip_off_min_delay();
  return (ulonglong)in_stack_00000000 << 0x20;
}

