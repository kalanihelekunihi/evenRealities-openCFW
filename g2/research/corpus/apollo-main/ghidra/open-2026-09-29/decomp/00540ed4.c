
undefined8 _flashDBRead(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = param_3;
  iVar1 = FUN_004709c8(param_1,param_2,param_3,param_4,param_3,param_4);
  if (iVar1 != 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = 0x4b;
      FUN_0043d574(1,DAT_00541268,DAT_00541264,DAT_00541260,0x4b,DAT_0054125c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__db_api_read_failed_0054126c);
    }
    param_3 = 0;
  }
  return CONCAT44(uVar2,param_3);
}

