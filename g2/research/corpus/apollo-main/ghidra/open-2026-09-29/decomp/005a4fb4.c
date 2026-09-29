
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong atBleKeepConnectHandler(void)

{
  uint unaff_r7;
  
  slave_adv_stop_flag_or_0046f2dc(1);
  at_core_output(_DAT_005a4fcc);
  return (ulonglong)unaff_r7 << 0x20;
}

