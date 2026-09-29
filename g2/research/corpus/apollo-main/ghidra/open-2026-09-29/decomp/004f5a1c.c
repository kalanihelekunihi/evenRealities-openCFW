
char FUN_004f5a1c(void)

{
  ushort uVar1;
  ushort *puVar2;
  int iVar3;
  int iVar4;
  char cVar5;
  uint uVar6;
  int iVar7;
  undefined4 uVar8;
  int iVar9;
  undefined4 in_r3;
  uint uVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int local_28;
  undefined4 uStack_24;
  
  iVar7 = DAT_004f61f0;
  uStack_24 = in_r3;
  FUN_0043c0e4(DAT_004f61f0,0x1220,0);
  puVar2 = DAT_004f5c3c;
  local_28 = 0;
  uVar1 = *DAT_004f5c3c;
  uVar10 = (uint)uVar1;
  cVar5 = FUN_004f5662(0,0x14,&local_28,2);
  uVar8 = DAT_004f631c;
  if (cVar5 == '\0') {
    if (0 < local_28) {
      if ((int)(local_28 + (uint)uVar1) < 0x29) {
        FUN_00439be4(DAT_004f631c,puVar2 + 4,(uint)uVar1 * 0x128);
        FUN_00439be4(puVar2 + local_28 * 0x94 + 4,uVar8,(uint)uVar1 * 0x128);
      }
      else {
        iVar11 = local_28 + (uint)uVar1 + -0x28;
        for (iVar9 = (uint)uVar1 - iVar11; iVar4 = DAT_004f62fc, iVar3 = DAT_004f5c40,
            iVar9 < (int)(uint)uVar1; iVar9 = iVar9 + 1) {
          for (iVar14 = 0; iVar14 < (int)(uint)*(ushort *)(DAT_004f62fc + 0x280);
              iVar14 = iVar14 + 1) {
            if (*(int *)(DAT_004f62fc + iVar14 * 0x10) == *(int *)(puVar2 + iVar9 * 0x94 + 0x8a)) {
              if (*(ushort *)(DAT_004f5c40 + 0x280) < 0x28) {
                *(int *)(DAT_004f5c40 + (uint)*(ushort *)(DAT_004f5c40 + 0x280) * 0x10) =
                     *(int *)(puVar2 + iVar9 * 0x94 + 0x8a);
                iVar12 = iVar4 + iVar14 * 0x10;
                uVar8 = *(undefined4 *)(iVar12 + 0xc);
                iVar13 = (uint)*(ushort *)(iVar3 + 0x280) * 0x10 + iVar3;
                *(undefined4 *)(iVar13 + 8) = *(undefined4 *)(iVar12 + 8);
                *(undefined4 *)(iVar13 + 0xc) = uVar8;
                *(short *)(iVar3 + 0x280) = *(short *)(iVar3 + 0x280) + 1;
                for (; iVar14 < (int)(*(ushort *)(iVar4 + 0x280) - 1); iVar14 = iVar14 + 1) {
                  uVar6 = 0;
                  do {
                    *(undefined1 *)(iVar14 * 0x10 + iVar4 + uVar6) =
                         *(undefined1 *)(iVar14 * 0x10 + iVar4 + uVar6 + 0x10);
                    uVar6 = uVar6 + 1;
                  } while (uVar6 < 0x10);
                }
                *(short *)(iVar4 + 0x280) = *(short *)(iVar4 + 0x280) + -1;
              }
              break;
            }
          }
        }
        if (*(short *)(DAT_004f5c40 + 0x280) != 0) {
          FUN_004f6328();
        }
        uVar8 = DAT_004f631c;
        uVar10 = uVar10 - iVar11;
        FUN_00439be4(DAT_004f631c,puVar2 + 4,(uVar10 & 0xffff) * 0x128);
        FUN_00439be4(puVar2 + iVar11 * 0x94 + 4,uVar8,(uVar10 & 0xffff) * 0x128);
      }
      for (iVar9 = 0; iVar9 < local_28; iVar9 = iVar9 + 1) {
        FUN_004f55e0(iVar9 * 0xe8 + iVar7,puVar2 + iVar9 * 0x94 + 4);
      }
    }
    *DAT_004f62f4 = 2;
    *DAT_004f62f8 = local_28;
    iVar7 = FUN_0043d0ce();
    if (iVar7 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004f6314,DAT_004f6310,DAT_004f6588,0x36b,DAT_004f6584,local_28,
                   uVar10 & 0xffff);
    }
    iVar7 = FUN_0043d0ce();
    if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_004f675c,DAT_004f675c,local_28,uVar10 & 0xffff);
    }
    cVar5 = '\0';
  }
  return cVar5;
}

