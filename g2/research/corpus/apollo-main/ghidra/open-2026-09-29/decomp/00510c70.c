
undefined4
APP_PbTxEncodeGlassesCaseInfo(undefined1 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  undefined1 uVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 auStack_54 [12];
  uint local_48;
  int local_44;
  undefined1 auStack_40 [4];
  undefined2 local_3c;
  undefined1 auStack_2c [20];
  undefined4 uStack_18;
  
  uVar5 = DAT_00510fb4;
  uStack_18 = param_4;
  if (param_2 == 0) {
    FUN_00439c04(auStack_40,DAT_00510fac,0x14);
    local_3c = 1;
    APP_errorFaultHandler(auStack_40);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00510f68,DAT_00510f64,DAT_00510fb0,0x66,DAT_00510fa0);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00510fa8);
    }
    uVar5 = 2;
  }
  else {
    FUN_004905f4(auStack_2c,DAT_00510fb4,0x100);
    FUN_00439c04(auStack_54,auStack_2c,0x14);
    puVar1 = DAT_00510fb8;
    FUN_0043c0e4(DAT_00510fb8,10,0);
    *puVar1 = 1;
    puVar1[1] = param_1;
    *(undefined2 *)(puVar1 + 2) = 3;
    uVar2 = FUN_004ac726();
    puVar1[4] = uVar2;
    uVar2 = FUN_004ac73c();
    puVar1[5] = uVar2;
    uVar2 = FUN_004ac752();
    puVar1[6] = uVar2;
    iVar4 = FUN_004acad0();
    puVar1[7] = iVar4 == 1;
    puVar1[8] = 0;
    cVar3 = FUN_00490c32(auStack_54,DAT_00510f7c,puVar1);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00510f68,DAT_00510f64,DAT_00510fb0,0x7d,DAT_00510fbc,local_48 & 0xffff);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00510fc0,DAT_00510fc0,local_48 & 0xffff);
    }
    if (cVar3 == '\0') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        iVar4 = DAT_00510f80;
        if (local_44 != 0) {
          iVar4 = local_44;
        }
        FUN_0043d574(1,DAT_00510f68,DAT_00510f64,DAT_00510fb0,0x80,DAT_00510fc4,iVar4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        iVar4 = DAT_00510f80;
        if (local_44 != 0) {
          iVar4 = local_44;
        }
        compress_log_output(0x4400000,DAT_00510fc8,DAT_00510fc8,iVar4);
      }
      uVar5 = 0x2b;
    }
    else {
      Thread_MsgPbTxByBle(1,0x81,uVar5,local_48 & 0xffff);
      uVar5 = 0;
    }
  }
  return uVar5;
}

