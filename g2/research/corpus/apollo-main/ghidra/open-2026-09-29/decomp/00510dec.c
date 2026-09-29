
undefined4
APP_PbNotifyEncodeGlassesCaseInfo
          (undefined4 param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  char *pcVar2;
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
  if (param_2 == (undefined1 *)0x0) {
    FUN_00439c04(auStack_40,DAT_00510fcc,0x14);
    local_3c = 1;
    APP_errorFaultHandler(auStack_40);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00510f68,DAT_00510f64,DAT_00510fd0,0x8c,DAT_00510fa0);
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
    pcVar2 = DAT_00510fd4;
    puVar1[1] = *DAT_00510fd4;
    *pcVar2 = *pcVar2 + '\x01';
    *(undefined2 *)(puVar1 + 2) = 3;
    puVar1[4] = *param_2;
    puVar1[5] = param_2[1];
    puVar1[6] = param_2[2];
    puVar1[7] = param_2[3];
    puVar1[8] = 0;
    cVar3 = FUN_00490c32(auStack_54,DAT_00510f7c,puVar1);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00510f68,DAT_00510f64,DAT_00510fd0,0xa3,DAT_00510fbc,local_48 & 0xffff);
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
        FUN_0043d574(1,DAT_00510f68,DAT_00510f64,DAT_00510fd0,0xa7,DAT_00510fc4,iVar4);
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
      Thread_MsgPbNotifyByBle(1,0x81,uVar5,local_48 & 0xffff);
      uVar5 = 0;
    }
  }
  return uVar5;
}

