
undefined4 gx8002_app_suspend(void)

{
  int iVar1;
  
  gx8002_watchdog_stop();
  iVar1 = *DAT_10208cbc;
  if ((iVar1 != 0) && (*(uint *)(iVar1 + 0x10) != 0)) {
    (*(code *)(*(uint *)(iVar1 + 0x10) & 0xfffffffe))(*(undefined4 *)(iVar1 + 0x14));
  }
  return 0;
}

