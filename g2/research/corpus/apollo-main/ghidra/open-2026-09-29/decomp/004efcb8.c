
undefined8 FUN_004efcb8(uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  short *psVar2;
  char cVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  uint local_30;
  undefined4 local_2c;
  uint local_28;
  undefined4 uStack_24;
  
  psVar2 = DAT_004eff64;
  local_30 = param_1;
  local_2c = param_2;
  local_28 = param_3;
  uStack_24 = param_4;
  if (*DAT_004eff54 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      local_2c = DAT_004eff58;
      local_30 = 0x522;
      FUN_0043d574(2,DAT_004eff18,DAT_004eff14,DAT_004eff5c);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004eff60,DAT_004eff60);
    }
  }
  else if (*DAT_004eff64 != 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      local_2c = DAT_004eff68;
      local_30 = 0x528;
      local_28 = param_1;
      FUN_0043d574(4,DAT_004eff18,DAT_004eff14,DAT_004eff5c);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004eff6c,DAT_004eff6c,param_1);
    }
    iVar4 = DAT_004eff70;
    FUN_0043c0e4(DAT_004eff70,0x1088,0);
    FUN_00439be4(iVar4,psVar2,0x1088);
    for (uVar6 = 0; puVar1 = DAT_004eff00, (int)uVar6 < 8; uVar6 = uVar6 + 1) {
      if ((param_1 & 0xff & 1 << (uVar6 & 0xff)) != 0) {
        FUN_0043c0e4(uVar6 * 0x210 + iVar4 + 4,0x210,0);
      }
    }
    osMutexAcquire(*DAT_004eff00,0xffffffff);
    iVar7 = 0;
    for (iVar8 = 0; iVar8 < 8; iVar8 = iVar8 + 1) {
      iVar5 = FUN_0044a43c(iVar8 * 0x210 + iVar4 + 4);
      if (iVar5 != 0) {
        FUN_00439be4(psVar2 + iVar7 * 0x108 + 2,iVar8 * 0x210 + iVar4 + 4,0x210);
        iVar7 = iVar7 + 1;
      }
    }
    *psVar2 = (short)iVar7;
    osMutexRelease(*puVar1);
    cVar3 = FUN_0045a570();
    if (cVar3 == '\x01') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_28 = param_1 & 0xff;
        local_2c = DAT_004eff74;
        local_30 = 0x543;
        FUN_0043d574(3,DAT_004eff18,DAT_004eff14,DAT_004eff5c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_004eff78,DAT_004eff78,param_1 & 0xff);
      }
      FUN_0043c0e4(&local_28,5,0);
      local_28 = CONCAT31(local_28._1_3_,2);
      FUN_00464bb2(1,&local_28,1,0);
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_2c = DAT_004eff7c;
        local_30 = 0x547;
        FUN_0043d574(4,DAT_004eff18,DAT_004eff14,DAT_004eff5c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004eff80,DAT_004eff80);
      }
    }
  }
  return CONCAT44(local_2c,local_30);
}

