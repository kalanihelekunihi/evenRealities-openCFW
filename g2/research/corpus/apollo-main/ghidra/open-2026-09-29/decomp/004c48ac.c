
undefined8 _bleRingReceiveData(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  local_10 = param_3;
  local_c = param_4;
  if (*(char *)(param_1 + 3) == '\0') {
    if (*(short *)(param_1 + 10) == *(short *)(*(int *)(DAT_004c4c68 + 4) + 2)) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_004c4ca4;
        local_10 = 0xcc;
        FUN_0043d574(3,DAT_004c4c78,DAT_004c4c74,DAT_004c4ca8);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004c4cac,DAT_004c4cac);
      }
      Thread_SendMsgToRingTaskWithId(*(undefined4 *)(param_1 + 4),*(undefined2 *)(param_1 + 8));
    }
  }
  return CONCAT44(local_c,local_10);
}

