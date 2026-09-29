
void FUN_00438bf0(int param_1,int param_2,longlong *param_3,int param_4,undefined2 *param_5,
                 int param_6)

{
  short sVar1;
  short sVar2;
  longlong lVar3;
  longlong lVar4;
  int iVar5;
  int iVar6;
  short *psVar7;
  short *psVar8;
  short *psVar9;
  short *psVar10;
  short *psVar11;
  short *psVar12;
  short *psVar13;
  short *psVar14;
  short *psVar15;
  short *psVar16;
  short *psVar17;
  short *psVar18;
  short *psVar19;
  short *psVar20;
  short *psVar21;
  uint uVar22;
  short *psVar23;
  short *psVar24;
  short *psVar25;
  short *psVar26;
  short *psVar27;
  short *psVar28;
  short *psVar29;
  short *psVar30;
  short *psVar31;
  short *psVar32;
  short *psVar33;
  short *psVar34;
  short *psVar35;
  short *psVar36;
  short *psVar37;
  int iVar38;
  int iVar39;
  
  iVar5 = (0x78 / param_1) * 2;
  iVar6 = 0;
  if (0 < param_6 * 0xf) {
    lVar3 = *param_3;
    lVar4 = param_3[1];
    do {
      iVar39 = 0;
      psVar7 = (short *)(param_2 + iVar5 * (iVar6 - param_1 * (iVar6 / param_1)) * 2);
      psVar23 = (short *)(param_4 + (iVar5 + -1) * -2 + (iVar6 / param_1) * 2);
      iVar38 = 0;
      if (0 < iVar5) {
        do {
          psVar24 = psVar23 + 1;
          sVar1 = *psVar23;
          psVar8 = psVar7 + 1;
          sVar2 = *psVar7;
          psVar25 = psVar23 + 2;
          psVar9 = psVar7 + 2;
          psVar26 = psVar23 + 3;
          psVar10 = psVar7 + 3;
          psVar27 = psVar23 + 4;
          psVar11 = psVar7 + 4;
          psVar28 = psVar23 + 5;
          psVar12 = psVar7 + 5;
          psVar29 = psVar23 + 6;
          psVar13 = psVar7 + 6;
          psVar30 = psVar23 + 7;
          psVar14 = psVar7 + 7;
          psVar31 = psVar23 + 8;
          psVar15 = psVar7 + 8;
          psVar32 = psVar23 + 9;
          psVar16 = psVar7 + 9;
          psVar33 = psVar23 + 10;
          psVar17 = psVar7 + 10;
          psVar34 = psVar23 + 0xb;
          psVar18 = psVar7 + 0xb;
          psVar35 = psVar23 + 0xc;
          psVar19 = psVar7 + 0xc;
          psVar36 = psVar23 + 0xd;
          psVar20 = psVar7 + 0xd;
          psVar37 = psVar23 + 0xe;
          psVar21 = psVar7 + 0xe;
          psVar23 = psVar23 + 0xf;
          psVar7 = psVar7 + 0xf;
          iVar38 = iVar38 + 0xf;
          iVar39 = (int)*psVar37 * (int)*psVar21 +
                   (int)*psVar36 * (int)*psVar20 +
                   (int)*psVar35 * (int)*psVar19 +
                   (int)*psVar34 * (int)*psVar18 +
                   (int)*psVar33 * (int)*psVar17 +
                   (int)*psVar32 * (int)*psVar16 +
                   (int)*psVar31 * (int)*psVar15 +
                   (int)*psVar30 * (int)*psVar14 +
                   (int)*psVar29 * (int)*psVar13 +
                   (int)*psVar28 * (int)*psVar12 +
                   (int)*psVar27 * (int)*psVar11 +
                   (int)*psVar26 * (int)*psVar10 +
                   (int)*psVar25 * (int)*psVar9 +
                   (int)*psVar24 * (int)*psVar8 + (int)sVar1 * (int)sVar2 + iVar39;
        } while (iVar38 < iVar5);
      }
      lVar3 = lVar3 + (longlong)DAT_00438fa4 * (longlong)iVar39;
      uVar22 = (uint)lVar3 >> 0x1e | (int)((ulonglong)lVar3 >> 0x20) * 4;
      lVar3 = ((longlong)DAT_00438fa8 * (longlong)iVar39 + lVar4) -
              (longlong)DAT_00438fa0 * (longlong)(int)uVar22;
      lVar4 = (longlong)DAT_00438fa4 * (longlong)iVar39 -
              (longlong)DAT_00438fac * (longlong)(int)uVar22;
      *param_5 = (short)(uVar22 + 0x8000 >> 0x10);
      iVar6 = iVar6 + 0xf;
      param_5 = param_5 + 1;
    } while (iVar6 < param_6 * 0xf);
    *param_3 = lVar3;
    param_3[1] = lVar4;
  }
  return;
}

