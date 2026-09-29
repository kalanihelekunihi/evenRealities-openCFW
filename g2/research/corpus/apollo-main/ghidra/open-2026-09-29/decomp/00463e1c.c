
undefined8 FUN_00463e1c(int *param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  local_10 = param_3;
  local_c = param_4;
  if (param_1 == (int *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = DAT_004642c0;
      local_10 = 0x51;
      FUN_0043d574(1,DAT_004642cc,DAT_004642c8,DAT_004642e4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004642d0,DAT_004642d0);
    }
  }
  else {
    if (param_2 == '\x01') {
      if ((*param_1 != 0) && (iVar1 = FUN_0043e2ea(*param_1), iVar1 != 0)) {
        FUN_0044d7b8(*param_1);
      }
      *param_1 = 0;
    }
    param_1[1] = 0;
    param_1[2] = 0;
    file_heap_free(param_1);
  }
  return CONCAT44(local_c,local_10);
}

