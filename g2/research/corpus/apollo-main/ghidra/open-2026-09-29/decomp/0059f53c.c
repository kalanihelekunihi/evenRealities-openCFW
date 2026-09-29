
undefined4
APP_PbTranslateRxFrameDataProcess(int param_1,ushort param_2,byte *param_3,undefined4 param_4)

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
      local_34 = DAT_0059fa68;
      local_38 = 0x3f;
      FUN_0043d574(1,DAT_0059fa74,DAT_0059fa70,DAT_0059fa6c);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0059fa78,DAT_0059fa78);
    }
    uVar5 = 6;
  }
  else {
    uVar6 = param_2;
    if (0x20 < param_2) {
      uVar6 = 0x20;
    }
    FUN_0043dacc(DAT_0059fa7c,0x10,param_1,uVar6);
    FUN_0048f49c(&local_38,param_1,param_2);
    FUN_00439c04(auStack_24,&local_38,0x10);
    cVar3 = FUN_00490120(auStack_24,DAT_0059fa80,param_3);
    if (cVar3 == '\0') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_30 = DAT_0059fa84;
        if (local_18 != 0) {
          local_30 = local_18;
        }
        local_34 = DAT_0059fa88;
        local_38 = 0x46;
        FUN_0043d574(1,DAT_0059fa74,DAT_0059fa70,DAT_0059fa6c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        uVar7 = DAT_0059fa84;
        if (local_18 != 0) {
          uVar7 = local_18;
        }
        compress_log_output(0x4400000,DAT_0059fa8c,DAT_0059fa8c,uVar7);
      }
      uVar5 = 5;
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_28 = (uint)*DAT_0059fa90;
        local_2c = (uint)param_3[1];
        local_30 = (uint)*param_3;
        local_34 = DAT_0059fa94;
        local_38 = 0x49;
        FUN_0043d574(3,DAT_0059fa74,DAT_0059fa70,DAT_0059fa6c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        local_34 = (uint)*DAT_0059fa90;
        local_38 = (uint)param_3[1];
        compress_log_output(0xcc00000,DAT_0059fa98,DAT_0059fa98,*param_3);
      }
      iVar4 = osKernelGetTickCount();
      piVar2 = DAT_0059fa9c;
      pbVar1 = DAT_0059fa90;
      uVar7 = iVar4 - *DAT_0059fa9c;
      if ((param_3[1] == *DAT_0059fa90) && (uVar7 < 3000)) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          local_30 = (uint)*pbVar1;
          local_34 = DAT_0059faa0;
          local_38 = 0x50;
          local_2c = uVar7;
          FUN_0043d574(2,DAT_0059fa74,DAT_0059fa70,DAT_0059fa6c);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          local_38 = uVar7;
          compress_log_output(0x8800000,DAT_0059faa4,DAT_0059faa4,*pbVar1);
        }
        uVar5 = 0xd;
      }
      else {
        *DAT_0059fa90 = param_3[1];
        *piVar2 = iVar4;
        uVar5 = 0;
      }
    }
  }
  return uVar5;
}

