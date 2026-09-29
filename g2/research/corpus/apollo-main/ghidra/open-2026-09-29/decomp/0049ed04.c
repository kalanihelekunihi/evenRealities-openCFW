
undefined4 FUN_0049ed04(undefined4 param_1,int param_2,undefined4 param_3)

{
  uint *puVar1;
  int *piVar2;
  char cVar3;
  int iVar4;
  uint uVar5;
  uint local_1c;
  char local_18 [4];
  uint local_14;
  
  if (param_2 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0049efbc,DAT_0049efb8,DAT_0049efe8,0x89,DAT_0049efe4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0049efec,DAT_0049efec);
    }
    return 0xffffffff;
  }
  FUN_0043c0e4(local_18,8,0);
  FUN_00439be4(local_18,param_2,param_3);
  puVar1 = DAT_0049efc4;
  if (local_18[0] == '\x02') {
    if (local_14 == 0) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0049efbc,DAT_0049efb8,DAT_0049efe8,0x92,DAT_0049eff0);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0049eff4,DAT_0049eff4);
      }
      return 0;
    }
    if (*DAT_0049efc4 == local_14) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0049efbc,DAT_0049efb8,DAT_0049efe8,0x96,DAT_0049eff8);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0049effc,DAT_0049effc);
      }
      return 0;
    }
    *DAT_0049efc4 = local_14;
    iVar4 = FUN_0045a568();
    piVar2 = DAT_0049f000;
    if (iVar4 == 1) {
      if (*puVar1 == 2) {
        iVar4 = osKernelGetTickCount();
        *DAT_0049f000 = iVar4;
      }
      else if ((*puVar1 == 1) && (*DAT_0049f000 != 0)) {
        iVar4 = osKernelGetTickCount();
        uVar5 = iVar4 - *piVar2;
        local_1c = uVar5;
        FUN_0048eb32(DAT_0049f004,1,&local_1c);
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,DAT_0049efbc,DAT_0049efb8,DAT_0049efe8,0xa3,DAT_0049f008,uVar5);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_0049f00c,DAT_0049f00c,uVar5);
        }
        *piVar2 = 0;
      }
    }
    FUN_0049ebb6(*puVar1 & 0xff);
  }
  else if (local_18[0] == '\x03') {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      local_1c = local_14 & 0xffff;
      FUN_0043d574(3,DAT_0049efbc,DAT_0049efb8,DAT_0049efe8,0xad,DAT_0049f010,local_14 >> 0x10);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_0049f014,DAT_0049f014,local_14 >> 0x10,local_14 & 0xffff);
    }
    if (local_14 >> 0x10 == 2) {
      *DAT_0049f018 = local_14 & 0xffff;
    }
    else if (local_14 >> 0x10 == 1) {
      *DAT_0049f01c = local_14 & 0xffff;
    }
    iVar4 = FUN_0045a568();
    if (iVar4 == 2) {
      if (*DAT_0049efc4 == 0) {
        FUN_0049eae2(5,0);
      }
      return 0;
    }
    if (*DAT_0049f018 == 0) {
      FUN_0049eae2(4,0);
    }
    else if ((*DAT_0049f01c == 2) && (*DAT_0049f018 == 2)) {
      FUN_0049eae2(2,2);
    }
    else if ((*DAT_0049f01c == 1) && (*DAT_0049f018 == 1)) {
      FUN_0049eae2(2,1);
    }
  }
  else if (local_18[0] == '\x04') {
    iVar4 = FUN_0045a568();
    if (iVar4 != 2) {
      return 0;
    }
    cVar3 = FUN_00502dae();
    if (cVar3 != '\0') {
      FUN_0049eae2(3,cVar3);
    }
  }
  else if (local_18[0] == '\x05') {
    iVar4 = FUN_0045a568();
    if (iVar4 != 1) {
      return 0;
    }
    if (*DAT_0049efc4 != 0) {
      FUN_0049eae2(2,*DAT_0049efc4);
    }
  }
  return 0;
}

