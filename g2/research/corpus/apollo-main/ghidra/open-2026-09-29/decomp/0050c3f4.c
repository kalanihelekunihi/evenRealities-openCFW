
undefined8 FUN_0050c3f4(int param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = param_2;
  if (param_1 != 0) {
    iVar1 = FUN_0043e2ea(param_1);
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_3 = 0x8c9;
        FUN_0043d574(2,DAT_0050c9c8,DAT_0050c9c4,DAT_0050c9d4,0x8c9,DAT_0050c9d0);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0050c9d8);
      }
    }
    else {
      iVar1 = FUN_0044e498(param_1);
      iVar2 = FUN_0044e4bc(param_1);
      if (param_2 < 0) {
        iVar3 = 0;
      }
      else {
        iVar3 = iVar2 + iVar1;
        if (param_2 <= iVar2 + iVar1) {
          iVar3 = param_2;
        }
      }
    }
  }
  return CONCAT44(param_3,iVar3);
}

