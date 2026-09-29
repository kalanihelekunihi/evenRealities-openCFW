
void _masterConnectEventRetry(char param_1)

{
  ushort *puVar1;
  int iVar2;
  int iVar3;
  
  puVar1 = DAT_004a22e0;
  if (param_1 == '>') {
    *DAT_004a22e0 = 0;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004a1af4,DAT_004a1af0,DAT_004a22f4,0x3ae,DAT_004a22e4,0x3e);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_004a22f8,DAT_004a22f8,0x3e);
    }
    central_schedule_master_connect_004a2618(2000,1);
  }
  else {
    *DAT_004a22e0 = *DAT_004a22e0 + 1;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004a1af4,DAT_004a1af0,DAT_004a22f4,0x3b5,DAT_004a22fc,*puVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_004a2368,DAT_004a2368,*puVar1);
    }
    iVar2 = DAT_004a236c;
    if (*puVar1 < 0xbe) {
      if (*puVar1 < 0xb) {
        iVar2 = 2000;
      }
      else {
        iVar2 = (*puVar1 - 10) * 10000;
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004a1af4,DAT_004a1af0,DAT_004a22f4,0x3bd,DAT_004a2370);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004a2374,DAT_004a2374);
      }
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004a1af4,DAT_004a1af0,DAT_004a22f4,0x3c9,DAT_004a2378,param_1,iVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_004a2644,DAT_004a2644,param_1,iVar2);
    }
    central_schedule_master_connect_004a2618(iVar2,1);
  }
  return;
}

