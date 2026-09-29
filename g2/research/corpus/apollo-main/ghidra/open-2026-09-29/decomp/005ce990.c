
undefined4 APP_PbTerminalRxFrameDataProcess(int param_1,undefined2 param_2,int param_3)

{
  int *piVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint local_30;
  undefined4 local_2c;
  uint local_28;
  uint local_24;
  undefined1 auStack_20 [12];
  uint local_14;
  
  if ((param_1 == 0) || (param_3 == 0)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_2c = DAT_005cf1ec;
      local_30 = 0x70;
      FUN_0043d574(1,DAT_005cf1d8,DAT_005cf1d4,DAT_005cf1f0);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005cf1f4,DAT_005cf1f4);
    }
    uVar4 = 6;
  }
  else {
    FUN_0048f49c(&local_30,param_1,param_2);
    FUN_00439c04(auStack_20,&local_30,0x10);
    cVar2 = FUN_00490120(auStack_20,DAT_005cf1c8,param_3);
    if (cVar2 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_28 = DAT_005cf1e0;
        if (local_14 != 0) {
          local_28 = local_14;
        }
        local_2c = DAT_005cf1f8;
        local_30 = 0x77;
        FUN_0043d574(1,DAT_005cf1d8,DAT_005cf1d4,DAT_005cf1f0);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        uVar5 = DAT_005cf1e0;
        if (local_14 != 0) {
          uVar5 = local_14;
        }
        compress_log_output(0x4400000,DAT_005cf1fc,DAT_005cf1fc,uVar5);
      }
      uVar4 = 5;
    }
    else {
      iVar3 = osKernelGetTickCount();
      piVar1 = DAT_005cf200;
      uVar5 = iVar3 - *DAT_005cf200;
      if ((*(char *)(param_3 + 1) == *DAT_005cf204) && (uVar5 < 3000)) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          local_28 = (uint)*(byte *)(param_3 + 1);
          local_2c = DAT_005cf208;
          local_30 = 0x7e;
          local_24 = uVar5;
          FUN_0043d574(2,DAT_005cf1d8,DAT_005cf1d4,DAT_005cf1f0);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          local_30 = uVar5;
          compress_log_output(0x8800000,DAT_005cf20c,DAT_005cf20c,*(undefined1 *)(param_3 + 1));
        }
        uVar4 = 0xd;
      }
      else {
        *DAT_005cf204 = *(char *)(param_3 + 1);
        *piVar1 = iVar3;
        uVar4 = 0;
      }
    }
  }
  return uVar4;
}

