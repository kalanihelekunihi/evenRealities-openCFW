
undefined8 als_function_11(uint param_1,undefined4 param_2,undefined4 param_3)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_004ae4e4;
  if (param_1 < 0xb) {
    if ((*DAT_004ae4e4 == 0) && (iVar2 = als_function_07(), iVar2 != 0)) {
      *piVar1 = 1;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0xd2;
        param_3 = DAT_004ae4f4;
        FUN_0043d574(3,DAT_004ae4dc,DAT_004ae4d8,DAT_004ae4ec,0xd2,DAT_004ae4f4,0xf);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_004ae6c4,DAT_004ae6c4,0xf);
      }
    }
    if (*piVar1 == 1) {
      *DAT_004ae6c8 = 0;
      *DAT_004ae6cc = 0xf;
      *DAT_004ae8d4 = 0xf;
    }
    else {
      als_function_19(param_1);
    }
  }
  else {
    if (*DAT_004ae4e4 == 1) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0xc9;
        param_3 = DAT_004ae4e8;
        FUN_0043d574(3,DAT_004ae4dc,DAT_004ae4d8,DAT_004ae4ec,0xc9,DAT_004ae4e8,param_1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_004ae4f0,DAT_004ae4f0,param_1);
      }
    }
    *piVar1 = 0;
    als_function_19(param_1);
  }
  return CONCAT44(param_3,param_2);
}

