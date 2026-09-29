
undefined8 FUN_005122ec(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  
  pcVar1 = (char *)FUN_0050938e(1);
  iVar2 = FUN_0055fa0e(DAT_00512384,0);
  if (iVar2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x399;
      param_3 = DAT_00512a68;
      FUN_0043d574(1,DAT_00512408,DAT_00512404,DAT_00512a6c,0x399,DAT_00512a68,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__npmx_driver_p_buck1_is_null__00512bb4,
                          PTR_s__npmx_driver_p_buck1_is_null__00512bb4);
    }
  }
  else {
    FUN_0055fa40(iVar2,1);
    if (*pcVar1 == '\x06') {
      FUN_0055fa22(iVar2,8);
    }
    else {
      FUN_0055fa22(iVar2,1);
    }
    FUN_0055fa18(iVar2,0);
  }
  return CONCAT44(param_3,param_2);
}

