
undefined4
_evenOtaBootloaderWriteFile2MRAM(undefined4 param_1,int param_2,undefined4 param_3,int param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  
  iVar3 = param_2;
  iVar2 = FUN_0043d0ce(0);
  if (iVar2 << 0x1e < 0) {
    iVar3 = DAT_004455d0;
    param_3 = param_1;
    param_4 = param_2;
    FUN_0043d574(3,DAT_004455b0,DAT_004455ac,DAT_004455d4,0x358,DAT_004455d0,param_1,param_2);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc800000,DAT_004455d8,DAT_004455d8,param_1,param_2,iVar3,param_3,param_4);
  }
  iVar3 = osKernelGetTickCount();
  uVar4 = semantic_OtaSelectFlashOps(1);
  piVar1 = DAT_004455dc;
  iVar2 = file_open(param_1,uVar4);
  *piVar1 = iVar2;
  if (*piVar1 == 0) {
    *(undefined1 *)(piVar1 + 1) = 0;
  }
  else {
    *(undefined1 *)(piVar1 + 1) = 1;
  }
  uVar5 = semantic_OtaFileSize(*piVar1);
  if (uVar5 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004455b0,DAT_004455ac,DAT_004455d4,0x363,DAT_004455e0,param_1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004455e4,DAT_004455e4,param_1);
    }
    if (*piVar1 == 0) {
      uVar4 = 0;
    }
    else {
      uVar4 = file_close(*piVar1);
      *piVar1 = 0;
    }
  }
  else {
    for (uVar6 = 0; uVar4 = DAT_0044558c, uVar6 < uVar5; uVar6 = uVar6 + 0x1000) {
      uVar7 = 0x1000;
      if (uVar5 < uVar6 + 0x1000) {
        uVar7 = uVar5 - uVar6;
      }
      file_read(DAT_0044558c,1,uVar7,*piVar1);
      semantic_OtaBufferedFlashWrite(uVar7 & 0xffff,uVar4,uVar6 + param_2,1);
    }
    if (*piVar1 != 0) {
      file_close(*piVar1);
      *piVar1 = 0;
    }
    iVar2 = FUN_0043d0ce(0);
    if (iVar2 << 0x1e < 0) {
      iVar2 = osKernelGetTickCount();
      FUN_0043d574(3,DAT_004455b0,DAT_004455ac,DAT_004455d4,0x381,DAT_004455e8,iVar2 - iVar3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      iVar2 = osKernelGetTickCount();
      compress_log_output(0xc400000,DAT_004455ec,DAT_004455ec,iVar2 - iVar3);
    }
    uVar4 = 0;
  }
  return uVar4;
}

