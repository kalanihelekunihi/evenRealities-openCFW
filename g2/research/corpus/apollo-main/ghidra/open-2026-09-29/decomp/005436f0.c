
undefined4
PB_TxEncodeTimeSyncInfo(byte param_1,int param_2,undefined2 param_3,undefined1 *param_4,int param_5)

{
  undefined4 *puVar1;
  char cVar2;
  undefined4 uVar3;
  int iVar4;
  undefined1 auStack_80 [12];
  uint local_74;
  int local_70;
  undefined1 auStack_6c [4];
  undefined2 local_68;
  undefined1 auStack_58 [4];
  undefined2 local_54;
  undefined1 auStack_44 [4];
  undefined2 local_40;
  undefined1 auStack_30 [20];
  undefined1 *puStack_1c;
  
  uVar3 = 0;
  puStack_1c = param_4;
  if (param_2 == 0) {
    FUN_00439c04(auStack_44,DAT_00543be0,0x14);
    local_40 = 1;
    uVar3 = APP_errorFaultHandler(auStack_44);
  }
  if (param_4 == (undefined1 *)0x0) {
    FUN_00439c04(auStack_58,DAT_00543be4,0x14);
    local_54 = 1;
    uVar3 = APP_errorFaultHandler(auStack_58);
  }
  if (param_5 == 0) {
    FUN_00439c04(auStack_6c,DAT_00543be8,0x14);
    local_68 = 1;
    uVar3 = APP_errorFaultHandler(auStack_6c);
  }
  if (((param_2 == 0) || (param_4 == (undefined1 *)0x0)) || (param_5 == 0)) {
    iVar4 = FUN_0043d0ce(uVar3);
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00543bf8,DAT_00543bf4,DAT_00543bf0,0x12f,DAT_00543bec);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00543bfc,DAT_00543bfc);
    }
    uVar3 = 2;
  }
  else {
    FUN_0043c0e4(param_2,param_3,0);
    FUN_004905f4(auStack_30,param_2,param_3);
    FUN_00439c04(auStack_80,auStack_30,0x14);
    *param_4 = 0x80;
    *(ushort *)(param_4 + 2) = (ushort)param_1;
    *(undefined2 *)(param_4 + 4) = 0x80;
    param_4[0xd] = 0;
    cVar2 = FUN_00490c32(auStack_80,DAT_005439c8,param_4);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00543bf8,DAT_00543bf4,DAT_00543bf0,0x13f,DAT_005439cc,local_74);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_005439d0,DAT_005439d0,local_74);
    }
    if (cVar2 == '\0') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        iVar4 = DAT_005439d4;
        if (local_70 != 0) {
          iVar4 = local_70;
        }
        FUN_0043d574(1,DAT_00543bf8,DAT_00543bf4,DAT_00543bf0,0x142,DAT_005439d8,iVar4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        iVar4 = DAT_005439d4;
        if (local_70 != 0) {
          iVar4 = local_70;
        }
        compress_log_output(0x4400000,DAT_00543b88,DAT_00543b88,iVar4);
      }
      uVar3 = 0x2b;
    }
    else {
      Thread_MsgPbTxByBle(1,0x80,param_2,local_74 & 0xffff);
      puVar1 = DAT_00543bd0;
      SVC_KvdbWriteTime(*DAT_00543bd0,(int)*(char *)(DAT_00543bd0 + 1));
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00543bf8,DAT_00543bf4,DAT_00543bf0,0x14a,DAT_00543c00,*puVar1,
                     (int)*(char *)(puVar1 + 1));
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_00543c04,DAT_00543c04,*puVar1,(int)*(char *)(puVar1 + 1))
        ;
      }
      uVar3 = 0;
    }
  }
  return uVar3;
}

