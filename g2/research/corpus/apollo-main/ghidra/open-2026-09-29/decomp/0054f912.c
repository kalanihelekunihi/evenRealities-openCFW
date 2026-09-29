
undefined4
AUDM_common_data_handler(undefined4 param_1,undefined1 *param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if ((param_2 == (undefined1 *)0x0) || (param_3 == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0054f988,DAT_0054f984,DAT_0054fa1c,0xcc,DAT_0054fa18,param_2,param_3,
                   param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_0054fa20,DAT_0054fa20,param_2,param_3);
    }
    uVar2 = 0xffffffff;
  }
  else {
    aud_send_message_type8(*param_2);
    uVar2 = 0;
  }
  return uVar2;
}

