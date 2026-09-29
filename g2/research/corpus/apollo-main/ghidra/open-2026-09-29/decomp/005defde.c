
int FUN_005defde(int param_1,int param_2,uint param_3)

{
  short sVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  int iVar10;
  uint uVar11;
  byte *pbVar12;
  byte *pbVar13;
  uint uVar14;
  uint uVar15;
  
  uVar5 = *(int *)(param_1 + 0x308) + *(int *)(param_1 + 0x304);
  uVar11 = 1;
  iVar6 = *(int *)(param_1 + 0x30c);
  uVar8 = *(int *)(param_1 + 0x304) + 4;
  iVar10 = 0;
  do {
    if ((iVar6 == 0) || (uVar5 < uVar8 + 6)) {
      return iVar10;
    }
    uVar9 = uVar8 + CONCAT11(*(undefined1 *)(uVar8 + 2),*(undefined1 *)(uVar8 + 3));
    if (uVar5 < uVar9) {
      uVar9 = uVar5;
    }
    iVar4 = iVar10;
    if ((*(uint *)(param_1 + 0x310) & uVar11) != 0) {
      uVar2 = (uint)CONCAT11(*(undefined1 *)(uVar8 + 6),*(undefined1 *)(uVar8 + 7));
      pbVar12 = (byte *)(uVar8 + 0xe);
      if ((int)(uVar9 - (int)pbVar12) < (int)(uVar2 * 6)) {
        uVar2 = (int)(uVar9 - (int)pbVar12) / 6;
      }
      if (*(char *)(uVar8 + 4) == '\0') {
        uVar7 = param_3 | param_2 << 0x10;
        if ((*(uint *)(param_1 + 0x314) & uVar11) == 0) {
LAB_005df118:
          if (uVar2 != 0) {
            if (((uint)pbVar12[3] |
                (uint)pbVar12[1] << 0x10 | (uint)*pbVar12 << 0x18 | (uint)pbVar12[2] << 8) != uVar7)
            break;
            sVar1 = CONCAT11(pbVar12[4],pbVar12[5]);
LAB_005df100:
            iVar4 = (int)sVar1;
            if (-1 < (int)((uint)CONCAT11(*(char *)(uVar8 + 4),*(undefined1 *)(uVar8 + 5)) << 0x1c))
            {
              iVar4 = iVar4 + iVar10;
            }
          }
          goto LAB_005df006;
        }
        uVar15 = 0;
        while (uVar3 = uVar2, uVar15 < uVar3) {
          uVar2 = uVar3 + uVar15 >> 1;
          pbVar13 = pbVar12 + uVar2 * 6;
          uVar14 = (uint)pbVar13[3] |
                   (uint)pbVar13[1] << 0x10 | (uint)*pbVar13 << 0x18 | (uint)pbVar13[2] << 8;
          if (uVar14 == uVar7) {
            sVar1 = CONCAT11(pbVar13[4],pbVar13[5]);
            goto LAB_005df100;
          }
          if (uVar14 < uVar7) {
            uVar15 = uVar2 + 1;
            uVar2 = uVar3;
          }
        }
      }
    }
LAB_005df006:
    iVar6 = iVar6 + -1;
    uVar11 = uVar11 << 1;
    uVar8 = uVar9;
    iVar10 = iVar4;
  } while( true );
  pbVar12 = pbVar12 + 6;
  uVar2 = uVar2 - 1;
  goto LAB_005df118;
}

