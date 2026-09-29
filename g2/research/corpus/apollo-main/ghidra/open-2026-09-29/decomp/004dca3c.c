
undefined8 FUN_004dca3c(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int *piVar2;
  
  if (param_1 == (int *)0x0) {
    iVar1 = FUN_0043d0ce();
    piVar2 = param_1;
    if (iVar1 << 0x1e < 0) {
      piVar2 = (int *)0x15e;
      param_2 = DAT_004dcc4c;
      FUN_0043d574(2,DAT_004dcc58,DAT_004dcc54,DAT_004dcc50,0x15e,DAT_004dcc4c,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004dcc5c,DAT_004dcc5c);
    }
  }
  else {
    piVar2 = param_1;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      piVar2 = (int *)0x162;
      param_2 = DAT_004dcc60;
      FUN_0043d574(4,DAT_004dcc58,DAT_004dcc54,DAT_004dcc50,0x162,DAT_004dcc60,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004dcc64,DAT_004dcc64,param_1);
    }
    if (*param_1 != 0) {
      FUN_0044d7b8(*param_1);
      *param_1 = 0;
      param_1[1] = 0;
    }
    if (param_1[3] != 0) {
      file_heap_free(param_1[3]);
      param_1[3] = 0;
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        piVar2 = (int *)0x16f;
        param_2 = DAT_004dcc68;
        FUN_0043d574(4,DAT_004dcc58,DAT_004dcc54,DAT_004dcc50);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004dcc6c,DAT_004dcc6c);
      }
    }
    if (param_1[2] != 0) {
      file_heap_free(param_1[2]);
      param_1[2] = 0;
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        piVar2 = (int *)0x176;
        param_2 = DAT_004dcc70;
        FUN_0043d574(4,DAT_004dcc58,DAT_004dcc54,DAT_004dcc50);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004dcc74,DAT_004dcc74);
      }
    }
    file_heap_free(param_1);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      piVar2 = (int *)0x17b;
      param_2 = DAT_004dcc78;
      FUN_0043d574(4,DAT_004dcc58,DAT_004dcc54,DAT_004dcc50);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004dcc7c,DAT_004dcc7c);
    }
  }
  return CONCAT44(param_2,piVar2);
}

