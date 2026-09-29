
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
terminal_display_exit_sync
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_3;
  uStack_c = param_4;
  FUN_0043c0e4(&uStack_10,2,0);
  if (*(char *)(_DAT_005e4764 + 0x274) != '\0') {
    *(undefined1 *)(_DAT_005e4764 + 0x274) = 0;
    iVar2 = settings_get_terminal_mode();
    if (iVar2 == 0) {
      uVar1 = 1;
    }
    else {
      uVar1 = 2;
    }
    uStack_10 = CONCAT31(uStack_10._1_3_,uVar1);
    APP_PbTerminalTxEncodeStatusReply(&uStack_10);
  }
  return CONCAT44(uStack_c,uStack_10);
}

