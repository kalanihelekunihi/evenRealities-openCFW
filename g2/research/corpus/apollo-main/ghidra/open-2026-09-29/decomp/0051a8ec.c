
int FUN_0051a8ec(undefined4 param_1,int param_2)

{
  byte bVar1;
  int *piVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  int iVar5;
  char cVar6;
  int iVar7;
  uint uVar8;
  byte bVar9;
  bool bVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float extraout_s1;
  float extraout_s1_00;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  undefined8 unaff_d8;
  float fVar20;
  undefined8 uVar19;
  undefined4 uVar21;
  undefined8 uVar22;
  undefined4 uVar23;
  float fVar24;
  float fVar25;
  float fVar26;
  float fVar27;
  float fVar28;
  float fVar29;
  float fVar30;
  float fVar31;
  float fVar32;
  float fVar33;
  float fVar34;
  float local_7c;
  float fStack_78;
  undefined4 local_74;
  undefined4 uStack_70;
  float local_6c;
  float fStack_68;
  undefined4 local_64;
  undefined4 uStack_60;
  
  piVar2 = DAT_0051b134;
  fVar20 = (float)((ulonglong)unaff_d8 >> 0x20);
  fVar18 = ABS(*(float *)(param_2 + 0x1c));
  bVar10 = DAT_0051ac54 <= fVar18;
  if (bVar10) {
    fVar20 = ABS(*(float *)(param_2 + 0x20));
  }
  if (bVar10 && (bVar10 && DAT_0051ac54 <= fVar20)) {
    fVar31 = *(float *)(param_2 + 0x24) * DAT_0051b118;
    fVar24 = *(float *)(param_2 + 0x34);
    fVar25 = *(float *)(param_2 + 0x38);
    fVar11 = *(float *)(param_2 + 0x2c);
    fVar12 = *(float *)(param_2 + 0x30);
    bVar9 = *(byte *)(param_2 + 3);
    fVar29 = (float)FUN_0050968c();
    fVar31 = (float)FUN_00509690(fVar31);
    fVar17 = fVar24 * fVar29 + fVar25 * fVar31;
    fVar27 = fVar11 * fVar29 + fVar12 * fVar31;
    fVar13 = fVar17 / fVar18;
    fVar24 = fVar25 * fVar29 - fVar24 * fVar31;
    fVar15 = fVar27 / fVar18;
    fVar34 = fVar12 * fVar29 - fVar11 * fVar31;
    fVar14 = fVar24 / fVar20;
    fVar16 = fVar34 / fVar20;
    fVar30 = fVar13 - fVar15;
    fVar32 = fVar14 - fVar16;
    fVar11 = fVar13 + fVar15;
    fVar25 = fVar30 * fVar30 + fVar32 * fVar32;
    bVar1 = bVar9 >> 6;
    fVar12 = fVar14 + fVar16;
    bVar9 = bVar9 >> 5 & 1;
    if (fVar25 == 0.0) {
      iVar7 = *piVar2;
      *(undefined4 *)(iVar7 + 0x114) = 0;
      *(undefined4 *)(iVar7 + 0x118) = 0;
      FUN_0051565c(0x100);
      return 0x100;
    }
    fVar33 = 1.0 / fVar25 + -0.25;
    if ((int)((uint)(fVar33 < 0.0) << 0x1f) < 0) {
      fVar25 = (float)FUN_004397a8(fVar25 * 0.25);
      fVar20 = fVar20 * fVar25;
      fVar18 = fVar18 * fVar25;
      fVar13 = fVar17 / fVar18;
      fVar14 = fVar24 / fVar20;
      fVar15 = fVar27 / fVar18;
      fVar11 = fVar13 + fVar15;
      fVar16 = fVar34 / fVar20;
      fVar12 = fVar14 + fVar16;
      fVar30 = fVar13 - fVar15;
      fVar32 = fVar14 - fVar16;
      fVar33 = DAT_0051b11c;
    }
    fVar17 = fVar20;
    local_7c = fVar18;
    fVar27 = (float)FUN_004397a8(fVar33);
    fVar26 = fVar11 * 0.5 + fVar27 * fVar32;
    fVar28 = fVar12 * 0.5 - fVar27 * fVar30;
    fVar34 = (float)FUN_0050969c(fVar14 - fVar28,fVar13 - fVar26);
    fVar25 = (float)FUN_0050969c(fVar16 - fVar28,fVar15 - fVar26);
    fVar24 = DAT_0051b120;
    fVar34 = fVar34 * DAT_0051b120;
    fVar25 = fVar25 * DAT_0051b120;
    fVar33 = fVar25 - fVar34;
    if ((int)((uint)(fVar33 < 0.0) << 0x1f) < 0) {
      fVar33 = fVar33 + DAT_0051b124;
    }
    if (((-1 < (int)((uint)(fVar33 < DAT_0051b128) << 0x1f)) || (bVar9 == (bVar1 & 1))) &&
       ((fVar33 < DAT_0051b128 || (bVar9 != (bVar1 & 1))))) {
      fVar26 = fVar11 * 0.5 - fVar27 * fVar32;
      fVar28 = fVar12 * 0.5 + fVar27 * fVar30;
      fVar34 = (float)FUN_0050969c(fVar14 - fVar28,fVar13 - fVar26);
      fVar25 = (float)FUN_0050969c(fVar16 - fVar28,fVar15 - fVar26);
      fVar34 = fVar34 * fVar24;
      fVar25 = fVar25 * fVar24;
    }
    fVar12 = local_7c;
    fVar11 = DAT_0051b130;
    fVar24 = DAT_0051b12c;
    fVar13 = fVar26 * fVar18 * fVar29 - fVar28 * fVar20 * fVar31;
    fVar18 = fVar26 * fVar18 * fVar31 + fVar28 * fVar20 * fVar29;
    fVar20 = fVar34;
    if ((bVar1 & 1) == 0) {
      fVar20 = fVar25;
      fVar25 = fVar34;
    }
    if ((int)((uint)(fVar25 < fVar20) << 0x1f) < 0) {
      fVar25 = fVar25 + DAT_0051b124;
    }
    bVar10 = true;
    cVar6 = '\x01';
    fVar29 = fVar25;
    if ((bVar1 & 1) == 0) {
      while ((int)((uint)(fVar20 < fVar25) << 0x1f) < 0) {
        fVar31 = fVar25 + fVar11;
        iVar7 = (uint)(fVar20 < fVar31) << 0x1f;
        if (iVar7 < 0) {
          fVar29 = fVar31;
        }
        if (-1 < iVar7) {
          fVar29 = fVar20;
        }
        if (-1 < (int)((uint)(fVar20 < fVar31) << 0x1f)) {
          cVar6 = cVar6 + '\x02';
        }
        if (!bVar10) {
          *(bool *)(*piVar2 + 0x1c0) = bVar10;
          *(undefined1 *)(*piVar2 + 0x2eb) = 1;
        }
        iVar7 = FUN_0051a694(fVar25,fVar29,fVar13,fVar18,fVar12,fVar17,param_1,param_2,cVar6);
        if (iVar7 != 0) goto LAB_0051b0dc;
        bVar10 = false;
        cVar6 = '\0';
        fVar25 = fVar31;
        fVar29 = extraout_s1_00;
      }
    }
    else {
      while ((int)((uint)(fVar20 < fVar25) << 0x1f) < 0) {
        fVar31 = fVar20 + fVar24;
        iVar7 = (uint)(fVar31 < fVar25) << 0x1f;
        if (iVar7 < 0) {
          fVar29 = fVar31;
        }
        if (-1 < iVar7) {
          fVar29 = fVar25;
        }
        if (-1 < (int)((uint)(fVar31 < fVar25) << 0x1f)) {
          cVar6 = cVar6 + '\x02';
        }
        if (!bVar10) {
          *(bool *)(*piVar2 + 0x1c0) = bVar10;
          *(undefined1 *)(*piVar2 + 0x2eb) = 1;
        }
        iVar7 = FUN_0051a694(fVar20,fVar29,fVar13,fVar18,fVar12,fVar17,param_1,param_2,cVar6);
        if (iVar7 != 0) {
LAB_0051b0dc:
          iVar5 = *piVar2;
          *(undefined4 *)(iVar5 + 0x114) = 0;
          *(undefined4 *)(iVar5 + 0x118) = 0;
          FUN_0051565c(iVar7);
          return iVar7;
        }
        bVar10 = false;
        cVar6 = '\0';
        fVar20 = fVar31;
        fVar29 = extraout_s1;
      }
    }
    *(undefined1 *)(*piVar2 + 0x1c0) = 1;
    *(undefined1 *)(*piVar2 + 0x2eb) = 0;
    return 0;
  }
  iVar7 = *DAT_0051b134;
  if (*(char *)(iVar7 + 0x7c) != '\0') {
    uVar22 = *(undefined8 *)(param_2 + 0xc);
    uVar19 = *(undefined8 *)(param_2 + 0x14);
    uVar8 = 0;
    if (*(int *)(iVar7 + 0x88) != 0) {
      if (*(int *)(iVar7 + 0x114) == 0) {
        uVar8 = 0x7800000;
      }
      else {
        uVar8 = 0x4000000;
      }
    }
    uVar8 = uVar8 & *(uint *)(iVar7 + 0x8c);
    if (*(char *)(*DAT_0051b138 + 8) == '\x01') {
      uVar8 = uVar8 | *(uint *)(*DAT_0051b138 + 0xc) & 0xc0000000;
    }
    puVar3 = (undefined4 *)FUN_00514aec(5);
    if (puVar3 == (undefined4 *)0x0) {
      return 0;
    }
    *puVar3 = 800;
    puVar3[1] = (int)uVar22;
    puVar3[2] = 0x324;
    puVar3[3] = (int)((ulonglong)uVar22 >> 0x20);
    puVar3[4] = 0x330;
    puVar3[5] = (int)uVar19;
    puVar3[6] = 0x334;
    puVar3[7] = (int)((ulonglong)uVar19 >> 0x20);
    puVar3[8] = DAT_0051b13c;
    uVar8 = uVar8 | 0xb;
LAB_0051ada8:
    puVar3[9] = uVar8;
    return 0;
  }
  fVar31 = *(float *)(param_2 + 0xc);
  fVar20 = *(float *)(param_2 + 0x10);
  fVar18 = *(float *)(param_2 + 0x14);
  fVar29 = *(float *)(param_2 + 0x18);
  if (*(int *)(iVar7 + 0x110) == 0) {
    uVar8 = 0;
    if (*(int *)(iVar7 + 0x88) != 0) {
      uVar8 = 0x7800000;
    }
    uVar8 = uVar8 & *(uint *)(iVar7 + 0x8c);
    if (*(char *)(*DAT_0051b138 + 8) == '\x01') {
      uVar8 = uVar8 | *(uint *)(*DAT_0051b138 + 0xc) & 0xc0000000;
    }
    puVar3 = (undefined4 *)FUN_00514aec(5);
    if (puVar3 == (undefined4 *)0x0) {
      return 0;
    }
    *puVar3 = 800;
    puVar3[2] = 0x324;
    puVar3[4] = 0x330;
    uVar4 = DAT_0051b13c;
    puVar3[1] = fVar31;
    puVar3[3] = fVar20;
    puVar3[5] = fVar18;
    puVar3[6] = 0x334;
    puVar3[7] = fVar29;
    puVar3[8] = uVar4;
    uVar8 = uVar8 | 10;
    goto LAB_0051ada8;
  }
  fVar24 = fVar18 - fVar31;
  fVar25 = fVar29 - fVar20;
  if ((int)((uint)(ABS(fVar24 * fVar24 + fVar25 * fVar25) < DAT_0051ac54) << 0x1f) < 0) {
    *(float *)(iVar7 + 0x198) = fVar31;
    *(float *)(iVar7 + 0x19c) = fVar20 + *(float *)(iVar7 + 0x130) * -0.5;
    *(float *)(iVar7 + 0x1a0) = fVar31;
    *(float *)(iVar7 + 0x1a4) = fVar20 + *(float *)(iVar7 + 0x130) * 0.5;
    *(undefined4 *)(iVar7 + 400) = *(undefined4 *)(iVar7 + 0x198);
    *(undefined4 *)(iVar7 + 0x194) = *(undefined4 *)(iVar7 + 0x19c);
    iVar7 = *piVar2;
    *(undefined4 *)(iVar7 + 0x1a8) = *(undefined4 *)(iVar7 + 0x1a0);
    *(undefined4 *)(iVar7 + 0x1ac) = *(undefined4 *)(iVar7 + 0x1a4);
    return 0;
  }
  fVar11 = (float)FUN_004397a8();
  fVar24 = fVar24 * (1.0 / fVar11);
  fVar25 = fVar25 * (1.0 / fVar11);
  fVar12 = *(float *)(iVar7 + 0x130) * 0.5 * fVar25;
  fVar14 = fVar31 - fVar12;
  fVar13 = *(float *)(iVar7 + 0x134) * 0.5 * fVar24;
  fVar15 = fVar13 + fVar20;
  uVar22 = CONCAT44(fVar15,fVar14);
  *(float *)(iVar7 + 400) = fVar14;
  *(float *)(iVar7 + 0x194) = fVar15;
  iVar7 = *piVar2;
  fVar16 = fVar18 - fVar12;
  fVar17 = fVar13 + fVar29;
  *(float *)(iVar7 + 0x198) = fVar16;
  *(float *)(iVar7 + 0x19c) = fVar17;
  iVar7 = *piVar2;
  fVar18 = fVar12 + fVar18;
  fVar29 = fVar29 - fVar13;
  *(float *)(iVar7 + 0x1a0) = fVar18;
  *(float *)(iVar7 + 0x1a4) = fVar29;
  iVar7 = *piVar2;
  fVar12 = fVar12 + fVar31;
  fVar20 = fVar20 - fVar13;
  uVar19 = CONCAT44(fVar20,fVar12);
  *(float *)(iVar7 + 0x1a8) = fVar12;
  *(float *)(iVar7 + 0x1ac) = fVar20;
  iVar7 = *piVar2;
  if (*(int *)(iVar7 + 0x110) == 0) {
    uVar4 = FUN_005226b2(*(undefined4 *)(iVar7 + 0x8c));
    FUN_00516b34(fVar14,fVar15,fVar16,fVar17,fVar18,fVar29,fVar12,fVar20);
  }
  else {
    bVar10 = -1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b);
    uVar4 = FUN_0052266e(bVar10,0,bVar10,0);
    iVar7 = *piVar2;
    if (0.0 < *(float *)(iVar7 + 0x184)) {
      local_64 = *(undefined4 *)(iVar7 + 0x164);
      uStack_60 = *(undefined4 *)(iVar7 + 0x168);
      local_6c = *(float *)(iVar7 + 0x16c);
      fStack_68 = *(float *)(iVar7 + 0x170);
      local_74 = *(undefined4 *)(iVar7 + 0x174);
      uStack_70 = *(undefined4 *)(iVar7 + 0x178);
      local_7c = *(float *)(iVar7 + 0x17c);
      fStack_78 = *(float *)(iVar7 + 0x180);
      FUN_00516b34(local_64,uStack_60,local_6c,fStack_68,local_74,uStack_70,local_7c,fStack_78);
      iVar7 = *piVar2;
      if ((int)((uint)(ABS(*(float *)(iVar7 + 0x188) * fVar25 - *(float *)(iVar7 + 0x18c) * fVar24)
                      < DAT_0051ae80) << 0x1f) < 0) {
        uVar22 = *(undefined8 *)(iVar7 + 0x16c);
        uVar19 = *(undefined8 *)(iVar7 + 0x174);
      }
      else {
        local_64 = *(undefined4 *)(iVar7 + 0x16c);
        uStack_60 = *(undefined4 *)(iVar7 + 0x170);
        local_74 = *(undefined4 *)(iVar7 + 0x174);
        uStack_70 = *(undefined4 *)(iVar7 + 0x178);
        local_7c = fVar12;
        fStack_78 = fVar20;
        local_6c = fVar14;
        fStack_68 = fVar15;
        iVar7 = FUN_005179d0(&local_64,&local_6c,&local_74,&local_7c,0);
        if (iVar7 != 0) goto LAB_0051acca;
      }
    }
    iVar7 = *piVar2;
    if ((0.0 < *(float *)(iVar7 + 0x158)) && (*(int *)(iVar7 + 0x128) == 1)) {
      if ((int)((uint)(ABS(*(float *)(iVar7 + 0x15c) * fVar25 - *(float *)(iVar7 + 0x160) * fVar24)
                      < DAT_0051ae80) << 0x1f) < 0) {
        uVar22 = *(undefined8 *)(iVar7 + 0x140);
        uVar19 = *(undefined8 *)(iVar7 + 0x148);
      }
      else {
        local_64 = *(undefined4 *)(iVar7 + 0x140);
        uStack_60 = *(undefined4 *)(iVar7 + 0x144);
        local_6c = (float)uVar22;
        fStack_68 = (float)((ulonglong)uVar22 >> 0x20);
        local_74 = *(undefined4 *)(iVar7 + 0x148);
        uStack_70 = *(undefined4 *)(iVar7 + 0x14c);
        local_7c = (float)uVar19;
        fStack_78 = (float)((ulonglong)uVar19 >> 0x20);
        iVar7 = FUN_005179d0(&local_64,&local_6c,&local_74,&local_7c,0);
        if (iVar7 != 0) {
LAB_0051acca:
          iVar7 = *piVar2;
          *(undefined4 *)(iVar7 + 0x114) = 0;
          *(undefined4 *)(iVar7 + 0x118) = 0;
          FUN_0051565c();
          return 0;
        }
      }
    }
    iVar7 = *piVar2;
    *(int *)(iVar7 + 0x128) = *(int *)(iVar7 + 0x128) + 1;
    uVar23 = (undefined4)((ulonglong)uVar22 >> 0x20);
    uVar21 = (undefined4)((ulonglong)uVar19 >> 0x20);
    if (*(float *)(iVar7 + 0x158) == 0.0) {
      *(int *)(iVar7 + 0x138) = (int)uVar22;
      *(undefined4 *)(iVar7 + 0x13c) = uVar23;
      iVar7 = *piVar2;
      *(float *)(iVar7 + 0x140) = fVar16;
      *(float *)(iVar7 + 0x144) = fVar17;
      iVar7 = *piVar2;
      *(float *)(iVar7 + 0x148) = fVar18;
      *(float *)(iVar7 + 0x14c) = fVar29;
      iVar7 = *piVar2;
      *(int *)(iVar7 + 0x150) = (int)uVar19;
      *(undefined4 *)(iVar7 + 0x154) = uVar21;
      iVar7 = *piVar2;
      *(float *)(iVar7 + 0x158) = fVar11;
      *(float *)(iVar7 + 0x15c) = fVar24;
      *(float *)(iVar7 + 0x160) = fVar25;
    }
    else {
      *(int *)(iVar7 + 0x164) = (int)uVar22;
      *(undefined4 *)(iVar7 + 0x168) = uVar23;
      iVar7 = *piVar2;
      *(float *)(iVar7 + 0x16c) = fVar16;
      *(float *)(iVar7 + 0x170) = fVar17;
      iVar7 = *piVar2;
      *(float *)(iVar7 + 0x174) = fVar18;
      *(float *)(iVar7 + 0x178) = fVar29;
      iVar7 = *piVar2;
      *(int *)(iVar7 + 0x17c) = (int)uVar19;
      *(undefined4 *)(iVar7 + 0x180) = uVar21;
      iVar7 = *piVar2;
      *(float *)(iVar7 + 0x184) = fVar11;
      *(float *)(iVar7 + 0x188) = fVar24;
      *(float *)(iVar7 + 0x18c) = fVar25;
    }
  }
  FUN_005226b2(uVar4);
  return 0;
}

