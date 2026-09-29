
undefined4 silent_mode_common_data_handler(int param_1,char *param_2,int param_3)

{
  char cVar1;
  char cVar2;
  int iVar3;
  
  if (((param_1 == 4) && (param_2 != (char *)0x0)) && (param_3 != 0)) {
    cVar1 = *param_2;
    cVar2 = silent_mode_status_get();
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00469b3c,DAT_00469b38,DAT_00469b80,0xbd,DAT_00469b7c,cVar2,cVar1,
                   *DAT_00469b54);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_00469b84,DAT_00469b84,cVar2,cVar1,*DAT_00469b54);
    }
    if ((cVar1 == '\x01') && (cVar2 == '\0')) {
      *DAT_00469b88 = 1;
      notify_silent_mode_to_app(1);
    }
    else {
      if (cVar1 != '\0') {
        return 0;
      }
      if (cVar2 != '\x01') {
        return 0;
      }
      *DAT_00469b88 = 0;
      SilentMode_SetStatus(0);
    }
    iVar3 = FUN_0045a568();
    if (iVar3 == 1) {
      FUN_0045a8ee(0x10a,0,0,500);
    }
  }
  return 0;
}

