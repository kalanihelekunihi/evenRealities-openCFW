
undefined4
FUN_005179d0(float *param_1,undefined4 *param_2,float *param_3,undefined4 *param_4,int param_5)

{
  char cVar1;
  int *piVar2;
  int iVar3;
  undefined4 *puVar4;
  int iVar5;
  int iVar6;
  undefined4 *puVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  undefined4 uVar13;
  bool bVar14;
  bool bVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  undefined4 uVar22;
  undefined4 uVar23;
  undefined4 uVar24;
  float local_b0;
  float local_ac;
  float local_a8;
  float local_a4;
  undefined4 local_a0;
  float local_9c;
  undefined4 local_98;
  undefined4 local_94;
  undefined4 local_90;
  undefined4 local_8c;
  undefined4 local_88;
  float local_84;
  undefined4 uStack_80;
  undefined4 uStack_7c;
  undefined4 local_78;
  undefined4 local_74;
  undefined4 local_70;
  undefined4 local_6c;
  float local_68;
  undefined4 local_64;
  float local_60;
  undefined4 local_5c;
  undefined4 local_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 local_4c;
  
  piVar2 = DAT_00517e08;
  iVar3 = *DAT_00517e08;
  if (*(int *)(iVar3 + 0x110) == 0) {
    return 0;
  }
  cVar1 = *(char *)(iVar3 + 0x2e2);
  uVar9 = 0;
  if ((cVar1 == '\0') || (*(int *)(iVar3 + 0x118) != 0)) {
    if (-1 < (int)((uint)*(byte *)(iVar3 + 0x7d) << 0x1b)) {
      uVar9 = FUN_0052266e(1,0,1,0);
    }
    FUN_00516b34(*param_1,param_1[1],*param_2,param_2[1],*param_3,param_3[1],*param_4,param_4[1]);
    goto LAB_00517a30;
  }
  if (cVar1 == '\x02') {
    local_b0 = *DAT_00517e0c;
    local_ac = DAT_00517e0c[1];
    iVar3 = FUN_00522f50(*param_1,param_1[1],*param_3,param_3[1],*param_2,param_2[1],*param_4,
                         param_4[1],&local_b0,&local_ac);
    if (iVar3 == 0) {
      return 0;
    }
    iVar3 = *piVar2;
    fVar16 = (float)FUN_004397a8(*(float *)(iVar3 + 0xec) * *(float *)(iVar3 + 0xec) +
                                 *(float *)(iVar3 + 0xf0) * *(float *)(iVar3 + 0xf0));
    fVar17 = (float)FUN_004397a8(*(float *)(iVar3 + 0xf8) * *(float *)(iVar3 + 0xf8) +
                                 *(float *)(iVar3 + 0xfc) * *(float *)(iVar3 + 0xfc));
    fVar16 = ABS(fVar16);
    bVar14 = NAN(fVar16) || NAN(DAT_00517e00);
    if (fVar16 < DAT_00517e00) {
      bVar14 = NAN(ABS(fVar17)) || NAN(DAT_00517e00);
    }
    bVar14 = (fVar16 < DAT_00517e00 && ABS(fVar17) < DAT_00517e00) == bVar14;
    if (bVar14) {
      FUN_00522622(1);
    }
    if ((int)((uint)*(byte *)(*piVar2 + 0x7d) << 0x1b) < 0) {
      FUN_00522fb4(local_b0,local_ac,*(float *)(*piVar2 + 0x2d8) * 0.5);
    }
    else {
      FUN_00523284();
    }
    if (!bVar14) {
      return 0;
    }
    FUN_00522622(0);
    return 0;
  }
  if (cVar1 != '\x01') {
    return 0x1000000;
  }
  if (*(char *)(iVar3 + 0x2e4) == '\0') {
    fVar16 = *(float *)(iVar3 + 0x158);
    if ((fVar16 <= 0.0) || (*(int *)(iVar3 + 0x128) != 1)) {
      if (param_5 == 1) {
        bVar14 = fVar16 < 0.0;
        bVar15 = fVar16 == 0.0;
        if (!bVar15 && !bVar14) {
          fVar16 = *(float *)(iVar3 + 0x184);
          bVar14 = fVar16 < 0.0;
          bVar15 = fVar16 == 0.0;
        }
        if (!bVar15 && bVar14 == NAN(fVar16)) {
          local_a0 = *(undefined4 *)(iVar3 + 0x138);
          local_9c = *(float *)(iVar3 + 0x13c);
          local_98 = *(undefined4 *)(iVar3 + 0x140);
          local_94 = *(undefined4 *)(iVar3 + 0x144);
          local_90 = *(undefined4 *)(iVar3 + 0x148);
          puVar4 = (undefined4 *)(iVar3 + 0x164);
          local_8c = *(undefined4 *)(iVar3 + 0x14c);
          local_88 = *(undefined4 *)(iVar3 + 0x150);
          local_84 = *(float *)(iVar3 + 0x154);
          uStack_80 = *(undefined4 *)(iVar3 + 0x158);
          uStack_7c = *(undefined4 *)(iVar3 + 0x15c);
          local_78 = *(undefined4 *)(iVar3 + 0x160);
          puVar7 = &local_74;
          goto LAB_00517bee;
        }
      }
      local_74 = *(undefined4 *)(iVar3 + 0x164);
      local_70 = *(undefined4 *)(iVar3 + 0x168);
      local_6c = *(undefined4 *)(iVar3 + 0x16c);
      local_68 = *(float *)(iVar3 + 0x170);
      local_64 = *(undefined4 *)(iVar3 + 0x174);
      puVar4 = (undefined4 *)(iVar3 + 400);
      local_60 = *(float *)(iVar3 + 0x178);
      local_5c = *(undefined4 *)(iVar3 + 0x17c);
      local_58 = *(undefined4 *)(iVar3 + 0x180);
      uStack_54 = *(undefined4 *)(iVar3 + 0x184);
      uStack_50 = *(undefined4 *)(iVar3 + 0x188);
      local_4c = *(undefined4 *)(iVar3 + 0x18c);
      puVar7 = &local_a0;
    }
    else {
      local_74 = *(undefined4 *)(iVar3 + 0x138);
      local_70 = *(undefined4 *)(iVar3 + 0x13c);
      local_6c = *(undefined4 *)(iVar3 + 0x140);
      local_68 = *(float *)(iVar3 + 0x144);
      local_64 = *(undefined4 *)(iVar3 + 0x148);
      puVar4 = (undefined4 *)(iVar3 + 400);
      local_60 = *(float *)(iVar3 + 0x14c);
      local_5c = *(undefined4 *)(iVar3 + 0x150);
      local_58 = *(undefined4 *)(iVar3 + 0x154);
      uStack_54 = *(undefined4 *)(iVar3 + 0x158);
      uStack_50 = *(undefined4 *)(iVar3 + 0x15c);
      local_4c = *(undefined4 *)(iVar3 + 0x160);
      puVar7 = &local_a0;
    }
  }
  else {
    local_74 = *(undefined4 *)(iVar3 + 0x334);
    local_70 = *(undefined4 *)(iVar3 + 0x338);
    local_6c = *(undefined4 *)(iVar3 + 0x33c);
    local_68 = *(float *)(iVar3 + 0x340);
    local_64 = *(undefined4 *)(iVar3 + 0x344);
    puVar4 = (undefined4 *)(iVar3 + 0x308);
    local_60 = *(float *)(iVar3 + 0x348);
    local_5c = *(undefined4 *)(iVar3 + 0x34c);
    local_58 = *(undefined4 *)(iVar3 + 0x350);
    uStack_54 = *(undefined4 *)(iVar3 + 0x354);
    uStack_50 = *(undefined4 *)(iVar3 + 0x358);
    local_4c = *(undefined4 *)(iVar3 + 0x35c);
    puVar7 = &local_a0;
  }
LAB_00517bee:
  uVar8 = puVar4[1];
  uVar10 = puVar4[2];
  uVar11 = puVar4[3];
  uVar12 = puVar4[4];
  uVar13 = puVar4[5];
  *puVar7 = *puVar4;
  puVar7[1] = uVar8;
  puVar7[2] = uVar10;
  puVar7[3] = uVar11;
  puVar7[4] = uVar12;
  puVar7[5] = uVar13;
  uVar8 = puVar4[7];
  uVar10 = puVar4[8];
  uVar11 = puVar4[9];
  uVar12 = puVar4[10];
  puVar7[6] = puVar4[6];
  puVar7[7] = uVar8;
  puVar7[8] = uVar10;
  puVar7[9] = uVar11;
  puVar7[10] = uVar12;
  iVar3 = FUN_005177a4(&local_a0,&local_74);
  if ((((iVar3 == 1) && (iVar3 = FUN_005177a4(&local_98,&local_6c), iVar3 == 1)) &&
      (iVar3 = FUN_005177a4(&local_90,&local_64), iVar3 == 1)) &&
     (iVar3 = FUN_005177a4(&local_88,&local_5c), iVar3 == 1)) {
    return 0;
  }
  iVar3 = FUN_0051785c(&local_a0,&local_6c);
  if ((iVar3 != 0) || (iVar3 = FUN_0051785c(&local_74,&local_a0), iVar3 != 0)) goto LAB_00517c84;
  iVar3 = FUN_0051785c(&local_a0,&local_64);
  uVar8 = local_64;
  fVar16 = local_60;
  uVar10 = local_88;
  fVar17 = local_84;
  uVar11 = local_a0;
  fVar21 = local_9c;
  uVar12 = local_6c;
  fVar18 = local_68;
  uVar13 = local_98;
  uVar24 = local_94;
  uVar22 = local_74;
  uVar23 = local_70;
  if ((iVar3 == 0) &&
     (iVar3 = FUN_0051785c(&local_74,&local_88), uVar8 = local_64, fVar16 = local_60,
     uVar10 = local_88, fVar17 = local_84, uVar11 = local_a0, fVar21 = local_9c, uVar12 = local_6c,
     fVar18 = local_68, uVar13 = local_98, uVar24 = local_94, uVar22 = local_74, uVar23 = local_70,
     iVar3 == 0)) {
    iVar3 = (uint)(local_60 < local_68) << 0x1f;
    if ((int)((uint)(local_9c < local_68) << 0x1f) < 0) {
      if (-1 < iVar3) {
LAB_00517c84:
        uVar8 = local_6c;
        fVar16 = local_68;
        uVar10 = local_a0;
        fVar17 = local_9c;
        uVar11 = local_88;
        fVar21 = local_84;
        uVar12 = local_64;
        fVar18 = local_60;
        uVar13 = local_90;
        uVar24 = local_8c;
        uVar22 = local_5c;
        uVar23 = local_58;
      }
    }
    else if (iVar3 < 0) goto LAB_00517c84;
  }
  local_a8 = *DAT_00517e10;
  local_a4 = DAT_00517e10[1];
  local_b0 = *DAT_00517e14;
  local_ac = DAT_00517e14[1];
  iVar3 = FUN_00522f50(uVar12,fVar18,uVar8,fVar16,uVar11,fVar21,uVar10,fVar17,&local_a8,&local_a4);
  iVar5 = FUN_00522f50(uVar22,uVar23,uVar12,fVar18,uVar11,fVar21,uVar13,uVar24,&local_b0,&local_ac);
  fVar16 = (float)FUN_00524218((local_b0 - local_a8) * (local_b0 - local_a8) +
                               (local_ac - local_a4) * (local_ac - local_a4));
  iVar6 = *piVar2;
  if (((int)((uint)(*(float *)(iVar6 + 0x2dc) * *(float *)(iVar6 + 0x2d8) < fVar16) << 0x1f) < 0) ||
     (iVar5 == 0 || iVar3 == 0)) {
    if (-1 < (int)((uint)*(byte *)(iVar6 + 0x7d) << 0x1b)) {
      uVar9 = FUN_0052266e(1,0,1,0);
    }
    uVar11 = *param_4;
    fVar21 = (float)param_4[1];
    uVar12 = *param_2;
    fVar18 = (float)param_2[1];
    fVar16 = *param_1;
    fVar17 = param_1[1];
    fVar19 = *param_3;
    fVar20 = param_3[1];
  }
  else {
    fVar16 = local_a8;
    fVar17 = local_a4;
    fVar19 = local_b0;
    fVar20 = local_ac;
    if (-1 < (int)((uint)*(byte *)(iVar6 + 0x7d) << 0x1b)) {
      uVar9 = FUN_0052266e(0,1,1,0);
      fVar16 = local_a8;
      fVar17 = local_a4;
      fVar19 = local_b0;
      fVar20 = local_ac;
    }
  }
  FUN_00516b34(fVar16,fVar17,uVar12,fVar18,fVar19,fVar20,uVar11,fVar21);
LAB_00517a30:
  if (-1 < (int)((uint)*(byte *)(*piVar2 + 0x7d) << 0x1b)) {
    FUN_005226b2(uVar9);
  }
  return 0;
}

