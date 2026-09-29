
undefined8 FUN_004917d2(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = file_heap_allocate(0x7160);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0xf4;
      FUN_0043d574(1,DAT_00491ee8,DAT_00491ee4,DAT_00491f04,0xf4,DAT_00491f00,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00491f08,DAT_00491f08);
    }
    iVar1 = 0;
  }
  else {
    FUN_00491752(iVar1,param_1);
  }
  return CONCAT44(param_2,iVar1);
}

