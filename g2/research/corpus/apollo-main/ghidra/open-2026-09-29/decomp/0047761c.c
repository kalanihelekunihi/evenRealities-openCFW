
undefined8 _connectParamReq(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined2 *puVar3;
  
  iVar1 = FUN_004b8122();
  if ((iVar1 == 0) || (*(char *)(iVar1 + 0x56) == '\0')) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x120;
      param_3 = DAT_0047814c;
      FUN_0043d574(1,DAT_00477ad8,DAT_00477ad4,DAT_00478150,0x120,DAT_0047814c,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00478154,DAT_00478154);
    }
  }
  else {
    iVar2 = dmGetConnParamPtr();
    if (iVar2 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_2 = 0x125;
        param_3 = DAT_00478158;
        FUN_0043d574(2,DAT_00477ad8,DAT_00477ad4,DAT_00478150,0x125,DAT_00478158,param_4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0047815c,DAT_0047815c);
      }
    }
    else {
      iVar2 = settings_get_terminal_mode();
      if ((iVar2 == 1) && (param_1 == 0xa4)) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_2 = 0x12a;
          param_3 = DAT_004781f0;
          FUN_0043d574(2,DAT_00477ad8,DAT_00477ad4,DAT_00478150,0x12a,DAT_004781f0,param_4);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_00478270,DAT_00478270);
        }
      }
      else {
        puVar3 = (undefined2 *)WsfMsgAlloc(0xc);
        if (puVar3 != (undefined2 *)0x0) {
          *(undefined1 *)(puVar3 + 1) = 0xb9;
          *puVar3 = 0;
          puVar3[4] = (ushort)param_1;
          WsfMsgSend(*(undefined1 *)(iVar1 + 0x56),puVar3);
        }
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

