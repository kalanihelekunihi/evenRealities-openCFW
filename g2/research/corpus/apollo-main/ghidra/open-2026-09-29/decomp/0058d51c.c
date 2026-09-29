
char FUN_0058d51c(undefined4 *param_1)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar2 = DAT_0058d9c0;
  if (param_1 == (undefined4 *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0058d9c8,DAT_0058d9c4,DAT_0058d9d0,0x29,DAT_0058d9cc);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0058d9d4,DAT_0058d9d4);
    }
    cVar1 = '\x02';
  }
  else {
    FUN_0043c0e4(DAT_0058d9c0,0x1220,0);
    cVar1 = FUN_0058da28(param_1,iVar2);
    if (cVar1 == '\0') {
      *(undefined1 *)(iVar2 + 0xe4) = 1;
      *(undefined1 *)(iVar2 + 0x1220) = 1;
      *(undefined1 *)(iVar2 + 0x1221) = 1;
      *(undefined1 *)(iVar2 + 0x1222) = 3;
      uVar3 = service_time_current_epoch_get();
      *(undefined4 *)(iVar2 + 0x1228) = uVar3;
      *(undefined4 *)(iVar2 + 0x122c) = 0;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_0058d9c8,DAT_0058d9c4,DAT_0058d9d0,0x3e,DAT_0058d9e0,*param_1,param_1[1],
                     (int)param_1 + 0x1a);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xcc00000,DAT_0058d9f8,DAT_0058d9f8,*param_1,param_1[1],
                            (int)param_1 + 0x1a);
      }
      cVar1 = '\0';
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0058d9c8,DAT_0058d9c4,DAT_0058d9d0,0x33,DAT_0058d9d8);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0058d9dc,DAT_0058d9dc);
      }
    }
  }
  return cVar1;
}

