
longlong platform_boot_sequence_4301d6(void)

{
  uint unaff_r7;
  
  descriptor_register_430280(PTR_DAT_0043023c,0x61);
  mode_one_apply_42fff2();
  platform_bringup_430000();
  func_0x0041f612();
  platform_finish_430502();
  return (ulonglong)unaff_r7 << 0x20;
}

