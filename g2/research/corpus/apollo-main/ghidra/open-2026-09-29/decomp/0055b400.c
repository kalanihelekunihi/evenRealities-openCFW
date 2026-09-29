
int FUN_0055b400(undefined4 *param_1,undefined2 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 local_1c;
  undefined1 local_1b;
  char local_18;
  char local_17;
  char local_16;
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  FUN_0043c0e4(&local_1c,2,0);
  FUN_0043c0e4(&local_18,3,0);
  if (param_1 == (undefined4 *)0x0) {
    iVar1 = -1;
  }
  else {
    iVar1 = FUN_0055b3ea(param_2);
    if (iVar1 == 0) {
      iVar1 = 0xff;
    }
    else {
      local_1c = (undefined1)*param_2;
      local_1b = (undefined1)((ushort)*param_2 >> 8);
      iVar1 = (*(code *)*param_1)(7,&local_1c,2);
      if ((iVar1 == 0) && (iVar1 = (*(code *)param_1[3])(&local_18,3), iVar1 == 0)) {
        if ((local_18 == '\a') && (local_16 == '\x17')) {
          if (local_17 == '\0') {
            iVar1 = 0;
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(1,DAT_0055b9d4,DAT_0055b9d0,DAT_0055b9cc,0xe1,DAT_0055b9dc,local_17);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x4400000,DAT_0055b9e0,DAT_0055b9e0,local_17);
            }
            iVar1 = 0xff;
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0055b9d4,DAT_0055b9d0,DAT_0055b9cc,0xdc,DAT_0055b9c8,local_18,
                         local_17,local_16);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x4c00000,DAT_0055b9d8,DAT_0055b9d8,local_18,local_17,local_16);
          }
          iVar1 = 0xff;
        }
      }
    }
  }
  return iVar1;
}

