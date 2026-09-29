
undefined8
_flashDBWrite(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = param_3;
  iVar1 = FUN_004708a8(param_1,param_2,param_3,param_4,param_3,param_4);
  if (iVar1 != 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = 0x55;
      FUN_0043d574(1,DAT_00541268,DAT_00541264,PTR_s__flashDBWrite_00541274,0x55,
                   PTR_s_write_failed_00541270);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__db_api_write_failed_00541278);
    }
    param_3 = 0;
  }
  return CONCAT44(uVar2,param_3);
}

