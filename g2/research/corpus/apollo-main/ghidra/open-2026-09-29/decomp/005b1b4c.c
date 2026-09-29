
undefined4
APP_PbConversateRxFrameDataProcess(int param_1,ushort param_2,byte *param_3,undefined4 param_4)

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
      local_34 = DAT_005b223c;
      local_38 = 0x3e;
      FUN_0043d574(1,DAT_005b2248,DAT_005b2244,DAT_005b2240);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005b224c,DAT_005b224c);
    }
    uVar5 = 6;
  }
  else {
    uVar6 = param_2;
    if (0x20 < param_2) {
      uVar6 = 0x20;
    }
    FUN_0043dacc(DAT_005b2250,0x10,param_1,uVar6);
    FUN_0048f49c(&local_38,param_1,param_2);
    FUN_00439c04(auStack_24,&local_38,0x10);
    cVar3 = FUN_00490120(auStack_24,DAT_005b2254,param_3);
    if (cVar3 == '\0') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_30 = DAT_005b2258;
        if (local_18 != 0) {
          local_30 = local_18;
        }
        local_34 = DAT_005b225c;
        local_38 = 0x45;
        FUN_0043d574(1,DAT_005b2248,DAT_005b2244,DAT_005b2240);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        uVar7 = DAT_005b2258;
        if (local_18 != 0) {
          uVar7 = local_18;
        }
        compress_log_output(0x4400000,DAT_005b2260,DAT_005b2260,uVar7);
      }
      uVar5 = 5;
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_28 = (uint)*DAT_005b2264;
        local_2c = (uint)param_3[1];
        local_30 = (uint)*param_3;
        local_34 = DAT_005b2268;
        local_38 = 0x48;
        FUN_0043d574(3,DAT_005b2248,DAT_005b2244,DAT_005b2240);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        local_34 = (uint)*DAT_005b2264;
        local_38 = (uint)param_3[1];
        compress_log_output(0xcc00000,DAT_005b226c,DAT_005b226c,*param_3);
      }
      iVar4 = osKernelGetTickCount();
      piVar2 = DAT_005b2270;
      pbVar1 = DAT_005b2264;
      uVar7 = iVar4 - *DAT_005b2270;
      if ((param_3[1] == *DAT_005b2264) && (uVar7 < 3000)) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          local_30 = (uint)*pbVar1;
          local_34 = DAT_005b2274;
          local_38 = 0x4f;
          local_2c = uVar7;
          FUN_0043d574(2,DAT_005b2248,DAT_005b2244,DAT_005b2240);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          local_38 = uVar7;
          compress_log_output(0x8800000,DAT_005b2278,DAT_005b2278,*pbVar1);
        }
        uVar5 = 0xd;
      }
      else {
        *DAT_005b2264 = param_3[1];
        *piVar2 = iVar4;
        uVar5 = 0;
      }
    }
  }
  return uVar5;
}

