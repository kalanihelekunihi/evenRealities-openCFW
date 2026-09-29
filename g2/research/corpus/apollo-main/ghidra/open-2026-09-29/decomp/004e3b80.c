
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4
APP_PbNotifyEncodeEvenAIVADInfo
          (undefined4 param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  char *pcVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 auStack_54 [12];
  uint uStack_48;
  int iStack_44;
  undefined1 auStack_40 [4];
  undefined2 uStack_3c;
  undefined1 auStack_2c [20];
  undefined4 uStack_18;
  
  uVar5 = DAT_004e4034;
  uStack_18 = param_4;
  if (param_2 == (undefined1 *)0x0) {
    FUN_00439c04(auStack_40,_DAT_004e4534,0x14);
    uStack_3c = 1;
    APP_errorFaultHandler(auStack_40);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_pb_evenai_004e3ea0,PTR_s_D__01_workspace_s200_ap510b_iar__004e3e9c,
                   _DAT_004e4604,0x148,DAT_004e3e8c);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__pb_evenai_PORINT_NULL_004e3e94);
    }
    uVar5 = 2;
  }
  else {
    FUN_004905f4(auStack_2c,DAT_004e4034,0x100);
    FUN_00439c04(auStack_54,auStack_2c,0x14);
    puVar1 = DAT_004e4038;
    FUN_0043c0e4(DAT_004e4038,0x20c,0);
    *puVar1 = 2;
    pcVar2 = DAT_004e4124;
    puVar1[1] = *DAT_004e4124;
    *pcVar2 = *pcVar2 + '\x01';
    *(undefined2 *)(puVar1 + 2) = 4;
    puVar1[4] = *param_2;
    cVar3 = FUN_00490c32(auStack_54,DAT_004e3d0c,puVar1);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_pb_evenai_004e3ea0,PTR_s_D__01_workspace_s200_ap510b_iar__004e3e9c,
                   _DAT_004e4604,0x15b,DAT_004e4110,uStack_48 & 0xffff);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004e4114,DAT_004e4114,uStack_48 & 0xffff);
    }
    if (cVar3 == '\0') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        iVar4 = _DAT_004e4128;
        if (iStack_44 != 0) {
          iVar4 = iStack_44;
        }
        FUN_0043d574(1,PTR_s_pb_evenai_004e3ea0,PTR_s_D__01_workspace_s200_ap510b_iar__004e3e9c,
                     _DAT_004e4604,0x15e,DAT_004e4118,iVar4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        iVar4 = _DAT_004e4128;
        if (iStack_44 != 0) {
          iVar4 = iStack_44;
        }
        compress_log_output(0x4400000,DAT_004e4388,DAT_004e4388,iVar4);
      }
      uVar5 = 0x2b;
    }
    else {
      Thread_MsgPbNotifyByBle(1,7,uVar5,uStack_48 & 0xffff);
      uVar5 = 0;
    }
  }
  return uVar5;
}

