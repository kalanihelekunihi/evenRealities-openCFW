
undefined4
APP_PbRxTelepromptFrameDataProcess(int param_1,ushort param_2,byte *param_3,undefined4 param_4)

{
  byte *pbVar1;
  int *piVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  ushort uVar6;
  uint uVar7;
  uint local_38;
  uint local_34;
  uint local_30;
  uint local_2c;
  uint local_28;
  undefined1 auStack_24 [12];
  uint local_18;
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  if ((param_1 == 0) || (param_3 == (byte *)0x0)) {
    iVar4 = FUN_0043d0ce(0);
    if (iVar4 << 0x1e < 0) {
      local_34 = DAT_00588cf4;
      local_38 = 0x40;
      FUN_0043d574(1,DAT_00588d00,DAT_00588cfc,DAT_00588cf8);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00588d04,DAT_00588d04);
    }
    uVar5 = 6;
  }
  else {
    uVar6 = param_2;
    if (0x20 < param_2) {
      uVar6 = 0x20;
    }
    FUN_0043dacc(DAT_00588d08,0x10,param_1,uVar6);
    FUN_0048f49c(&local_38,param_1,param_2);
    FUN_00439c04(auStack_24,&local_38,0x10);
    cVar3 = FUN_00490120(auStack_24,DAT_00588d0c,param_3);
    if (cVar3 == '\0') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_30 = DAT_00588d10;
        if (local_18 != 0) {
          local_30 = local_18;
        }
        local_34 = DAT_00588d14;
        local_38 = 0x47;
        FUN_0043d574(1,DAT_00588d00,DAT_00588cfc,DAT_00588cf8);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        uVar7 = DAT_00588d10;
        if (local_18 != 0) {
          uVar7 = local_18;
        }
        compress_log_output(0x4400000,DAT_00588d18,DAT_00588d18,uVar7);
      }
      uVar5 = 5;
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_28 = (uint)*DAT_00588d1c;
        local_2c = (uint)param_3[1];
        local_30 = (uint)*param_3;
        local_34 = DAT_00588d20;
        local_38 = 0x4a;
        FUN_0043d574(3,DAT_00588d00,DAT_00588cfc,DAT_00588cf8);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        local_34 = (uint)*DAT_00588d1c;
        local_38 = (uint)param_3[1];
        compress_log_output(0xcc00000,DAT_00588d24,DAT_00588d24,*param_3);
      }
      iVar4 = osKernelGetTickCount();
      piVar2 = DAT_00588d28;
      pbVar1 = DAT_00588d1c;
      uVar7 = iVar4 - *DAT_00588d28;
      if ((param_3[1] == *DAT_00588d1c) && (uVar7 < 3000)) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          local_30 = (uint)*pbVar1;
          local_34 = DAT_00588d2c;
          local_38 = 0x51;
          local_2c = uVar7;
          FUN_0043d574(2,DAT_00588d00,DAT_00588cfc,DAT_00588cf8);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          local_38 = uVar7;
          compress_log_output(0x8800000,DAT_00588d30,DAT_00588d30,*pbVar1);
        }
        uVar5 = 0xd;
      }
      else {
        *DAT_00588d1c = param_3[1];
        *piVar2 = iVar4;
        uVar5 = 0;
      }
    }
  }
  return uVar5;
}

