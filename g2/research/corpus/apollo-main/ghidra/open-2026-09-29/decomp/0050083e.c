
uint FUN_0050083e(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  byte *pbVar2;
  int iVar3;
  uint uVar4;
  undefined1 *puVar5;
  uint local_40;
  undefined4 local_3c;
  undefined1 *local_38;
  uint local_34;
  undefined4 local_30;
  uint local_2c;
  undefined1 auStack_28 [12];
  uint local_1c;
  undefined1 *local_18;
  undefined4 uStack_14;
  
  uVar1 = DAT_0050116c;
  uStack_14 = param_4;
  FUN_0043c0e4(DAT_0050116c,0x400,0);
  FUN_004905f4(&local_40,uVar1,0x400);
  FUN_00439c04(auStack_28,&local_40,0x14);
  pbVar2 = DAT_00501170;
  iVar3 = FUN_00490c32(auStack_28,DAT_00501174,DAT_00501170);
  if (iVar3 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_38 = DAT_00501178;
      if (local_18 != (undefined1 *)0x0) {
        local_38 = local_18;
      }
      local_3c = DAT_0050117c;
      local_40 = 0x91;
      FUN_0043d574(1,DAT_00501188,DAT_00501184,DAT_00501180);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      puVar5 = DAT_00501178;
      if (local_18 != (undefined1 *)0x0) {
        puVar5 = local_18;
      }
      compress_log_output(0x4400000,DAT_0050118c,DAT_0050118c,puVar5);
    }
    uVar4 = 0xffffffff;
  }
  else {
    if (param_1 == '\0') {
      uVar4 = Thread_MsgPbTxByBle(1,0x1f,uVar1,local_1c & 0xffff);
    }
    else {
      uVar4 = Thread_MsgPbNotifyByBle(1,0x1f,uVar1,local_1c & 0xffff);
    }
    if (uVar4 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_38 = DAT_005011a0;
        if (param_1 != '\0') {
          local_38 = DAT_0050119c;
        }
        local_2c = local_1c;
        local_30 = *(undefined4 *)(pbVar2 + 4);
        local_34 = (uint)*pbVar2;
        local_3c = DAT_005011a4;
        local_40 = 0xab;
        FUN_0043d574(4,DAT_00501188,DAT_00501184,DAT_00501180);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        puVar5 = DAT_005011a0;
        if (param_1 != '\0') {
          puVar5 = DAT_0050119c;
        }
        local_38 = (undefined1 *)local_1c;
        local_3c = *(undefined4 *)(pbVar2 + 4);
        local_40 = (uint)*pbVar2;
        compress_log_output(0x11000000,DAT_005011a8,DAT_005011a8,puVar5);
      }
      uVar4 = 0;
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_38 = DAT_00501190;
        if (param_1 == '\0') {
          local_38 = &LAB_00500bf0;
        }
        local_3c = DAT_00501194;
        local_40 = 0xa3;
        local_34 = uVar4;
        FUN_0043d574(1,DAT_00501188,DAT_00501184,DAT_00501180);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        puVar5 = DAT_00501190;
        if (param_1 == '\0') {
          puVar5 = &LAB_00500bf0;
        }
        local_40 = uVar4;
        compress_log_output(0x4800000,DAT_00501198,DAT_00501198,puVar5);
      }
    }
  }
  return uVar4;
}

