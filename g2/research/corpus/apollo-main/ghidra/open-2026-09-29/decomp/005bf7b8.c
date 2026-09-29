
undefined4
legal_regulatory_ui_event_handler
          (int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  int local_20;
  undefined4 local_1c;
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  FUN_0043c0e4(&local_20,8,0);
  FUN_00439be4(&local_20,param_2,8);
  if (param_1 == 2) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005bf950,DAT_005bf94c,DAT_005bf948,0x140,DAT_005bf944);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_005bf954,DAT_005bf954);
    }
    FUN_005bf332(param_4);
    puVar1 = DAT_005bf8a4;
    *(undefined4 *)(DAT_005bf958 + 4) = *DAT_005bf8a4;
    FUN_0058c238(*puVar1,0xfa,0);
  }
  else if (param_1 == 3) {
    if (local_20 == 1) {
      FUN_0044ea04(*DAT_005bf8a4,local_1c,1);
    }
  }
  else if ((param_1 != 4) && (param_1 == 5)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005bf950,DAT_005bf94c,DAT_005bf948,0x155,DAT_005bf95c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_005bf960,DAT_005bf960);
    }
  }
  return 0;
}

