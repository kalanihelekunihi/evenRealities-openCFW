
undefined8
device_mgr_fn_004c659a(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  
  if ((((param_1 != 0) && (*(int *)(DAT_004c6c08 + 0xc) != 0)) &&
      (iVar2 = osMessageQueuePut(*(undefined4 *)(DAT_004c6c08 + 0xc),param_1,0,0,param_2,param_3,
                                 param_4), pcVar1 = DAT_004c6c64, iVar2 != 0)) &&
     (*DAT_004c6c64 = *DAT_004c6c64 + '\x01', *pcVar1 != '\0')) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x10c;
      param_3 = DAT_004c6c68;
      FUN_0043d574(2,DAT_004c6c00,DAT_004c6bfc,DAT_004c6c6c,0x10c,DAT_004c6c68,iVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_004c6c70,DAT_004c6c70,iVar2);
    }
    *pcVar1 = '\0';
  }
  return CONCAT44(param_3,param_2);
}

