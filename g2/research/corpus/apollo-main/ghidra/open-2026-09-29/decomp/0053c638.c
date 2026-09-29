
undefined8 AUD_SendMessage(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = DAT_0053cd94;
  if ((param_1 != 0) && (*(int *)(DAT_0053cd94 + 0xc) != 0)) {
    iVar1 = osMessageQueuePut(*(undefined4 *)(DAT_0053cd94 + 0xc),param_1,0,0,param_2,param_3,
                              param_4);
    if (iVar1 == 0) {
      osThreadFlagsSet(*(undefined4 *)(iVar2 + 8),0x400000);
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x119;
        param_3 = DAT_0053cec4;
        FUN_0043d574(1,DAT_0053cd90,DAT_0053cd8c,DAT_0053cec8,0x119,DAT_0053cec4,iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0053cecc,DAT_0053cecc,iVar1);
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

