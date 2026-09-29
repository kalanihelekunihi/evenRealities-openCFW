
undefined8 ui_common_api_fn_00509c1c(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = file_heap_allocate(0x206);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0x1d;
      FUN_0043d574(2,DAT_00509fa4,DAT_00509fa0,DAT_00509f9c,0x1d,DAT_00509f98);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00509fa8,DAT_00509fa8);
    }
    iVar1 = 0;
  }
  else {
    FUN_0043c0e4(iVar1,0x206,0);
    *(undefined2 *)(iVar1 + 0x200) = 0;
    *(undefined2 *)(iVar1 + 0x202) = 0;
    *(undefined2 *)(iVar1 + 0x204) = 0;
  }
  return CONCAT44(param_3,iVar1);
}

