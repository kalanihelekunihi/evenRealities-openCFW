
undefined4 FUN_004ff7dc(undefined4 param_1,undefined1 param_2,int param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_60;
  undefined4 local_5c;
  undefined1 auStack_58 [72];
  
  if (param_3 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_5c = DAT_004ff8c8;
      local_60 = 0x717;
      FUN_0043d574(1,DAT_004ff8a8,DAT_004ff8a4,DAT_004ff8cc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ff8d0,DAT_004ff8d0);
    }
    uVar2 = 1;
  }
  else {
    FUN_0048949c(&local_60,0x50);
    local_5c._0_2_ = CONCAT11(3,param_2);
    local_60 = param_1;
    FUN_00439c04(auStack_58,param_3,0x40);
    uVar2 = FUN_004ff09c(&local_60);
  }
  return uVar2;
}

