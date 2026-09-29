
undefined4 SVC_KvdbWriteMenuConfigureValue(void)

{
  bool bVar1;
  int *piVar2;
  int *piVar3;
  uint *puVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  
  puVar4 = DAT_00492c7c;
  piVar3 = DAT_00492c78;
  piVar2 = DAT_00492c28;
  if ((*DAT_00492c78 != 1) || ((int)*DAT_00492c7c < 1)) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00492bf8,DAT_00492bf4,DAT_00492c8c,0xc4,DAT_00492cac,*piVar3,*DAT_00492c7c)
      ;
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x8800000,DAT_00492cb0,DAT_00492cb0,*piVar3,*DAT_00492c7c);
    }
    return 0xffffffff;
  }
  FUN_0043c0e4(DAT_00492c28,0x378,0);
  uVar8 = DAT_00492c2c;
  iVar5 = SVC_KvdbBlobRead(DAT_00492c2c,piVar2,0x378);
  if ((0 < iVar5) && (*piVar2 == DAT_00492c30)) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00492bf8,DAT_00492bf4,DAT_00492c8c,0x9d,DAT_00492c88,(char)piVar2[1]);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00492c90,DAT_00492c90,(char)piVar2[1]);
    }
    if ((uint)*(byte *)(piVar2 + 1) == *puVar4) {
      bVar1 = true;
      for (iVar5 = 0; iVar5 < (int)*puVar4; iVar5 = iVar5 + 1) {
        if (((((char)piVar2[iVar5 * 0xb + 2] != *(char *)(iVar5 * 0x34 + DAT_00492c40 + 0x28)) ||
             (piVar2[iVar5 * 0xb + 0xc] != *(int *)(iVar5 * 0x34 + DAT_00492c40 + 0x30))) ||
            (piVar2[iVar5 * 0xb + 3] != *(int *)(iVar5 * 0x34 + DAT_00492c40 + 0x2c))) ||
           (iVar6 = FUN_0046cacc(piVar2 + iVar5 * 0xb + 4,iVar5 * 0x34 + DAT_00492c40 + 4),
           iVar6 != 0)) {
          bVar1 = false;
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00492bf8,DAT_00492bf4,DAT_00492c8c,0xaa,DAT_00492c94,iVar5);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_00492c98,DAT_00492c98,iVar5);
          }
          break;
        }
      }
      if (bVar1) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(3,DAT_00492bf8,DAT_00492bf4,DAT_00492c8c,0xb1,DAT_00492c9c);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_00492ca0,DAT_00492ca0);
        }
        return 0;
      }
    }
  }
  FUN_0043c0e4(piVar2,0x378,0);
  FUN_0046018e();
  *piVar2 = DAT_00492c30;
  *(char *)(piVar2 + 1) = (char)*puVar4;
  for (iVar5 = 0; iVar6 = DAT_00492c40, iVar5 < (int)*puVar4; iVar5 = iVar5 + 1) {
    *(undefined1 *)(piVar2 + iVar5 * 0xb + 2) = *(undefined1 *)(iVar5 * 0x34 + DAT_00492c40 + 0x28);
    piVar2[iVar5 * 0xb + 3] = *(int *)(iVar5 * 0x34 + iVar6 + 0x2c);
    uVar7 = FUN_0044a43c(iVar5 * 0x34 + iVar6 + 4);
    FUN_00439be4(piVar2 + iVar5 * 0xb + 4,iVar5 * 0x34 + iVar6 + 4,uVar7);
    piVar2[iVar5 * 0xb + 0xc] = *(int *)(iVar6 + iVar5 * 0x34 + 0x30);
  }
  FUN_004601ea();
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00492bf8,DAT_00492bf4,DAT_00492c8c,199,DAT_00492ca4);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00492ca8,DAT_00492ca8);
  }
  uVar8 = SVC_KvdbBlobWrite(uVar8,piVar2,0x378);
  return uVar8;
}

