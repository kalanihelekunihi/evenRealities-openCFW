
undefined8 FUN_005118e8(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  uVar1 = FUN_0055ef6c(DAT_00511984,0);
  iVar2 = FUN_0055ef76(uVar1,3);
  if (iVar2 != DAT_00511964) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0x242;
      param_2 = DAT_005122e4;
      FUN_0043d574(1,DAT_00511958,DAT_00511954,DAT_005122e8,0x242,DAT_005122e4,iVar2,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__npmx_driver_ERROR_kick_npmx_wat_005124f0,
                          PTR_s__npmx_driver_ERROR_kick_npmx_wat_005124f0,iVar2);
    }
  }
  return CONCAT44(param_2,param_1);
}

