
/* WARNING: Removing unreachable block (ram,0x00445380) */

int _otaFsHealthProbe(void)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  
  iVar7 = -1;
  iVar2 = file_heap_allocate(0x1000);
  iVar3 = file_heap_allocate(0x1000);
  if ((iVar2 == 0) || (iVar3 == 0)) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004455b0,DAT_004455ac,DAT_004455f4,0x3a7,DAT_004455f0);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004455f8,DAT_004455f8);
    }
  }
  else {
    for (uVar5 = 0; uVar1 = DAT_00445600, uVar5 < 0x400; uVar5 = uVar5 + 1) {
      *(uint *)(iVar2 + uVar5 * 4) = DAT_004455fc ^ uVar5;
    }
    file_remove(DAT_00445600);
    iVar4 = file_open(uVar1,&DAT_00445424);
    if (iVar4 == 0) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004455b0,DAT_004455ac,DAT_004455f4,0x3b4,DAT_00445604);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00445608);
      }
    }
    else {
      iVar6 = file_write(iVar2,1,0x1000,iVar4);
      file_close(iVar4);
      if (iVar6 == 0x1000) {
        iVar4 = file_open(uVar1,&DAT_00445428);
        if (iVar4 == 0) {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004455b0,DAT_004455ac,DAT_004455f4,0x3c1,DAT_00445614);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_00445618,DAT_00445618);
          }
        }
        else {
          iVar6 = file_read(iVar3,1,0x1000,iVar4);
          file_close(iVar4);
          if (iVar6 == 0x1000) {
            iVar4 = FUN_004751c8(iVar2,iVar3,0x1000);
            if (iVar4 == 0) {
              iVar7 = 0;
            }
            else {
              iVar4 = FUN_0043d0ce();
              if (iVar4 << 0x1e < 0) {
                FUN_0043d574(1,DAT_004455b0,DAT_004455ac,DAT_004455f4,0x3cd,DAT_00445624);
              }
              iVar4 = FUN_0043d0ce();
              if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
                compress_log_output(0x4000000,DAT_00445628,DAT_00445628);
              }
            }
          }
          else {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              FUN_0043d574(1,DAT_004455b0,DAT_004455ac,DAT_004455f4,0x3c8,DAT_0044561c,iVar6,0x1000)
              ;
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0x4800000,DAT_00445620,DAT_00445620,iVar6,0x1000);
            }
          }
        }
      }
      else {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004455b0,DAT_004455ac,DAT_004455f4,0x3bb,DAT_0044560c,iVar6,0x1000);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_00445610,DAT_00445610,iVar6,0x1000);
        }
      }
    }
  }
  file_remove(DAT_00445600);
  if (iVar2 != 0) {
    file_heap_free(iVar2);
  }
  if (iVar3 != 0) {
    file_heap_free(iVar3);
  }
  if (iVar7 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004455b0,DAT_004455ac,DAT_004455f4,0x3dc,DAT_0044562c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00445630,DAT_00445630);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004455b0,DAT_004455ac,DAT_004455f4,0x3de,DAT_00445634);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00445638,DAT_00445638);
    }
  }
  return iVar7;
}

