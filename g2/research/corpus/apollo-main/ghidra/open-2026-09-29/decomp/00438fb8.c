
/* WARNING: Instruction at (ram,0x004391fe) overlaps instruction at (ram,0x004391fc)
    */

int FUN_00438fb8(uint param_1,byte param_2,char *param_3,undefined4 param_4,char *param_5)

{
  short *psVar1;
  short *psVar2;
  short *psVar3;
  short sVar4;
  char cVar5;
  int iVar6;
  short *psVar7;
  uint uVar8;
  undefined4 uVar9;
  uint uVar10;
  float *pfVar11;
  char *pcVar12;
  uint uVar13;
  int iVar14;
  char *pcVar15;
  int iVar16;
  float fVar17;
  int iVar18;
  float fVar19;
  short *psVar20;
  uint uVar21;
  bool bVar22;
  float fVar23;
  float fVar24;
  float fVar25;
  float fVar26;
  float local_290;
  char *local_28c;
  float local_288 [17];
  undefined1 auStack_244 [256];
  undefined1 auStack_144 [260];
  char local_2c;
  
  uVar13 = param_1 + 1;
  iVar14 = uVar13 * 0x20;
  FUN_00439710(param_3 + 0x20,param_3 + uVar13 * 0x40 + 0x20,(uVar13 * -0x20 + 0x180) * 2);
  (*(code *)(&PTR_FUN_00438d8a_1_00439680)[param_2])
            (param_3 + 0x10,param_4,param_3 + uVar13 * -0x40 + 800,iVar14);
  if ((param_1 & 0xff) == 2) {
    iVar6 = -0x58;
  }
  else {
    iVar6 = -0x30;
  }
  local_28c = param_3 + uVar13 * -0x40 + 800 + iVar6;
  uVar8 = uVar13 & 0x7ffffff;
  iVar6 = uVar8 * 0x10;
  FUN_00439710(param_3 + 800,param_3 + 800 + uVar13 * 0x20,(uVar8 * -0x10 + 0xb2) * 2);
  pcVar15 = param_3 + uVar8 * -0x20 + 0x484;
  psVar20 = (short *)(local_28c + -2);
  for (pcVar12 = pcVar15; pcVar12 < pcVar15 + uVar13 * 0x20; pcVar12 = pcVar12 + 4) {
    psVar7 = psVar20 + 2;
    *(short *)pcVar12 =
         (short)((uint)(((int)*psVar7 + (int)psVar20[-2]) * 0x1fa9 +
                       ((int)psVar20[1] + (int)psVar20[-1]) * 0x3c40 + *psVar20 * 0x482d) >> 0x10);
    if (pcVar15 + uVar13 * 0x20 <= pcVar12 + 2) break;
    psVar3 = psVar20 + 1;
    psVar1 = psVar20 + 3;
    sVar4 = *psVar20;
    psVar2 = psVar20 + 4;
    psVar20 = psVar20 + 4;
    *(short *)(pcVar12 + 2) =
         (short)((uint)(((int)*psVar2 + (int)sVar4) * 0x1fa9 +
                       ((int)*psVar1 + (int)*psVar3) * 0x3c40 + *psVar7 * 0x482d) >> 0x10);
  }
  fVar17 = DAT_00439350;
  local_2c = (char)param_1;
  if (local_2c == '\0') {
    iVar14 = uVar13 * 0x40;
    iVar6 = uVar13 * 0x20;
    local_28c = local_28c + uVar13 * -0x40;
    pcVar15 = pcVar15 + uVar13 * -0x20;
  }
  uVar21 = 0;
  uVar8 = *(int *)(param_3 + 0x484) - 4;
  uVar13 = 0;
  if (0 < (int)uVar8) {
    uVar13 = uVar8;
  }
  iVar18 = *(int *)(param_3 + 0x484) + 4;
  if (0x61 < iVar18) {
    iVar18 = 0x61;
  }
  local_290 = 1.37327e-43;
  fVar19 = (float)(iVar18 - uVar13);
  FUN_004387b0(pcVar15,pcVar15 + -0x22,iVar6,local_288);
  bVar22 = (int)((uint)(local_288[0] < local_288[1] * DAT_00439354) << 0x1f) < 0;
  fVar23 = local_288[0];
  if (bVar22) {
    local_288[0] = local_288[1] * DAT_00439354;
    fVar23 = local_288[1];
  }
  uVar8 = (uint)bVar22;
  uVar10 = 2;
  fVar24 = DAT_0043935c;
  pfVar11 = &local_290;
  do {
    fVar25 = pfVar11[4];
    fVar26 = fVar25 * fVar24;
    if (local_288[0] < fVar26) {
      uVar8 = uVar10;
      local_288[0] = fVar26;
      fVar23 = fVar25;
    }
    fVar25 = pfVar11[5] * (fVar24 + DAT_00439358);
    if (local_288[0] < fVar25) {
      uVar8 = uVar10 + 1;
      local_288[0] = fVar25;
      fVar23 = pfVar11[5];
    }
    fVar24 = fVar24 + DAT_00439358 + DAT_00439358;
    fVar25 = pfVar11[6] * fVar24;
    if (local_288[0] < fVar25) {
      uVar8 = uVar10 + 2;
      local_288[0] = fVar25;
      fVar23 = pfVar11[6];
    }
    fVar24 = fVar24 + DAT_00439358;
    fVar25 = pfVar11[7] * fVar24;
    if (local_288[0] < fVar25) {
      uVar8 = uVar10 + 3;
      local_288[0] = fVar25;
      fVar23 = pfVar11[7];
    }
    uVar10 = uVar10 + 4;
    fVar24 = fVar24 + DAT_00439358;
    pfVar11 = pfVar11 + 4;
  } while ((int)uVar10 < 0x62);
  fVar24 = local_288[uVar13];
  if (1 < (int)((int)fVar19 + 1U)) {
    pfVar11 = local_288 + uVar13 + 1;
    if (((uint)fVar19 & 3) != 0) {
      do {
        if (fVar24 < *pfVar11) {
          fVar24 = *pfVar11;
        }
        pfVar11 = pfVar11 + 1;
        loopEnd();
      } while( true );
    }
    local_290 = fVar19;
    if ((uint)fVar19 >> 2 != 0) {
      do {
        if (fVar24 < *pfVar11) {
          fVar24 = *pfVar11;
        }
        if (fVar24 < pfVar11[1]) {
          fVar24 = pfVar11[1];
        }
        if (fVar24 < pfVar11[2]) {
          fVar24 = pfVar11[2];
        }
        if (fVar24 < pfVar11[3]) {
          fVar24 = pfVar11[3];
        }
        pfVar11 = pfVar11 + 4;
        loopEnd();
      } while( true );
    }
  }
  fVar19 = DAT_00439350;
  if (0.0 < fVar23) {
    fVar19 = (float)FUN_00438770(pcVar15,pcVar15,iVar6);
    fVar25 = (float)FUN_00438770(pcVar15 + (uVar8 + 0x11) * -2,pcVar15 + (uVar8 + 0x11) * -2,iVar6);
    fVar19 = (float)FUN_004397a8(fVar19 * fVar25);
    fVar19 = fVar23 / fVar19;
  }
  fVar23 = DAT_00439350;
  if (0.0 < fVar24) {
    fVar23 = (float)FUN_00438770(pcVar15,pcVar15,iVar6);
    fVar25 = (float)FUN_00438770(pcVar15 + (uVar13 + 0x11) * -2,pcVar15 + (uVar13 + 0x11) * -2,iVar6
                                );
    fVar23 = (float)FUN_004397a8(fVar23 * fVar25);
    fVar23 = fVar24 / fVar23;
  }
  bVar22 = fVar19 * DAT_00439614 < fVar23;
  if (bVar22) {
    uVar8 = uVar13;
  }
  *(uint *)(param_3 + 0x484) = uVar8;
  if (bVar22) {
    fVar19 = fVar23;
  }
  if (fVar19 < DAT_00439668) {
    iVar6 = 0;
  }
  else {
    iVar16 = (uVar8 + 0x11) * 2;
    iVar18 = iVar16 + -4;
    iVar6 = 1;
    if (iVar18 < 0x20) {
      iVar18 = 0x20;
    }
    iVar16 = iVar16 + 4;
    if (0xe4 < iVar16) {
      iVar16 = 0xe4;
    }
    fVar17 = (float)(iVar16 - iVar18);
    local_290 = (float)((int)fVar17 + 9);
    FUN_004387b0(local_28c,local_28c + (iVar18 + -4) * -2,iVar14,local_288);
    if (1 < (int)((int)fVar17 + 1U)) {
      pfVar11 = local_288 + 5;
      if (((uint)fVar17 & 3) != 0) {
        do {
          if (local_288[4] < *pfVar11) {
            local_288[4] = *pfVar11;
          }
          pfVar11 = pfVar11 + 1;
          loopEnd();
        } while( true );
      }
      local_290 = fVar17;
      if ((uint)fVar17 >> 2 != 0) {
        do {
          if (local_288[4] < *pfVar11) {
            local_288[4] = *pfVar11;
          }
          if (local_288[4] < pfVar11[1]) {
            local_288[4] = pfVar11[1];
          }
          if (local_288[4] < pfVar11[2]) {
            local_288[4] = pfVar11[2];
          }
          if (local_288[4] < pfVar11[3]) {
            local_288[4] = pfVar11[3];
          }
          pfVar11 = pfVar11 + 4;
          loopEnd();
        } while( true );
      }
    }
    uVar13 = 0;
    fVar17 = local_288[1] * DAT_0043966c + local_288[2] * DAT_00439670 + local_288[3] * DAT_00439674
             + local_288[4] * DAT_00439678 + local_288[5] * DAT_00439674 +
             local_288[6] * DAT_00439670 + local_288[7] * DAT_0043966c;
    uVar8 = 1;
    do {
      if ((iVar18 < 0x7f) || (iVar18 < 0x9d && (uVar8 & 1) == 0)) {
        fVar23 = (float)FUN_00438ef0(local_288 + 4,uVar8);
        if (fVar17 < fVar23) {
          uVar13 = uVar8;
          fVar17 = fVar23;
        }
        if (0x20 < iVar18) {
          fVar23 = (float)FUN_00438ef0(local_288 + 4,-uVar8);
          if (fVar17 < fVar23) {
            uVar13 = -uVar8;
            fVar17 = fVar23;
          }
        }
      }
      uVar8 = uVar8 + 1;
    } while ((int)uVar8 < 4);
    if ((int)uVar13 < 0) {
      iVar18 = iVar18 + -1;
      uVar13 = uVar13 + 4;
    }
    uVar21 = uVar13 + iVar18 * 4;
    if (iVar18 < 0x7f) {
      iVar18 = uVar21 - 0x80;
    }
    else if (iVar18 < 0x9d) {
      iVar18 = ((int)uVar13 >> 1) + iVar18 * 2 + 0x7e;
    }
    else {
      iVar18 = iVar18 + 0x11b;
    }
    *(int *)(param_5 + 4) = iVar18;
    FUN_00438924(local_28c,iVar14,0,auStack_144);
    FUN_00438924(local_28c + ((int)uVar21 >> 2) * -2,iVar14,uVar21 & 3,auStack_244);
    fVar17 = (float)FUN_00438770(auStack_144,auStack_244,iVar14);
    fVar23 = (float)FUN_00438770(auStack_144,auStack_144,iVar14);
    fVar19 = (float)FUN_00438770(auStack_244,auStack_244,iVar14);
    fVar23 = (float)FUN_004397a8(fVar23 * fVar19);
    fVar17 = fVar17 / fVar23;
  }
  if (*param_3 == '\0') {
    if ((param_2 < 5 && iVar6 == 1) &&
       ((local_2c == '\x03' || (DAT_004396a4 <= *(float *)(param_3 + 0xc))))) {
      fVar23 = *(float *)(param_3 + 8);
      bVar22 = NAN(fVar23) || NAN(DAT_004396a4);
      if (fVar23 >= DAT_004396a4) {
        bVar22 = NAN(fVar17) || NAN(DAT_004396a4);
      }
      if ((fVar23 < DAT_004396a4 || fVar17 < DAT_004396a4) == bVar22) goto LAB_00439662;
    }
  }
  else {
    uVar8 = *(uint *)(param_3 + 4);
    uVar13 = uVar21;
    if (((int)uVar21 <= (int)uVar8) && (uVar13 = uVar8, (int)uVar21 <= (int)uVar8)) {
      uVar8 = uVar21;
    }
    if ((param_2 < 5 && iVar6 == 1) &&
       ((DAT_0043967c <= fVar17 ||
        (((DAT_0043969c <= fVar17 && ((int)(uVar13 - uVar8) < 8)) &&
         (DAT_004396a0 <= fVar17 - *(float *)(param_3 + 8))))))) {
LAB_00439662:
      cVar5 = '\x01';
      goto LAB_004395ea;
    }
  }
  cVar5 = '\0';
LAB_004395ea:
  *param_5 = cVar5;
  *param_3 = cVar5;
  *(uint *)(param_3 + 4) = uVar21;
  uVar9 = *(undefined4 *)(param_3 + 8);
  *(float *)(param_3 + 8) = fVar17;
  *(undefined4 *)(param_3 + 0xc) = uVar9;
  return iVar6;
}

