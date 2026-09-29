
undefined8 TT_Load_Simple_Glyph(int param_1,int *param_2,uint param_3)

{
  byte bVar1;
  char cVar2;
  short sVar3;
  ushort uVar4;
  short *psVar5;
  byte *pbVar6;
  short *psVar7;
  short *psVar8;
  short sVar9;
  byte *pbVar10;
  int *piVar11;
  byte *pbVar12;
  byte *pbVar13;
  int iVar14;
  int iVar15;
  byte *pbVar16;
  int iVar17;
  uint uVar18;
  char *pcVar19;
  int iVar20;
  char *pcVar21;
  char *pcVar22;
  uint uVar23;
  uint uVar24;
  byte bVar25;
  uint uVar26;
  int *local_30;
  uint local_2c;
  int local_28;
  
  pcVar19 = *(char **)(param_1 + 0xc4);
  pbVar16 = *(byte **)(param_1 + 200);
  iVar17 = *(int *)(param_1 + 0xc);
  sVar3 = *(short *)(param_1 + 0x20);
  iVar15 = (int)sVar3;
  local_28 = 0;
  local_2c = param_3;
  if ((iVar15 == 0) ||
     ((uint)(iVar15 + (int)*(short *)(iVar17 + 0x38) + (int)*(short *)(iVar17 + 0x14)) <=
      *(uint *)(iVar17 + 8))) {
    iVar14 = 0;
  }
  else {
    iVar14 = FT_GlyphLoader_CheckPoints(iVar17,0,iVar15);
  }
  local_30 = param_2;
  if (iVar14 != 0) goto LAB_005ef8d2;
  psVar7 = *(short **)(iVar17 + 0x44);
  psVar5 = psVar7 + iVar15;
  if ((iVar15 < 0xfff) && (pcVar19 + iVar15 * 2 + 2 <= pbVar16)) {
    cVar2 = *pcVar19;
    sVar9 = CONCAT11(cVar2,pcVar19[1]);
    if (0 < iVar15) {
      *psVar7 = sVar9;
    }
    if (-1 < cVar2) {
      while( true ) {
        pcVar21 = pcVar19 + 2;
        psVar8 = psVar7 + 1;
        if (psVar5 <= psVar8) break;
        *psVar8 = CONCAT11(*pcVar21,pcVar19[3]);
        if (*psVar8 <= sVar9) goto LAB_005ef612;
        sVar9 = *psVar8;
        psVar7 = psVar8;
        pcVar19 = pcVar21;
      }
      iVar20 = 0;
      if ((iVar15 < 1) || (iVar20 = *psVar7 + 1, -1 < iVar20)) {
        if ((iVar20 == -4) ||
           ((uint)(iVar20 + 4 + (int)*(short *)(iVar17 + 0x3a) + (int)*(short *)(iVar17 + 0x16)) <=
            *(uint *)(iVar17 + 4))) {
          iVar14 = 0;
        }
        else {
          iVar14 = FT_GlyphLoader_CheckPoints(iVar17,iVar20 + 4,0);
        }
        if (iVar14 != 0) goto LAB_005ef8d2;
        *(undefined4 *)(*(int *)(param_1 + 8) + 0x8c) = 0;
        *(undefined4 *)(*(int *)(param_1 + 8) + 0x88) = 0;
        if (pcVar19 + 4 <= pbVar16) {
          pcVar22 = pcVar19 + 4;
          uVar4 = CONCAT11(*pcVar21,pcVar19[3]);
          if (-1 < (int)((uint)*(byte *)(param_1 + 0x10) << 0x1e)) {
            if ((int)pbVar16 - (int)pcVar22 < (int)(uint)uVar4) {
              iVar14 = 0x16;
              goto LAB_005ef8d2;
            }
            local_2c = *(uint *)(*(int *)(param_1 + 0x9c) + 0x188);
            local_30 = (int *)(uint)uVar4;
            iVar14 = Update_Max(*(undefined4 *)(*(int *)(param_1 + 0x9c) + 8),&local_2c,1,
                                *(int *)(param_1 + 0x9c) + 0x18c);
            *(uint *)(*(int *)(param_1 + 0x9c) + 0x188) = local_2c & 0xffff;
            if (iVar14 != 0) goto LAB_005ef8d2;
            *(uint *)(*(int *)(param_1 + 8) + 0x8c) = (uint)uVar4;
            *(undefined4 *)(*(int *)(param_1 + 8) + 0x88) =
                 *(undefined4 *)(*(int *)(param_1 + 0x9c) + 0x18c);
            if (uVar4 != 0) {
              local_30 = *(int **)(*(int *)(param_1 + 0x9c) + 0x18c);
              FUN_00439be4(local_30,pcVar22,uVar4);
            }
          }
          pbVar12 = *(byte **)(iVar17 + 0x40);
          pbVar10 = pbVar12 + iVar20;
          pbVar13 = (byte *)(pcVar22 + uVar4);
          while (pbVar6 = pbVar13, pbVar12 < pbVar10) {
            if (pbVar16 < pbVar6 + 1) goto LAB_005ef612;
            bVar1 = *pbVar6;
            *pbVar12 = bVar1;
            pbVar12 = pbVar12 + 1;
            pbVar13 = pbVar6 + 1;
            if ((int)((uint)bVar1 << 0x1c) < 0) {
              if (pbVar16 < pbVar6 + 2) goto LAB_005ef612;
              bVar25 = pbVar6[1];
              if (pbVar10 < pbVar12 + bVar25) goto LAB_005ef612;
              for (; pbVar13 = pbVar6 + 2, bVar25 != 0; bVar25 = bVar25 - 1) {
                *pbVar12 = bVar1;
                pbVar12 = pbVar12 + 1;
              }
            }
          }
          piVar11 = *(int **)(iVar17 + 0x3c);
          local_30 = piVar11 + iVar20 * 2;
          pbVar13 = *(byte **)(iVar17 + 0x40);
          iVar15 = 0;
          if (pbVar6 + local_28 <= pbVar16) {
            for (; piVar11 < local_30; piVar11 = piVar11 + 2) {
              uVar26 = 0;
              bVar1 = *pbVar13;
              uVar23 = (uint)bVar1;
              if ((int)(uVar23 << 0x1e) < 0) {
                if (pbVar16 < pbVar6 + 1) goto LAB_005ef612;
                uVar26 = (uint)*pbVar6;
                pbVar10 = pbVar6 + 1;
                if (-1 < (int)(uVar23 << 0x1b)) {
                  uVar26 = -uVar26;
                }
              }
              else {
                pbVar10 = pbVar6;
                if (-1 < (int)(uVar23 << 0x1b)) {
                  if (pbVar16 < pbVar6 + 2) goto LAB_005ef612;
                  pbVar10 = pbVar6 + 2;
                  uVar26 = (uint)CONCAT11(*pbVar6,pbVar6[1]);
                }
              }
              iVar15 = uVar26 + iVar15;
              *piVar11 = iVar15;
              *pbVar13 = bVar1 & 0xed;
              pbVar13 = pbVar13 + 1;
              pbVar6 = pbVar10;
            }
            uVar23 = *(uint *)(iVar17 + 0x3c);
            uVar26 = uVar23 + iVar20 * 8;
            pbVar13 = *(byte **)(iVar17 + 0x40);
            iVar15 = 0;
            for (; uVar23 < uVar26; uVar23 = uVar23 + 8) {
              uVar18 = 0;
              bVar1 = *pbVar13;
              uVar24 = (uint)bVar1;
              if ((int)(uVar24 << 0x1d) < 0) {
                if (pbVar16 < pbVar6 + 1) goto LAB_005ef612;
                uVar18 = (uint)*pbVar6;
                pbVar10 = pbVar6 + 1;
                if (-1 < (int)(uVar24 << 0x1a)) {
                  uVar18 = -uVar18;
                }
              }
              else {
                pbVar10 = pbVar6;
                if (-1 < (int)(uVar24 << 0x1a)) {
                  if (pbVar16 < pbVar6 + 2) goto LAB_005ef612;
                  pbVar10 = pbVar6 + 2;
                  uVar18 = (uint)CONCAT11(*pbVar6,pbVar6[1]);
                }
              }
              iVar15 = uVar18 + iVar15;
              *(int *)(uVar23 + 4) = iVar15;
              *pbVar13 = bVar1 & 1;
              pbVar13 = pbVar13 + 1;
              pbVar6 = pbVar10;
            }
            *(short *)(iVar17 + 0x3a) = (short)iVar20;
            *(short *)(iVar17 + 0x38) = sVar3;
            *(byte **)(param_1 + 0xc4) = pbVar6;
            goto LAB_005ef8d2;
          }
        }
      }
    }
  }
LAB_005ef612:
  iVar14 = 0x14;
LAB_005ef8d2:
  return CONCAT44(local_30,iVar14);
}

