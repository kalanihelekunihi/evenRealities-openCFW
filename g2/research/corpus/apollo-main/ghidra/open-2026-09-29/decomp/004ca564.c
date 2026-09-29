
undefined8
uled_QSPI_PartialReflash_async
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
          undefined4 param_5)

{
  int iVar1;
  undefined4 uVar2;
  
  if (*DAT_004ca664 == 0) {
    iVar1 = FUN_0043d0ce();
    param_5 = param_2;
    if (iVar1 << 0x1e < 0) {
      param_5 = 0x157;
      FUN_0043d574(1,DAT_004ca674,DAT_004ca670,DAT_004ca6ec,0x157,DAT_004ca668,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ca678,DAT_004ca678);
    }
    uVar2 = 0xffffffff;
  }
  else {
    uVar2 = (**(code **)(*DAT_004ca664 + 0x28))();
  }
  return CONCAT44(param_5,uVar2);
}

