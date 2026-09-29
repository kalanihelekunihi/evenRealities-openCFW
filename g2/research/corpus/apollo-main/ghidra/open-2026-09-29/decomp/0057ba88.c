
int gx8002_host_init(void)

{
  int iVar1;
  int iVar2;
  undefined4 in_r3;
  
  iVar1 = uart_init();
  if (iVar1 == 0) {
    FUN_0058fab6(0x1c200);
    iVar1 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0057c61c,DAT_0057c618,DAT_0057c614,0x2d,DAT_0057c610,iVar1,in_r3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0057c620,DAT_0057c620,iVar1);
    }
  }
  return iVar1;
}

