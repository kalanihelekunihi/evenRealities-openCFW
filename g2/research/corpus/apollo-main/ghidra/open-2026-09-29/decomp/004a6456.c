
int DRV_IMUReadWhoAmI(uint *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  byte local_14 [4];
  undefined4 uStack_10;
  
  if (param_1 == (uint *)0x0) {
    iVar1 = -1;
  }
  else {
    local_14[0] = 0;
    uStack_10 = param_4;
    iVar1 = FUN_00505fbe(DAT_004a6614,local_14);
    if (iVar1 == 0) {
      *param_1 = (uint)local_14[0];
      iVar1 = 0;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004a65e8,DAT_004a65e4,DAT_004a661c,0x6a8,DAT_004a6618,iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_004a6620,DAT_004a6620,iVar1);
      }
    }
  }
  return iVar1;
}

