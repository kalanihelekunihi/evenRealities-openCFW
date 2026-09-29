
undefined4 _fileCaculateCRC(int *param_1,undefined4 param_2,uint *param_3,undefined4 *param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  
  iVar5 = -1;
  uVar1 = semantic_OtaSelectFlashOps(1);
  iVar2 = file_open(param_2,uVar1);
  *param_1 = iVar2;
  if (*param_1 == 0) {
    *(undefined1 *)(DAT_00448660 + 4) = 0;
  }
  else {
    iVar5 = 0;
    *(undefined1 *)(DAT_00448660 + 4) = 1;
  }
  if (-1 < iVar5) {
    uVar3 = semantic_OtaFileSize(*param_1);
    if ((int)uVar3 < 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004487a4,DAT_0044877c,DAT_00448668,0x67d,DAT_0044866c,param_2,uVar3);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_004486e8,DAT_004486e8,param_2,uVar3);
      }
      if (*param_1 == 0) {
        iVar2 = 0;
      }
      else {
        iVar2 = file_close(*param_1);
        *param_1 = 0;
      }
      if (iVar2 < 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004487a4,DAT_0044877c,DAT_00448668,0x680,DAT_004487d4,param_2,iVar2);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_004487d8,DAT_004487d8,param_2,iVar2);
        }
      }
      return 0;
    }
    *param_3 = uVar3;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004487a4,DAT_0044877c,DAT_00448668,0x686,DAT_00448748,*param_3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00448780,DAT_00448780,*param_3);
    }
    for (uVar3 = 0; uVar1 = DAT_004487a8, uVar3 < *param_3 >> 0xc; uVar3 = uVar3 + 1) {
      iVar2 = file_read(DAT_004487a8,1,0x1000,*param_1);
      if (iVar2 != 0x1000) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004487a4,DAT_0044877c,DAT_00448668,0x68b,DAT_004487dc,iVar2);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_004487e0,DAT_004487e0,iVar2);
        }
        if (*param_1 == 0) {
          iVar2 = 0;
        }
        else {
          iVar2 = file_close(*param_1);
          *param_1 = 0;
        }
        if (iVar2 < 0) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004487a4,DAT_0044877c,DAT_00448668,0x68e,DAT_004487d4,param_2,iVar2);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_004487d8,DAT_004487d8,param_2,iVar2);
          }
        }
        return 0;
      }
      FUN_0047cbc4(uVar1,0x1000,param_4);
    }
    uVar3 = *param_3 & 0xfff;
    if (uVar3 != 0) {
      uVar4 = file_read(DAT_004487a8,1,uVar3,*param_1);
      if (uVar4 != uVar3) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004487a4,DAT_0044877c,DAT_00448668,0x699,DAT_00448844,uVar4,uVar3);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_00448848,DAT_00448848,uVar4,uVar3);
        }
        if (*param_1 == 0) {
          iVar2 = 0;
        }
        else {
          iVar2 = file_close(*param_1);
          *param_1 = 0;
        }
        if (iVar2 < 0) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004487a4,DAT_0044877c,DAT_00448668,0x69c,DAT_004487d4,param_2,iVar2);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_004487d8,DAT_004487d8,param_2,iVar2);
          }
        }
        return 0;
      }
      FUN_0047cbc4(uVar1,uVar3,param_4);
    }
    if (*param_1 == 0) {
      iVar2 = 0;
    }
    else {
      iVar2 = file_close(*param_1);
      *param_1 = 0;
    }
    if (iVar2 < 0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004487a4,DAT_0044877c,DAT_00448668,0x6a4,DAT_004487d4,param_2,iVar2);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_004487d8,DAT_004487d8,param_2,iVar2);
      }
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004487a4,DAT_0044877c,DAT_00448668,0x6a6,DAT_00448850,param_2,*param_3,
                   *param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_00448854,DAT_00448854,param_2,*param_3,*param_4);
    }
    return 1;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(1,DAT_004487a4,DAT_0044877c,DAT_00448668,0x677,DAT_00448664,param_2,iVar5);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x4800000,DAT_004486e4,DAT_004486e4,param_2,iVar5);
  }
  return 0;
}

