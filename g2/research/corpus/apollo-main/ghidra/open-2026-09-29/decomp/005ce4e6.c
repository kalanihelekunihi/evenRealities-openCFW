
undefined4 APP_PbTxEncodeRingEvent(undefined1 param_1,ushort *param_2)

{
  undefined1 *puVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_54 [12];
  uint local_48;
  int local_44;
  undefined1 auStack_40 [4];
  undefined2 local_3c;
  undefined1 auStack_2c [20];
  
  uVar4 = DAT_005ce798;
  if (param_2 == (ushort *)0x0) {
    FUN_00439c04(auStack_40,DAT_005ce790,0x14);
    local_3c = 1;
    APP_errorFaultHandler(auStack_40);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005ce73c,DAT_005ce738,DAT_005ce794,0x84,DAT_005ce774);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005ce77c);
    }
    uVar4 = 2;
  }
  else {
    FUN_004905f4(auStack_2c,DAT_005ce798,0x100);
    FUN_00439c04(auStack_54,auStack_2c,0x14);
    puVar1 = DAT_005ce79c;
    FUN_0043c0e4(DAT_005ce79c,0x40,0);
    *puVar1 = 1;
    puVar1[1] = param_1;
    *(undefined2 *)(puVar1 + 2) = 3;
    puVar1[0xc] = (char)param_2[4];
    *(undefined4 *)(puVar1 + 0x10) = *(undefined4 *)(param_2 + 6);
    *(ushort *)(puVar1 + 4) = *param_2;
    if ((*param_2 != 0) && (*param_2 < 7)) {
      FUN_00439be4(puVar1 + 6,param_2 + 1,*param_2);
    }
    puVar1[0x14] = 0;
    cVar2 = FUN_00490c32(auStack_54,DAT_005ce750,puVar1);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005ce73c,DAT_005ce738,DAT_005ce794,0x9d,DAT_005ce7a0,local_48 & 0xffff);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_005ce7a4,DAT_005ce7a4,local_48 & 0xffff);
    }
    if (cVar2 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        iVar3 = DAT_005ce754;
        if (local_44 != 0) {
          iVar3 = local_44;
        }
        FUN_0043d574(1,DAT_005ce73c,DAT_005ce738,DAT_005ce794,0xa0,DAT_005ce7a8,iVar3);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        iVar3 = DAT_005ce754;
        if (local_44 != 0) {
          iVar3 = local_44;
        }
        compress_log_output(0x4400000,DAT_005ce7ac,DAT_005ce7ac,iVar3);
      }
      uVar4 = 0x2b;
    }
    else {
      Thread_MsgPbTxByBle(1,0x91,uVar4,local_48 & 0xffff);
      uVar4 = 0;
    }
  }
  return uVar4;
}

