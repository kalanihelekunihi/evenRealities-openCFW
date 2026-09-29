
void FUN_0050c1c0(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  int local_70;
  undefined4 local_6c;
  undefined4 local_60;
  undefined4 local_50;
  undefined4 local_40;
  
  if (param_1 != 0) {
    iVar1 = FUN_0043e2ea(param_1);
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_6c = DAT_0050c990;
        local_70 = 0x83d;
        FUN_0043d574(2,DAT_0050c2fc,DAT_0050c2f8,DAT_0050c994);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0050c998);
      }
    }
    else {
      *DAT_0050c960 = 1;
      *DAT_0050c964 = param_1;
      FUN_004503d6(&local_70);
      local_70 = param_1;
      uVar2 = FUN_0044e498(param_1);
      FUN_004506ce(&local_70,uVar2,param_2);
      local_6c = DAT_0050c99c;
      local_50 = DAT_0050c9a0;
      local_60 = DAT_0050c9a4;
      *DAT_0050c27c = 1;
      local_40 = param_3;
      FUN_00450408(&local_70);
    }
  }
  return;
}

