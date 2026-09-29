
void FUN_00438924(short *param_1,uint param_2,int param_3,undefined2 *param_4)

{
  short sVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  short sVar6;
  short sVar7;
  short sVar8;
  short sVar9;
  short sVar10;
  short sVar11;
  short sVar12;
  short sVar13;
  short sVar14;
  short sVar15;
  short sVar16;
  short *psVar17;
  short *psVar18;
  int iVar19;
  uint uVar20;
  undefined2 *puVar21;
  int iVar22;
  uint uVar23;
  int iVar24;
  int iVar25;
  int in_r12;
  int iVar26;
  
  iVar26 = (int)param_1[-2];
  iVar19 = (int)param_1[-1];
  uVar20 = param_2 & 0xfffffff8;
  iVar22 = 0;
  psVar17 = param_1 + 1;
  iVar24 = (int)*param_1;
  if (0 < (int)uVar20) {
    sVar1 = *(short *)(&DAT_00438bd6 + param_3 * 8);
    iVar25 = param_3 * 8;
    sVar2 = *(short *)(&DAT_00438bd4 + iVar25);
    sVar3 = *(short *)(&DAT_00438bd2 + iVar25);
    sVar4 = *(short *)(&DAT_00438bd6 + iVar25);
    sVar5 = *(short *)(&DAT_00438bd4 + iVar25);
    sVar6 = *(short *)(&DAT_00438bd2 + iVar25);
    sVar7 = *(short *)(&DAT_00438bd6 + iVar25);
    sVar8 = *(short *)(&DAT_00438bd4 + iVar25);
    sVar9 = *(short *)(&DAT_00438bd2 + iVar25);
    sVar10 = *(short *)(&DAT_00438bd6 + iVar25);
    sVar11 = *(short *)(&DAT_00438bd4 + iVar25);
    sVar12 = *(short *)(&DAT_00438bd2 + iVar25);
    sVar13 = *(short *)(&DAT_00438bd0 + param_3 * 8);
    do {
      sVar14 = *(short *)(&DAT_00438bd0 + param_3 * 8);
      sVar15 = *(short *)(&DAT_00438bd0 + param_3 * 8);
      iVar25 = (int)sVar15;
      sVar16 = *(short *)(&DAT_00438bd0 + param_3 * 8);
      uVar23 = 0;
      psVar18 = psVar17;
      puVar21 = param_4;
      do {
        psVar17 = psVar18;
        switch(uVar23 & 3) {
        case 0:
          psVar17 = psVar18 + 1;
          in_r12 = (int)*psVar18;
          iVar25 = sVar1 * iVar26 + sVar2 * iVar19 + (int)sVar14 * (int)*psVar18 + sVar3 * iVar24;
          break;
        case 1:
          psVar17 = psVar18 + 1;
          iVar26 = (int)*psVar18;
          iVar25 = sVar4 * iVar19 + sVar5 * iVar24 + (int)sVar15 * (int)*psVar18 + sVar6 * in_r12;
          break;
        case 2:
          psVar17 = psVar18 + 1;
          iVar19 = (int)*psVar18;
          iVar25 = sVar7 * iVar24 + sVar8 * in_r12 + (int)sVar16 * (int)*psVar18 + sVar9 * iVar26;
          break;
        case 3:
          psVar17 = psVar18 + 1;
          iVar24 = (int)*psVar18;
          iVar25 = sVar10 * in_r12 + sVar11 * iVar26 + (int)sVar13 * (int)*psVar18 + sVar12 * iVar19
          ;
        }
        iVar25 = iVar25 >> 0xf;
        uVar23 = uVar23 + 1;
        param_4 = puVar21 + 1;
        *puVar21 = (short)iVar25;
        psVar18 = psVar17;
        puVar21 = param_4;
      } while ((int)uVar23 < 8);
      iVar22 = iVar22 + 8;
    } while (iVar22 < (int)uVar20);
  }
  if ((int)uVar20 < (int)param_2) {
    iVar22 = param_3 * 8;
    sVar1 = *(short *)(&DAT_00438bd6 + iVar22);
    sVar2 = *(short *)(&DAT_00438bd4 + iVar22);
    sVar3 = *(short *)(&DAT_00438bd2 + iVar22);
    sVar4 = *(short *)(&DAT_00438bd6 + iVar22);
    sVar5 = *(short *)(&DAT_00438bd4 + iVar22);
    sVar6 = *(short *)(&DAT_00438bd2 + iVar22);
    sVar7 = *(short *)(&DAT_00438bd6 + iVar22);
    sVar8 = *(short *)(&DAT_00438bd4 + iVar22);
    sVar9 = *(short *)(&DAT_00438bd2 + iVar22);
    sVar10 = *(short *)(&DAT_00438bd6 + iVar22);
    sVar11 = *(short *)(&DAT_00438bd4 + iVar22);
    sVar12 = *(short *)(&DAT_00438bd2 + iVar22);
    iVar22 = (int)sVar12;
    sVar14 = *(short *)(&DAT_00438bd0 + param_3 * 8);
    sVar13 = *(short *)(&DAT_00438bd0 + param_3 * 8);
    do {
      psVar18 = psVar17;
      switch(uVar20 & 3) {
      case 0:
        psVar18 = psVar17 + 1;
        in_r12 = (int)*psVar17;
        iVar22 = sVar1 * iVar26 + sVar2 * iVar19 + (int)sVar14 * (int)*psVar17 + sVar3 * iVar24;
        break;
      case 1:
        psVar18 = psVar17 + 1;
        iVar26 = (int)*psVar17;
        iVar22 = sVar4 * iVar19 + sVar5 * iVar24 + (int)sVar13 * (int)*psVar17 + sVar6 * in_r12;
        break;
      case 2:
        psVar18 = psVar17 + 1;
        iVar19 = (int)*psVar17;
        iVar22 = sVar7 * iVar24 + sVar8 * in_r12 + (int)sVar13 * (int)*psVar17 + sVar9 * iVar26;
        break;
      case 3:
        psVar18 = psVar17 + 1;
        iVar24 = (int)*psVar17;
        iVar22 = sVar10 * in_r12 + sVar11 * iVar26 + (int)sVar13 * (int)*psVar17 + sVar12 * iVar19;
      }
      iVar22 = iVar22 >> 0xf;
      uVar20 = uVar20 + 1;
      *param_4 = (short)iVar22;
      psVar17 = psVar18;
      param_4 = param_4 + 1;
    } while ((int)uVar20 < (int)param_2);
  }
  return;
}

