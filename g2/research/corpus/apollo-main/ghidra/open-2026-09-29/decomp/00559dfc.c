
char FUN_00559dfc(char *param_1)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  
  if (param_1 == (char *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00559fb0,DAT_00559fac,DAT_0055a2ec,0x141,DAT_0055a2e8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0055a2f0,DAT_0055a2f0);
    }
    cVar1 = '\x01';
  }
  else if ((*param_1 == '\0') || (*param_1 == '\x01')) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00559fb0,DAT_00559fac,DAT_0055a2ec,0x147,DAT_00559fa8,*param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00559fb4,DAT_00559fb4,*param_1);
    }
    cVar1 = '\x03';
  }
  else {
    health_lock_storage();
    iVar2 = DAT_00559f88;
    iVar4 = DAT_00559f88 + 200;
    FUN_0043c0e4(iVar4,0x505,0);
    *(undefined4 *)(iVar2 + 0xc4) = 0;
    *(undefined4 *)(iVar2 + 0xc4) = 1;
    cVar1 = FUN_0055a230(param_1,iVar4);
    if (cVar1 == '\0') {
      health_unlock_storage();
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar3 = FUN_00559854(*param_1);
        FUN_0043d574(3,DAT_00559fb0,DAT_00559fac,DAT_0055a2ec,0x163,DAT_0055a2fc,uVar3,
                     *(undefined2 *)(param_1 + 2));
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        uVar3 = FUN_00559854(*param_1);
        compress_log_output(0xc800000,PTR_s__health_data_mgr_Saved_health_hi_0055a300,
                            PTR_s__health_data_mgr_Saved_health_hi_0055a300,uVar3,
                            *(undefined2 *)(param_1 + 2));
      }
      cVar1 = '\0';
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00559fb0,DAT_00559fac,DAT_0055a2ec,0x158,DAT_0055a2f4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0055a2f8,DAT_0055a2f8);
      }
      *(undefined4 *)(iVar2 + 0xc4) = 0;
      health_unlock_storage();
    }
  }
  return cVar1;
}

