
undefined4 APP_PbTxEncodeNotifWhitelistChk(undefined1 param_1,uint *param_2)

{
  undefined1 *puVar1;
  undefined1 uVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  uint local_58;
  uint local_54;
  uint local_50;
  uint local_4c;
  uint local_48;
  uint local_44;
  undefined1 auStack_40 [12];
  uint local_34;
  uint local_30;
  undefined1 auStack_2c [20];
  
  uVar5 = DAT_004d78f8;
  local_44 = 0;
  if (param_2 == (uint *)0x0) {
    FUN_00439c04(&local_58,DAT_004d7968,0x14);
    local_54 = CONCAT22(local_54._2_2_,1);
    APP_errorFaultHandler(&local_58);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      local_54 = DAT_004d7944;
      local_58 = 0x13a;
      FUN_0043d574(1,DAT_004d7974,DAT_004d7970,DAT_004d796c);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004d794c);
    }
    uVar5 = 2;
  }
  else {
    FUN_004905f4(auStack_2c,DAT_004d78f8,0x100);
    FUN_00439c04(auStack_40,auStack_2c,0x14);
    puVar1 = DAT_004d78fc;
    FUN_0043c0e4(DAT_004d78fc,0x4c,0);
    *puVar1 = 4;
    puVar1[1] = param_1;
    *(undefined2 *)(puVar1 + 2) = 7;
    uVar6 = *param_2;
    iVar4 = semantic_whitelist_get_cached_crc32(&local_44);
    if (iVar4 == 0) {
      *(undefined4 *)(puVar1 + 4) = 0;
      puVar1[8] = 1;
      puVar1[9] = 7;
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_54 = DAT_004d7978;
        local_58 = 0x149;
        FUN_0043d574(2,DAT_004d7974,DAT_004d7970,DAT_004d796c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_004d797c,DAT_004d797c);
      }
    }
    else {
      *(uint *)(puVar1 + 4) = local_44;
      if (uVar6 == local_44) {
        uVar2 = 2;
      }
      else {
        uVar2 = 3;
      }
      puVar1[8] = uVar2;
      puVar1[9] = 0;
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_48 = (uint)(byte)puVar1[8];
        local_4c = local_44;
        local_54 = DAT_004d7980;
        local_58 = 0x14f;
        local_50 = uVar6;
        FUN_0043d574(3,DAT_004d7974,DAT_004d7970,DAT_004d796c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        local_54 = (uint)(byte)puVar1[8];
        local_58 = local_44;
        compress_log_output(0xcc00000,DAT_004d7984,DAT_004d7984,uVar6);
      }
    }
    cVar3 = FUN_00490c32(auStack_40,DAT_004d792c,puVar1);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      local_50 = local_34 & 0xffff;
      local_54 = DAT_004d7900;
      local_58 = 0x154;
      FUN_0043d574(4,DAT_004d7974,DAT_004d7970,DAT_004d796c);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004d7904,DAT_004d7904,local_34 & 0xffff);
    }
    if (cVar3 == '\0') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_50 = DAT_004d7988;
        if (local_30 != 0) {
          local_50 = local_30;
        }
        local_54 = DAT_004d7908;
        local_58 = 0x156;
        FUN_0043d574(1,DAT_004d7974,DAT_004d7970,DAT_004d796c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        uVar6 = DAT_004d7988;
        if (local_30 != 0) {
          uVar6 = local_30;
        }
        compress_log_output(0x4400000,DAT_004d790c,DAT_004d790c,uVar6);
      }
      uVar5 = 0x2b;
    }
    else {
      Thread_MsgPbTxByBle(1,4,uVar5,local_34 & 0xffff);
      uVar5 = 0;
    }
  }
  return uVar5;
}

