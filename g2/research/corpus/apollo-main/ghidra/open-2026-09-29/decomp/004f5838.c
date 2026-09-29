
char FUN_004f5838(void)

{
  ushort *puVar1;
  int iVar2;
  int iVar3;
  char cVar4;
  uint uVar5;
  int iVar6;
  undefined4 uVar7;
  int iVar8;
  ushort uVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iStack_20;
  
  iVar6 = DAT_004f61f0;
  FUN_0043c0e4(DAT_004f61f0,0x1220,0);
  puVar1 = DAT_004f5c3c;
  iStack_20 = 0;
  uVar9 = *DAT_004f5c3c;
  cVar4 = FUN_004f5662(iVar6,0x14,&iStack_20,2);
  if (cVar4 == '\0') {
    if (0 < iStack_20) {
      if (0x28 < (int)(iStack_20 + (uint)uVar9)) {
        iVar10 = iStack_20 + (uint)uVar9 + -0x28;
        for (iVar8 = 0; iVar3 = DAT_004f62fc, iVar2 = DAT_004f5c40, iVar8 < iVar10;
            iVar8 = iVar8 + 1) {
          for (iVar13 = 0; iVar13 < (int)(uint)*(ushort *)(DAT_004f62fc + 0x280);
              iVar13 = iVar13 + 1) {
            if (*(int *)(DAT_004f62fc + iVar13 * 0x10) == *(int *)(puVar1 + iVar8 * 0x94 + 0x8a)) {
              if (*(ushort *)(DAT_004f5c40 + 0x280) < 0x28) {
                *(int *)(DAT_004f5c40 + (uint)*(ushort *)(DAT_004f5c40 + 0x280) * 0x10) =
                     *(int *)(puVar1 + iVar8 * 0x94 + 0x8a);
                iVar11 = iVar3 + iVar13 * 0x10;
                uVar7 = *(undefined4 *)(iVar11 + 0xc);
                iVar12 = (uint)*(ushort *)(iVar2 + 0x280) * 0x10 + iVar2;
                *(undefined4 *)(iVar12 + 8) = *(undefined4 *)(iVar11 + 8);
                *(undefined4 *)(iVar12 + 0xc) = uVar7;
                *(short *)(iVar2 + 0x280) = *(short *)(iVar2 + 0x280) + 1;
                for (; iVar13 < (int)(*(ushort *)(iVar3 + 0x280) - 1); iVar13 = iVar13 + 1) {
                  uVar5 = 0;
                  do {
                    *(undefined1 *)(iVar13 * 0x10 + iVar3 + uVar5) =
                         *(undefined1 *)(iVar13 * 0x10 + iVar3 + uVar5 + 0x10);
                    uVar5 = uVar5 + 1;
                  } while (uVar5 < 0x10);
                }
                *(short *)(iVar3 + 0x280) = *(short *)(iVar3 + 0x280) + -1;
              }
              break;
            }
          }
        }
        if (*(short *)(DAT_004f5c40 + 0x280) != 0) {
          FUN_004f6328();
        }
        uVar7 = DAT_004f631c;
        uVar5 = (uint)uVar9 - iVar10;
        uVar9 = (ushort)uVar5;
        FUN_00439be4(DAT_004f631c,puVar1 + iVar10 * 0x94 + 4,(uVar5 & 0xffff) * 0x128);
        FUN_00439be4(puVar1 + 4,uVar7,(uVar5 & 0xffff) * 0x128);
      }
      for (iVar8 = 0; iVar8 < iStack_20; iVar8 = iVar8 + 1) {
        FUN_004f55e0(iVar8 * 0xe8 + iVar6,puVar1 + (iVar8 + (uint)uVar9) * 0x94 + 4);
      }
    }
    *DAT_004f62f4 = 3;
    *DAT_004f62f8 = iStack_20;
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004f6314,DAT_004f6310,DAT_004f6324,0x305,DAT_004f6320,iStack_20,*puVar1);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_004f6580,DAT_004f6580,iStack_20,*puVar1);
    }
    cVar4 = '\0';
  }
  return cVar4;
}

