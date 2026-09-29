
undefined4 setting_notify_common(int param_1)

{
  undefined1 *puVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 local_3c [3];
  uint local_30;
  int local_2c;
  undefined1 auStack_28 [20];
  
  iVar3 = FUN_0045a568();
  puVar1 = DAT_0049bdf0;
  if (iVar3 == 1) {
    if (param_1 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0049c02c,DAT_0049c028,DAT_0049c024,0x16e,DAT_0049bf18);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0049bf20);
      }
      uVar4 = 1;
    }
    else {
      FUN_0043c0e4(DAT_0049bdf0,0x68,0);
      FUN_00439c04(puVar1,param_1,0x68);
      piVar2 = DAT_0049c030;
      *DAT_0049c030 = *DAT_0049c030 + 1;
      *(int *)(puVar1 + 4) = *piVar2;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_3c[0] = *(undefined4 *)(puVar1 + 4);
        FUN_0043d574(4,DAT_0049c02c,DAT_0049c028,DAT_0049c024,0x178,DAT_0049c034,*puVar1);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_0049c038,DAT_0049c038,*puVar1,*(undefined4 *)(puVar1 + 4)
                           );
      }
      uVar4 = DAT_0049bffc;
      FUN_004905f4(auStack_28,DAT_0049bffc,0x100);
      FUN_00439c04(local_3c,auStack_28,0x14);
      iVar3 = FUN_00490c32(local_3c,DAT_0049c03c,puVar1);
      if (iVar3 == 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          iVar3 = DAT_0049c040;
          if (local_2c != 0) {
            iVar3 = local_2c;
          }
          FUN_0043d574(1,DAT_0049c02c,DAT_0049c028,DAT_0049c024,0x17d,DAT_0049c044,iVar3);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          iVar3 = DAT_0049c040;
          if (local_2c != 0) {
            iVar3 = local_2c;
          }
          compress_log_output(0x4400000,DAT_0049c048,DAT_0049c048,iVar3);
        }
        uVar4 = 0x2b;
      }
      else {
        iVar3 = FUN_0045a568();
        if (iVar3 == 1) {
          Thread_MsgPbNotifyByBle(1,9,uVar4,local_30 & 0xffff);
        }
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0049c02c,DAT_0049c028,DAT_0049c024,0x185,DAT_0049c04c,local_30);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_0049c050,DAT_0049c050,local_30);
        }
        uVar4 = 0;
      }
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0049c02c,DAT_0049c028,DAT_0049c024,0x167,DAT_0049bfe8);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0049bff0,DAT_0049bff0);
    }
    uVar4 = 0;
  }
  return uVar4;
}

