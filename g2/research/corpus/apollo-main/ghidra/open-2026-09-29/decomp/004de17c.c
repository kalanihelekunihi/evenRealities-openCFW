
undefined8 FUN_004de17c(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int *piVar2;
  
  if (param_1 == (int *)0x0) {
    iVar1 = FUN_0043d0ce();
    piVar2 = param_1;
    if (iVar1 << 0x1e < 0) {
      piVar2 = (int *)0x2e7;
      param_2 = DAT_004de33c;
      FUN_0043d574(2,DAT_004de348,DAT_004de344,DAT_004de340,0x2e7,DAT_004de33c,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004de34c,DAT_004de34c);
    }
  }
  else {
    piVar2 = param_1;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      piVar2 = (int *)0x2eb;
      param_2 = DAT_004de350;
      FUN_0043d574(4,DAT_004de348,DAT_004de344,DAT_004de340,0x2eb,DAT_004de350,param_1[0x16]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004dedc4,DAT_004dedc4,param_1[0x16]);
    }
    if (*param_1 != 0) {
      FUN_0044d7b8(*param_1);
      *param_1 = 0;
    }
    for (iVar1 = 0; iVar1 < 0x14; iVar1 = iVar1 + 1) {
      param_1[iVar1 + 2] = 0;
    }
    param_1[1] = 0;
    if (param_1[0x15c] != 0) {
      ui_common_api_fn_00509f52(param_1[0x15c]);
      ui_common_api_fn_00509c96(param_1[0x15c]);
      param_1[0x15c] = 0;
    }
    file_heap_free(param_1);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      piVar2 = (int *)0x303;
      param_2 = DAT_004dedc8;
      FUN_0043d574(3,DAT_004de348,DAT_004de344,DAT_004de340);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_004dedcc,DAT_004dedcc);
    }
  }
  return CONCAT44(param_2,piVar2);
}

