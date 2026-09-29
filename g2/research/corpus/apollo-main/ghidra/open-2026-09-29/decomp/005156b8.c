
undefined4 FUN_005156b8(float param_1,uint param_2,char *param_3)

{
  uint *puVar1;
  char cVar2;
  char cVar3;
  undefined4 *puVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  undefined4 uVar9;
  uint *unaff_r6;
  uint uVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  bool bVar13;
  bool bVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  float fVar24;
  float fVar25;
  float fVar26;
  undefined8 uVar27;
  undefined8 uVar28;
  float fVar29;
  float fVar30;
  float local_94;
  float local_90;
  float local_8c;
  float fStack_88;
  float local_84;
  float fStack_80;
  float local_7c;
  float fStack_78;
  undefined4 local_74;
  undefined4 uStack_70;
  
  *(undefined4 *)(param_3 + 0xc) = *(undefined4 *)(param_3 + 0x14);
  *(undefined4 *)(param_3 + 0x10) = *(undefined4 *)(param_3 + 0x18);
  puVar1 = DAT_00516230;
  bVar13 = -1 < (int)(param_2 << 0x1b);
  uVar10 = param_2 & 0x6f;
  uVar7 = (byte)param_3[0x44] & 0x6f;
  cVar3 = (char)param_2;
  if (uVar10 == 1) {
    if (param_3[1] == '\x01') {
      cVar2 = '\0';
      if (*(int *)(param_3 + 4) != 0) {
        uVar7 = *DAT_00516230;
        cVar2 = *(char *)(uVar7 + 0x7c);
        unaff_r6 = DAT_00516230;
      }
      if (*(int *)(param_3 + 4) != 0 && cVar2 != '\0') {
        uVar27 = CONCAT44(DAT_005158d8,DAT_005158d8);
        if (*param_3 == '\0') {
          uVar27 = *(undefined8 *)(param_3 + 0x3c);
        }
        uVar11 = *(undefined4 *)(uVar7 + 0x2d4);
        uVar12 = *(undefined4 *)(uVar7 + 0x2d0);
        puVar4 = (undefined4 *)FUN_00514aec(7);
        if (puVar4 != (undefined4 *)0x0) {
          uVar7 = *(uint *)(*unaff_r6 + 0x8c) & 0x7800000;
          if (*(char *)(*DAT_00516238 + 8) == '\x01') {
            uVar7 = uVar7 | *(uint *)(*DAT_00516238 + 0xc) & 0xc0000000;
          }
          *puVar4 = 800;
          uVar9 = *(undefined4 *)(param_3 + 0xc);
          puVar4[2] = 0x324;
          puVar4[1] = uVar9;
          uVar9 = *(undefined4 *)(param_3 + 0x10);
          puVar4[4] = 0x330;
          puVar4[3] = uVar9;
          puVar4[6] = 0x334;
          puVar4[8] = 0x140;
          uVar9 = DAT_0051623c;
          puVar4[5] = (int)uVar27;
          puVar4[7] = (int)((ulonglong)uVar27 >> 0x20);
          puVar4[9] = uVar12;
          puVar4[10] = 0x144;
          puVar4[0xb] = uVar11;
          puVar4[0xc] = uVar9;
          puVar4[0xd] = uVar7 | 4;
        }
      }
    }
    *(undefined4 *)(*DAT_00516230 + 0x120) = 0xffffffff;
    *param_3 = '\0';
    param_3[2] = '\x01';
    *(undefined4 *)(param_3 + 8) = *(undefined4 *)(param_3 + 4);
    iVar5 = *(int *)(param_3 + 4);
    iVar8 = *(int *)((int)param_1 + 0xc);
    fVar15 = *(float *)(iVar8 + iVar5 * 4);
    if (bVar13) {
      *(float *)(param_3 + 0x14) = fVar15;
      *(int *)(param_3 + 4) = iVar5 + 1;
      *(undefined4 *)(param_3 + 0x18) = *(undefined4 *)(iVar8 + (iVar5 + 1) * 4);
    }
    else {
      *(float *)(param_3 + 0x14) = *(float *)(param_3 + 0x2c) + fVar15;
      *(int *)(param_3 + 4) = iVar5 + 1;
      *(float *)(param_3 + 0x18) = *(float *)(param_3 + 0x30) + *(float *)(iVar8 + (iVar5 + 1) * 4);
    }
    *(int *)(param_3 + 4) = iVar5 + 2;
    *(undefined4 *)(param_3 + 0x2c) = *(undefined4 *)(param_3 + 0x14);
    *(undefined4 *)(param_3 + 0x30) = *(undefined4 *)(param_3 + 0x18);
    *(undefined4 *)(param_3 + 0x3c) = *(undefined4 *)(param_3 + 0x14);
    *(undefined4 *)(param_3 + 0x40) = *(undefined4 *)(param_3 + 0x18);
    goto LAB_00516b1a;
  }
  if (param_2 == 0 || param_2 == 0x80) {
    if (*param_3 == '\x01') {
      param_3[0x14] = '\0';
      param_3[0x15] = '\0';
      param_3[0x16] = '\0';
      param_3[0x17] = '\0';
      param_3[0x18] = '\0';
      param_3[0x19] = '\0';
      param_3[0x1a] = '\0';
      param_3[0x1b] = '\0';
    }
    else {
      *(undefined4 *)(param_3 + 0x14) = *(undefined4 *)(param_3 + 0x3c);
      *(undefined4 *)(param_3 + 0x18) = *(undefined4 *)(param_3 + 0x40);
    }
    *(undefined4 *)(param_3 + 0x2c) = *(undefined4 *)(param_3 + 0x14);
    cVar2 = '\0';
    *(undefined4 *)(param_3 + 0x30) = *(undefined4 *)(param_3 + 0x18);
    param_3[2] = '\0';
  }
  else {
    if (*(int *)(param_3 + 4) == 0) {
      *(undefined4 *)(*DAT_00516230 + 0x120) = 0xffffffff;
      *param_3 = '\x01';
    }
    fVar15 = *(float *)(param_3 + 0x28);
    param_3[2] = '\0';
    if (uVar10 == 6) {
      iVar5 = *(int *)(param_3 + 4);
      iVar8 = *(int *)((int)param_1 + 0xc);
      fVar16 = *(float *)(iVar8 + iVar5 * 4);
      *(float *)(param_3 + 0x1c) = fVar16;
      fVar19 = *(float *)(iVar8 + (iVar5 + 1) * 4);
      *(float *)(param_3 + 0x20) = fVar19;
      fVar21 = *(float *)(iVar8 + (iVar5 + 2) * 4);
      *(float *)(param_3 + 0x24) = fVar21;
      fVar15 = *(float *)(iVar8 + (iVar5 + 3) * 4);
      *(int *)(param_3 + 4) = iVar5 + 4;
      if (!bVar13) {
        *(float *)(param_3 + 0x1c) = fVar16 + *(float *)(param_3 + 0x2c);
        *(float *)(param_3 + 0x20) = fVar19 + *(float *)(param_3 + 0x30);
        fVar21 = fVar21 + *(float *)(param_3 + 0x2c);
        fVar15 = fVar15 + *(float *)(param_3 + 0x30);
      }
      *(float *)(param_3 + 0x24) = fVar21;
      *(undefined4 *)(param_3 + 0x34) = *(undefined4 *)(param_3 + 0x24);
      *(float *)(param_3 + 0x38) = fVar15;
    }
    else {
      if (uVar10 == 5) {
        iVar5 = *(int *)(param_3 + 4);
        iVar8 = *(int *)((int)param_1 + 0xc);
        fVar16 = *(float *)(iVar8 + iVar5 * 4);
        *(float *)(param_3 + 0x1c) = fVar16;
        fVar19 = *(float *)(iVar8 + (iVar5 + 1) * 4);
        *(int *)(param_3 + 4) = iVar5 + 2;
        if (!bVar13) {
          fVar16 = fVar16 + *(float *)(param_3 + 0x2c);
          fVar19 = fVar19 + *(float *)(param_3 + 0x30);
        }
      }
      else {
        if (uVar10 != 7) {
          if (uVar10 == 8) {
            if ((uVar7 == 5 || uVar7 == 7) || (uVar7 == 6 || uVar7 == 8)) {
              fVar15 = *(float *)(param_3 + 0x2c) * 2.0 - *(float *)(param_3 + 0x34);
              fVar16 = *(float *)(param_3 + 0x30) * 2.0 - *(float *)(param_3 + 0x38);
            }
            else {
              fVar15 = *(float *)(param_3 + 0x2c);
              fVar16 = *(float *)(param_3 + 0x30);
            }
            *(float *)(param_3 + 0x1c) = fVar15;
            *(float *)(param_3 + 0x20) = fVar16;
            iVar5 = *(int *)(param_3 + 4);
            iVar8 = *(int *)((int)param_1 + 0xc);
            fVar16 = *(float *)(iVar8 + iVar5 * 4);
            *(float *)(param_3 + 0x24) = fVar16;
            fVar15 = *(float *)(iVar8 + (iVar5 + 1) * 4);
            *(int *)(param_3 + 4) = iVar5 + 2;
            if (!bVar13) {
              fVar16 = fVar16 + *(float *)(param_3 + 0x2c);
              fVar15 = fVar15 + *(float *)(param_3 + 0x30);
            }
            *(float *)(param_3 + 0x24) = fVar16;
            *(undefined4 *)(param_3 + 0x34) = *(undefined4 *)(param_3 + 0x24);
            *(float *)(param_3 + 0x38) = fVar15;
          }
          else if ((param_2 & 0xf) == 9) {
            iVar5 = *(int *)(param_3 + 4);
            iVar8 = *(int *)((int)param_1 + 0xc);
            *(undefined4 *)(param_3 + 0x1c) = *(undefined4 *)(iVar8 + iVar5 * 4);
            *(undefined4 *)(param_3 + 0x20) = *(undefined4 *)(iVar8 + (iVar5 + 1) * 4);
            fVar19 = *(float *)(iVar8 + (iVar5 + 2) * 4);
            *(int *)(param_3 + 4) = iVar5 + 3;
            *(float *)(param_3 + 0x24) = fVar19;
            fVar16 = (float)FUN_0050969c(*(undefined4 *)(*puVar1 + 0xf8),
                                         *(undefined4 *)(*puVar1 + 0xec));
            *(float *)(param_3 + 0x24) = fVar16 + fVar19;
            *(undefined4 *)(param_3 + 0x34) = *(undefined4 *)(param_3 + 0x2c);
            *(undefined4 *)(param_3 + 0x38) = *(undefined4 *)(param_3 + 0x30);
            param_3[3] = cVar3;
          }
          goto LAB_00515a4c;
        }
        if ((uVar7 == 5 || uVar7 == 7) || (uVar7 == 6 || uVar7 == 8)) {
          fVar16 = *(float *)(param_3 + 0x2c) * 2.0 - *(float *)(param_3 + 0x34);
          fVar19 = *(float *)(param_3 + 0x30) * 2.0 - *(float *)(param_3 + 0x38);
        }
        else {
          fVar16 = *(float *)(param_3 + 0x2c);
          fVar19 = *(float *)(param_3 + 0x30);
        }
      }
      *(float *)(param_3 + 0x1c) = fVar16;
      *(float *)(param_3 + 0x20) = fVar19;
      *(undefined4 *)(param_3 + 0x34) = *(undefined4 *)(param_3 + 0x1c);
      *(undefined4 *)(param_3 + 0x38) = *(undefined4 *)(param_3 + 0x20);
    }
LAB_00515a4c:
    *(float *)(param_3 + 0x28) = fVar15;
    if (uVar10 == 4) {
      *(undefined4 *)(param_3 + 0x14) = *(undefined4 *)(param_3 + 0x2c);
      iVar6 = *(int *)(param_3 + 4);
      if (bVar13) {
        *(undefined4 *)(param_3 + 0x18) = *(undefined4 *)(*(int *)((int)param_1 + 0xc) + iVar6 * 4);
      }
      else {
        *(float *)(param_3 + 0x18) =
             *(float *)(param_3 + 0x30) + *(float *)(*(int *)((int)param_1 + 0xc) + iVar6 * 4);
      }
      iVar6 = iVar6 + 1;
LAB_00515a7c:
      *(int *)(param_3 + 4) = iVar6;
    }
    else {
      if (uVar10 != 3) {
        iVar5 = *(int *)(param_3 + 4);
        iVar8 = *(int *)((int)param_1 + 0xc);
        fVar15 = *(float *)(iVar8 + iVar5 * 4);
        if (uVar10 == 10) {
          *(int *)(param_3 + 4) = iVar5 + 1;
          fVar16 = DAT_00515d20;
          iVar5 = (int)fVar15 / 2;
          if (0 < iVar5) {
            local_94 = (float)CONCAT31(local_94._1_3_,cVar3);
            local_90 = param_1;
            do {
              iVar8 = *(int *)(param_3 + 4);
              iVar6 = *(int *)((int)local_90 + 0xc);
              fVar15 = *(float *)(iVar6 + iVar8 * 4);
              if (bVar13) {
                *(float *)(param_3 + 0x14) = fVar15;
                *(int *)(param_3 + 4) = iVar8 + 1;
                *(undefined4 *)(param_3 + 0x18) = *(undefined4 *)(iVar6 + (iVar8 + 1) * 4);
              }
              else {
                *(float *)(param_3 + 0x14) = fVar15 + *(float *)(param_3 + 0x2c);
                *(int *)(param_3 + 4) = iVar8 + 1;
                *(float *)(param_3 + 0x18) =
                     *(float *)(iVar6 + (iVar8 + 1) * 4) + *(float *)(param_3 + 0x30);
              }
              *(int *)(param_3 + 4) = iVar8 + 2;
              *(undefined4 *)(param_3 + 0x2c) = *(undefined4 *)(param_3 + 0x14);
              *(undefined4 *)(param_3 + 0x30) = *(undefined4 *)(param_3 + 0x18);
              param_3[0x44] = local_94._0_1_;
              uVar7 = *puVar1;
              if (*(char *)(uVar7 + 0x7c) == '\0') {
                if (*(char *)(uVar7 + 0x2e4) == '\0') {
                  fVar29 = *(float *)(param_3 + 0xc);
                  fVar15 = *(float *)(param_3 + 0x10);
                  fVar19 = *(float *)(param_3 + 0x14);
                  fVar21 = *(float *)(param_3 + 0x18);
                  if (*(int *)(uVar7 + 0x110) == 0) {
                    uVar10 = 0;
                    if (*(int *)(uVar7 + 0x88) != 0) {
                      uVar10 = 0x7800000;
                    }
                    uVar10 = uVar10 & *(uint *)(uVar7 + 0x8c);
                    if (*(char *)(*DAT_00516238 + 8) == '\x01') {
                      uVar10 = uVar10 | *(uint *)(*DAT_00516238 + 0xc) & 0xc0000000;
                    }
                    puVar4 = (undefined4 *)FUN_00514aec(5);
                    if (puVar4 != (undefined4 *)0x0) {
                      *puVar4 = 800;
                      puVar4[2] = 0x324;
                      puVar4[4] = 0x330;
                      uVar11 = DAT_0051623c;
                      puVar4[1] = fVar29;
                      puVar4[3] = fVar15;
                      puVar4[5] = fVar19;
                      puVar4[6] = 0x334;
                      puVar4[7] = fVar21;
                      puVar4[8] = uVar11;
                      puVar4[9] = uVar10 | 10;
                    }
                  }
                  else {
                    fVar30 = fVar19 - fVar29;
                    fVar17 = fVar21 - fVar15;
                    if ((int)((uint)(ABS(fVar30 * fVar30 + fVar17 * fVar17) < DAT_00515d24) << 0x1f)
                        < 0) {
                      *(float *)(uVar7 + 0x198) = fVar29;
                      *(float *)(uVar7 + 0x19c) = fVar15 + *(float *)(uVar7 + 0x130) * -0.5;
                      *(float *)(uVar7 + 0x1a0) = fVar29;
                      *(float *)(uVar7 + 0x1a4) = fVar15 + *(float *)(uVar7 + 0x130) * 0.5;
                      *(undefined4 *)(uVar7 + 400) = *(undefined4 *)(uVar7 + 0x198);
                      *(undefined4 *)(uVar7 + 0x194) = *(undefined4 *)(uVar7 + 0x19c);
                      uVar7 = *puVar1;
                      *(undefined4 *)(uVar7 + 0x1a8) = *(undefined4 *)(uVar7 + 0x1a0);
                      *(undefined4 *)(uVar7 + 0x1ac) = *(undefined4 *)(uVar7 + 0x1a4);
                    }
                    else {
                      fVar18 = (float)FUN_004397a8();
                      fVar30 = fVar30 * (1.0 / fVar18);
                      fVar17 = fVar17 * (1.0 / fVar18);
                      fVar20 = *(float *)(uVar7 + 0x130) * 0.5 * fVar17;
                      fVar24 = fVar29 - fVar20;
                      fVar23 = *(float *)(uVar7 + 0x134) * 0.5 * fVar30;
                      fVar25 = fVar23 + fVar15;
                      uVar27 = CONCAT44(fVar25,fVar24);
                      *(float *)(uVar7 + 400) = fVar24;
                      *(float *)(uVar7 + 0x194) = fVar25;
                      uVar7 = *puVar1;
                      fVar26 = fVar19 - fVar20;
                      fVar22 = fVar23 + fVar21;
                      *(float *)(uVar7 + 0x198) = fVar26;
                      *(float *)(uVar7 + 0x19c) = fVar22;
                      uVar7 = *puVar1;
                      fVar19 = fVar20 + fVar19;
                      fVar21 = fVar21 - fVar23;
                      *(float *)(uVar7 + 0x1a0) = fVar19;
                      *(float *)(uVar7 + 0x1a4) = fVar21;
                      uVar7 = *puVar1;
                      fVar20 = fVar20 + fVar29;
                      fVar15 = fVar15 - fVar23;
                      uVar28 = CONCAT44(fVar15,fVar20);
                      *(float *)(uVar7 + 0x1a8) = fVar20;
                      *(float *)(uVar7 + 0x1ac) = fVar15;
                      uVar7 = *puVar1;
                      if (*(int *)(uVar7 + 0x110) == 0) {
                        uVar11 = FUN_005226b2(*(undefined4 *)(uVar7 + 0x8c));
                        FUN_00516b34(fVar24,fVar25,fVar26,fVar22,fVar19,fVar21,fVar20,fVar15);
                      }
                      else {
                        bVar14 = -1 < (int)((uint)*(byte *)(uVar7 + 0x7d) << 0x1b);
                        uVar11 = FUN_0052266e(bVar14,0,bVar14,0);
                        uVar7 = *puVar1;
                        if (0.0 < *(float *)(uVar7 + 0x184)) {
                          local_74 = *(undefined4 *)(uVar7 + 0x164);
                          uStack_70 = *(undefined4 *)(uVar7 + 0x168);
                          local_7c = *(float *)(uVar7 + 0x16c);
                          fStack_78 = *(float *)(uVar7 + 0x170);
                          local_84 = *(float *)(uVar7 + 0x174);
                          fStack_80 = *(float *)(uVar7 + 0x178);
                          local_8c = *(float *)(uVar7 + 0x17c);
                          fStack_88 = *(float *)(uVar7 + 0x180);
                          FUN_00516b34(local_74,uStack_70,local_7c,fStack_78,local_84,fStack_80,
                                       local_8c,fStack_88);
                          uVar7 = *puVar1;
                          if ((int)((uint)(ABS(*(float *)(uVar7 + 0x188) * fVar17 -
                                               *(float *)(uVar7 + 0x18c) * fVar30) < fVar16) << 0x1f
                                   ) < 0) {
                            uVar27 = *(undefined8 *)(uVar7 + 0x16c);
                            uVar28 = *(undefined8 *)(uVar7 + 0x174);
                            goto LAB_00515e32;
                          }
                          local_74 = *(undefined4 *)(uVar7 + 0x16c);
                          uStack_70 = *(undefined4 *)(uVar7 + 0x170);
                          local_84 = *(float *)(uVar7 + 0x174);
                          fStack_80 = *(float *)(uVar7 + 0x178);
                          local_8c = fVar20;
                          fStack_88 = fVar15;
                          local_7c = fVar24;
                          fStack_78 = fVar25;
                          iVar8 = FUN_005179d0(&local_74,&local_7c,&local_84,&local_8c,0);
                          if (iVar8 == 0) goto LAB_00515e32;
LAB_00516006:
                          uVar7 = *puVar1;
                          *(undefined4 *)(uVar7 + 0x114) = 0;
                          *(undefined4 *)(uVar7 + 0x118) = 0;
                          FUN_0051565c();
                          goto LAB_00516018;
                        }
LAB_00515e32:
                        uVar7 = *puVar1;
                        if ((0.0 < *(float *)(uVar7 + 0x158)) && (*(int *)(uVar7 + 0x128) == 1)) {
                          if ((int)((uint)(ABS(*(float *)(uVar7 + 0x15c) * fVar17 -
                                               *(float *)(uVar7 + 0x160) * fVar30) < fVar16) << 0x1f
                                   ) < 0) {
                            uVar27 = *(undefined8 *)(uVar7 + 0x140);
                            uVar28 = *(undefined8 *)(uVar7 + 0x148);
                          }
                          else {
                            local_74 = *(undefined4 *)(uVar7 + 0x140);
                            uStack_70 = *(undefined4 *)(uVar7 + 0x144);
                            local_7c = (float)uVar27;
                            fStack_78 = (float)((ulonglong)uVar27 >> 0x20);
                            local_84 = *(float *)(uVar7 + 0x148);
                            fStack_80 = *(float *)(uVar7 + 0x14c);
                            local_8c = (float)uVar28;
                            fStack_88 = (float)((ulonglong)uVar28 >> 0x20);
                            iVar8 = FUN_005179d0(&local_74,&local_7c,&local_84,&local_8c,0);
                            if (iVar8 != 0) goto LAB_00516006;
                          }
                        }
                        uVar7 = *puVar1;
                        *(int *)(uVar7 + 0x128) = *(int *)(uVar7 + 0x128) + 1;
                        uVar9 = (undefined4)((ulonglong)uVar27 >> 0x20);
                        uVar12 = (undefined4)((ulonglong)uVar28 >> 0x20);
                        if (*(float *)(uVar7 + 0x158) == 0.0) {
                          *(int *)(uVar7 + 0x138) = (int)uVar27;
                          *(undefined4 *)(uVar7 + 0x13c) = uVar9;
                          uVar7 = *puVar1;
                          *(float *)(uVar7 + 0x140) = fVar26;
                          *(float *)(uVar7 + 0x144) = fVar22;
                          uVar7 = *puVar1;
                          *(float *)(uVar7 + 0x148) = fVar19;
                          *(float *)(uVar7 + 0x14c) = fVar21;
                          uVar7 = *puVar1;
                          *(int *)(uVar7 + 0x150) = (int)uVar28;
                          *(undefined4 *)(uVar7 + 0x154) = uVar12;
                          uVar7 = *puVar1;
                          *(float *)(uVar7 + 0x158) = fVar18;
                          *(float *)(uVar7 + 0x15c) = fVar30;
                          *(float *)(uVar7 + 0x160) = fVar17;
                        }
                        else {
                          *(int *)(uVar7 + 0x164) = (int)uVar27;
                          *(undefined4 *)(uVar7 + 0x168) = uVar9;
                          uVar7 = *puVar1;
                          *(float *)(uVar7 + 0x16c) = fVar26;
                          *(float *)(uVar7 + 0x170) = fVar22;
                          uVar7 = *puVar1;
                          *(float *)(uVar7 + 0x174) = fVar19;
                          *(float *)(uVar7 + 0x178) = fVar21;
                          uVar7 = *puVar1;
                          *(int *)(uVar7 + 0x17c) = (int)uVar28;
                          *(undefined4 *)(uVar7 + 0x180) = uVar12;
                          uVar7 = *puVar1;
                          *(float *)(uVar7 + 0x184) = fVar18;
                          *(float *)(uVar7 + 0x188) = fVar30;
                          *(float *)(uVar7 + 0x18c) = fVar17;
                        }
                      }
                      FUN_005226b2(uVar11);
                    }
                  }
                }
                else {
                  FUN_005639e8(*(undefined4 *)(param_3 + 0xc),*(undefined4 *)(param_3 + 0x10),
                               *(undefined4 *)(param_3 + 0x14),*(undefined4 *)(param_3 + 0x18));
                }
              }
              else {
                uVar11 = *(undefined4 *)(uVar7 + 0x2d4);
                uVar12 = *(undefined4 *)(uVar7 + 0x2d0);
                puVar4 = (undefined4 *)FUN_00514aec(7);
                if (puVar4 != (undefined4 *)0x0) {
                  uVar7 = *(uint *)(*puVar1 + 0x8c) & 0x7800000;
                  if (*(char *)(*DAT_00516238 + 8) == '\x01') {
                    uVar7 = uVar7 | *(uint *)(*DAT_00516238 + 0xc) & 0xc0000000;
                  }
                  *puVar4 = 800;
                  uVar9 = *(undefined4 *)(param_3 + 0xc);
                  puVar4[2] = 0x324;
                  puVar4[1] = uVar9;
                  uVar9 = *(undefined4 *)(param_3 + 0x10);
                  puVar4[4] = 0x330;
                  puVar4[3] = uVar9;
                  uVar9 = *(undefined4 *)(param_3 + 0x14);
                  puVar4[6] = 0x334;
                  puVar4[5] = uVar9;
                  uVar9 = *(undefined4 *)(param_3 + 0x18);
                  puVar4[8] = 0x140;
                  puVar4[7] = uVar9;
                  puVar4[9] = uVar12;
                  puVar4[10] = 0x144;
                  puVar4[0xb] = uVar11;
                  puVar4[0xc] = DAT_0051623c;
                  puVar4[0xd] = uVar7 | 4;
                }
              }
LAB_00516018:
              *(undefined4 *)(param_3 + 0xc) = *(undefined4 *)(param_3 + 0x14);
              *(undefined4 *)(param_3 + 0x10) = *(undefined4 *)(param_3 + 0x18);
              iVar5 = iVar5 + -1;
            } while (iVar5 != 0);
          }
          if ((*(float *)(param_3 + 0x2c) - *(float *)(param_3 + 0x3c) == 0.0) &&
             (*(float *)(param_3 + 0x30) - *(float *)(param_3 + 0x40) == 0.0)) {
LAB_00516558:
            param_3[1] = '\0';
            return 0;
          }
          *(undefined4 *)(param_3 + 0xc) = *(undefined4 *)(param_3 + 0x14);
          *(undefined4 *)(param_3 + 0x10) = *(undefined4 *)(param_3 + 0x18);
          *(undefined4 *)(param_3 + 0x14) = *(undefined4 *)(param_3 + 0x3c);
          *(undefined4 *)(param_3 + 0x18) = *(undefined4 *)(param_3 + 0x40);
          *(undefined4 *)(param_3 + 0x2c) = *(undefined4 *)(param_3 + 0x3c);
          *(undefined4 *)(param_3 + 0x30) = *(undefined4 *)(param_3 + 0x18);
          uVar7 = *puVar1;
          if (*(char *)(uVar7 + 0x7c) != '\0') {
            uVar12 = *(undefined4 *)(uVar7 + 0x2d4);
            uVar11 = *(undefined4 *)(uVar7 + 0x2d0);
            puVar4 = (undefined4 *)FUN_00514aec(7);
            if (puVar4 != (undefined4 *)0x0) {
              uVar7 = *(uint *)(*puVar1 + 0x8c) & 0x7800000;
              if (*(char *)(*DAT_00516238 + 8) == '\x01') {
                uVar7 = uVar7 | *(uint *)(*DAT_00516238 + 0xc) & 0xc0000000;
              }
              *puVar4 = 800;
              uVar9 = *(undefined4 *)(param_3 + 0xc);
              puVar4[2] = 0x324;
              puVar4[1] = uVar9;
              uVar9 = *(undefined4 *)(param_3 + 0x10);
              puVar4[4] = 0x330;
              puVar4[3] = uVar9;
              uVar9 = *(undefined4 *)(param_3 + 0x14);
              puVar4[6] = 0x334;
              puVar4[5] = uVar9;
              uVar9 = *(undefined4 *)(param_3 + 0x18);
              puVar4[8] = 0x140;
              puVar4[7] = uVar9;
              uVar9 = DAT_0051623c;
              puVar4[9] = uVar11;
              puVar4[10] = 0x144;
              puVar4[0xb] = uVar12;
              puVar4[0xc] = uVar9;
              puVar4[0xd] = uVar7 | 4;
              param_3[1] = '\0';
              return 0;
            }
            goto LAB_00516558;
          }
          if (*(char *)(uVar7 + 0x2e4) != '\0') {
            FUN_005639e8(*(undefined4 *)(param_3 + 0xc),*(undefined4 *)(param_3 + 0x10),
                         *(undefined4 *)(param_3 + 0x14),*(undefined4 *)(param_3 + 0x18));
            goto LAB_00516558;
          }
          fVar21 = *(float *)(param_3 + 0xc);
          fVar15 = *(float *)(param_3 + 0x10);
          fVar16 = *(float *)(param_3 + 0x14);
          fVar19 = *(float *)(param_3 + 0x18);
          if (*(int *)(uVar7 + 0x110) == 0) {
            uVar10 = 0;
            if (*(int *)(uVar7 + 0x88) != 0) {
              uVar10 = 0x7800000;
            }
            uVar10 = *(uint *)(uVar7 + 0x8c) & uVar10;
            if (*(char *)(*DAT_00516238 + 8) == '\x01') {
              uVar10 = *(uint *)(*DAT_00516238 + 0xc) & 0xc0000000 | uVar10;
            }
            puVar4 = (undefined4 *)FUN_00514aec(5);
            if (puVar4 != (undefined4 *)0x0) {
              *puVar4 = 800;
              puVar4[2] = 0x324;
              puVar4[4] = 0x330;
              uVar11 = DAT_0051623c;
              puVar4[1] = fVar21;
              puVar4[3] = fVar15;
              puVar4[5] = fVar16;
              puVar4[6] = 0x334;
              puVar4[7] = fVar19;
              puVar4[8] = uVar11;
              puVar4[9] = uVar10 | 10;
              param_3[1] = '\0';
              return 0;
            }
            goto LAB_00516558;
          }
          fVar29 = fVar16 - fVar21;
          fVar30 = fVar19 - fVar15;
          if ((int)((uint)(ABS(fVar29 * fVar29 + fVar30 * fVar30) < DAT_00516234) << 0x1f) < 0) {
            *(float *)(uVar7 + 0x198) = fVar21;
            *(float *)(uVar7 + 0x19c) = fVar15 + *(float *)(uVar7 + 0x130) * -0.5;
            *(float *)(uVar7 + 0x1a0) = fVar21;
            *(float *)(uVar7 + 0x1a4) = fVar15 + *(float *)(uVar7 + 0x130) * 0.5;
            *(undefined4 *)(uVar7 + 400) = *(undefined4 *)(uVar7 + 0x198);
            *(undefined4 *)(uVar7 + 0x194) = *(undefined4 *)(uVar7 + 0x19c);
            uVar7 = *puVar1;
            *(undefined4 *)(uVar7 + 0x1a8) = *(undefined4 *)(uVar7 + 0x1a0);
            *(undefined4 *)(uVar7 + 0x1ac) = *(undefined4 *)(uVar7 + 0x1a4);
            param_3[1] = '\0';
            return 0;
          }
          fVar17 = (float)FUN_004397a8();
          fVar29 = fVar29 * (1.0 / fVar17);
          fVar30 = fVar30 * (1.0 / fVar17);
          fVar18 = *(float *)(uVar7 + 0x130) * 0.5 * fVar30;
          fVar23 = fVar21 - fVar18;
          fVar20 = *(float *)(uVar7 + 0x134) * 0.5 * fVar29;
          fVar24 = fVar20 + fVar15;
          uVar27 = CONCAT44(fVar24,fVar23);
          *(float *)(uVar7 + 400) = fVar23;
          *(float *)(uVar7 + 0x194) = fVar24;
          uVar7 = *puVar1;
          fVar25 = fVar16 - fVar18;
          fVar26 = fVar20 + fVar19;
          *(float *)(uVar7 + 0x198) = fVar25;
          *(float *)(uVar7 + 0x19c) = fVar26;
          uVar7 = *puVar1;
          fVar16 = fVar18 + fVar16;
          fVar19 = fVar19 - fVar20;
          *(float *)(uVar7 + 0x1a0) = fVar16;
          *(float *)(uVar7 + 0x1a4) = fVar19;
          uVar7 = *puVar1;
          fVar18 = fVar18 + fVar21;
          fVar15 = fVar15 - fVar20;
          uVar28 = CONCAT44(fVar15,fVar18);
          *(float *)(uVar7 + 0x1a8) = fVar18;
          *(float *)(uVar7 + 0x1ac) = fVar15;
          uVar7 = *puVar1;
          if (*(int *)(uVar7 + 0x110) == 0) {
            uVar11 = FUN_005226b2(*(undefined4 *)(uVar7 + 0x8c));
            FUN_00516b34(fVar23,fVar24,fVar25,fVar26,fVar16,fVar19,fVar18,fVar15);
          }
          else {
            bVar13 = -1 < (int)((uint)*(byte *)(uVar7 + 0x7d) << 0x1b);
            uVar11 = FUN_0052266e(bVar13,0,bVar13,0);
            uVar7 = *puVar1;
            if (0.0 < *(float *)(uVar7 + 0x184)) {
              local_7c = *(float *)(uVar7 + 0x164);
              fStack_78 = *(float *)(uVar7 + 0x168);
              local_84 = *(float *)(uVar7 + 0x16c);
              fStack_80 = *(float *)(uVar7 + 0x170);
              local_8c = *(float *)(uVar7 + 0x174);
              fStack_88 = *(float *)(uVar7 + 0x178);
              local_94 = *(float *)(uVar7 + 0x17c);
              local_90 = *(float *)(uVar7 + 0x180);
              FUN_00516b34(local_7c,fStack_78,local_84,fStack_80,local_8c,fStack_88,local_94,
                           local_90);
              uVar7 = *puVar1;
              if ((int)((uint)(ABS(*(float *)(uVar7 + 0x188) * fVar30 -
                                   *(float *)(uVar7 + 0x18c) * fVar29) < DAT_00516704) << 0x1f) < 0)
              {
                uVar27 = *(undefined8 *)(uVar7 + 0x16c);
                uVar28 = *(undefined8 *)(uVar7 + 0x174);
              }
              else {
                local_7c = *(float *)(uVar7 + 0x16c);
                fStack_78 = *(float *)(uVar7 + 0x170);
                local_8c = *(float *)(uVar7 + 0x174);
                fStack_88 = *(float *)(uVar7 + 0x178);
                local_94 = fVar18;
                local_90 = fVar15;
                local_84 = fVar23;
                fStack_80 = fVar24;
                iVar5 = FUN_005179d0(&local_7c,&local_84,&local_8c,&local_94,0);
                if (iVar5 != 0) goto LAB_005164da;
              }
            }
            uVar7 = *puVar1;
            if ((0.0 < *(float *)(uVar7 + 0x158)) && (*(int *)(uVar7 + 0x128) == 1)) {
              if ((int)((uint)(ABS(*(float *)(uVar7 + 0x15c) * fVar30 -
                                   *(float *)(uVar7 + 0x160) * fVar29) < DAT_00516704) << 0x1f) < 0)
              {
                uVar27 = *(undefined8 *)(uVar7 + 0x140);
                uVar28 = *(undefined8 *)(uVar7 + 0x148);
              }
              else {
                local_7c = *(float *)(uVar7 + 0x140);
                fStack_78 = *(float *)(uVar7 + 0x144);
                local_84 = (float)uVar27;
                fStack_80 = (float)((ulonglong)uVar27 >> 0x20);
                local_8c = *(float *)(uVar7 + 0x148);
                fStack_88 = *(float *)(uVar7 + 0x14c);
                local_94 = (float)uVar28;
                local_90 = (float)((ulonglong)uVar28 >> 0x20);
                iVar5 = FUN_005179d0(&local_7c,&local_84,&local_8c,&local_94,0);
                if (iVar5 != 0) {
LAB_005164da:
                  uVar7 = *puVar1;
                  *(undefined4 *)(uVar7 + 0x114) = 0;
                  *(undefined4 *)(uVar7 + 0x118) = 0;
                  FUN_0051565c();
                  param_3[1] = '\0';
                  return 0;
                }
              }
            }
            uVar7 = *puVar1;
            *(int *)(uVar7 + 0x128) = *(int *)(uVar7 + 0x128) + 1;
            uVar9 = (undefined4)((ulonglong)uVar27 >> 0x20);
            uVar12 = (undefined4)((ulonglong)uVar28 >> 0x20);
            if (*(float *)(uVar7 + 0x158) == 0.0) {
              *(int *)(uVar7 + 0x138) = (int)uVar27;
              *(undefined4 *)(uVar7 + 0x13c) = uVar9;
              uVar7 = *puVar1;
              *(float *)(uVar7 + 0x140) = fVar25;
              *(float *)(uVar7 + 0x144) = fVar26;
              uVar7 = *puVar1;
              *(float *)(uVar7 + 0x148) = fVar16;
              *(float *)(uVar7 + 0x14c) = fVar19;
              uVar7 = *puVar1;
              *(int *)(uVar7 + 0x150) = (int)uVar28;
              *(undefined4 *)(uVar7 + 0x154) = uVar12;
              uVar7 = *puVar1;
              *(float *)(uVar7 + 0x158) = fVar17;
              *(float *)(uVar7 + 0x15c) = fVar29;
              *(float *)(uVar7 + 0x160) = fVar30;
            }
            else {
              *(int *)(uVar7 + 0x164) = (int)uVar27;
              *(undefined4 *)(uVar7 + 0x168) = uVar9;
              uVar7 = *puVar1;
              *(float *)(uVar7 + 0x16c) = fVar25;
              *(float *)(uVar7 + 0x170) = fVar26;
              uVar7 = *puVar1;
              *(float *)(uVar7 + 0x174) = fVar16;
              *(float *)(uVar7 + 0x178) = fVar19;
              uVar7 = *puVar1;
              *(int *)(uVar7 + 0x17c) = (int)uVar28;
              *(undefined4 *)(uVar7 + 0x180) = uVar12;
              uVar7 = *puVar1;
              *(float *)(uVar7 + 0x184) = fVar17;
              *(float *)(uVar7 + 0x188) = fVar29;
              *(float *)(uVar7 + 0x18c) = fVar30;
            }
          }
          FUN_005226b2(uVar11);
          param_3[1] = '\0';
          return 0;
        }
        if (uVar10 == 0xb) {
          *(int *)(param_3 + 4) = iVar5 + 1;
          fVar16 = DAT_00516704;
          iVar5 = (int)fVar15 / 2;
          if (0 < iVar5) {
            local_94 = (float)CONCAT31(local_94._1_3_,cVar3);
            local_90 = param_1;
            do {
              iVar8 = *(int *)(param_3 + 4);
              iVar6 = *(int *)((int)local_90 + 0xc);
              fVar15 = *(float *)(iVar6 + iVar8 * 4);
              if (bVar13) {
                *(float *)(param_3 + 0x14) = fVar15;
                *(int *)(param_3 + 4) = iVar8 + 1;
                *(undefined4 *)(param_3 + 0x18) = *(undefined4 *)(iVar6 + (iVar8 + 1) * 4);
              }
              else {
                *(float *)(param_3 + 0x14) = fVar15 + *(float *)(param_3 + 0x2c);
                *(int *)(param_3 + 4) = iVar8 + 1;
                *(float *)(param_3 + 0x18) =
                     *(float *)(iVar6 + (iVar8 + 1) * 4) + *(float *)(param_3 + 0x30);
              }
              *(int *)(param_3 + 4) = iVar8 + 2;
              *(undefined4 *)(param_3 + 0x2c) = *(undefined4 *)(param_3 + 0x14);
              *(undefined4 *)(param_3 + 0x30) = *(undefined4 *)(param_3 + 0x18);
              param_3[0x44] = local_94._0_1_;
              uVar7 = *puVar1;
              if (*(char *)(uVar7 + 0x7c) == '\0') {
                if (*(char *)(uVar7 + 0x2e4) == '\0') {
                  fVar29 = *(float *)(param_3 + 0xc);
                  fVar15 = *(float *)(param_3 + 0x10);
                  fVar19 = *(float *)(param_3 + 0x14);
                  fVar21 = *(float *)(param_3 + 0x18);
                  if (*(int *)(uVar7 + 0x110) == 0) {
                    uVar10 = 0;
                    if (*(int *)(uVar7 + 0x88) != 0) {
                      uVar10 = 0x7800000;
                    }
                    uVar10 = uVar10 & *(uint *)(uVar7 + 0x8c);
                    if (*(char *)(*DAT_005171ec + 8) == '\x01') {
                      uVar10 = uVar10 | *(uint *)(*DAT_005171ec + 0xc) & 0xc0000000;
                    }
                    puVar4 = (undefined4 *)FUN_00514aec(5);
                    if (puVar4 != (undefined4 *)0x0) {
                      *puVar4 = 800;
                      puVar4[2] = 0x324;
                      puVar4[4] = 0x330;
                      uVar11 = DAT_005171f0;
                      puVar4[1] = fVar29;
                      puVar4[3] = fVar15;
                      puVar4[5] = fVar19;
                      puVar4[6] = 0x334;
                      puVar4[7] = fVar21;
                      puVar4[8] = uVar11;
                      puVar4[9] = uVar10 | 10;
                    }
                  }
                  else {
                    fVar30 = fVar19 - fVar29;
                    fVar17 = fVar21 - fVar15;
                    if ((int)((uint)(ABS(fVar30 * fVar30 + fVar17 * fVar17) < DAT_00516788) << 0x1f)
                        < 0) {
                      *(float *)(uVar7 + 0x198) = fVar29;
                      *(float *)(uVar7 + 0x19c) = fVar15 + *(float *)(uVar7 + 0x130) * -0.5;
                      *(float *)(uVar7 + 0x1a0) = fVar29;
                      *(float *)(uVar7 + 0x1a4) = fVar15 + *(float *)(uVar7 + 0x130) * 0.5;
                      *(undefined4 *)(uVar7 + 400) = *(undefined4 *)(uVar7 + 0x198);
                      *(undefined4 *)(uVar7 + 0x194) = *(undefined4 *)(uVar7 + 0x19c);
                      uVar7 = *puVar1;
                      *(undefined4 *)(uVar7 + 0x1a8) = *(undefined4 *)(uVar7 + 0x1a0);
                      *(undefined4 *)(uVar7 + 0x1ac) = *(undefined4 *)(uVar7 + 0x1a4);
                    }
                    else {
                      fVar18 = (float)FUN_004397a8();
                      fVar30 = fVar30 * (1.0 / fVar18);
                      fVar17 = fVar17 * (1.0 / fVar18);
                      fVar20 = *(float *)(uVar7 + 0x130) * 0.5 * fVar17;
                      fVar24 = fVar29 - fVar20;
                      fVar23 = *(float *)(uVar7 + 0x134) * 0.5 * fVar30;
                      fVar25 = fVar23 + fVar15;
                      uVar27 = CONCAT44(fVar25,fVar24);
                      *(float *)(uVar7 + 400) = fVar24;
                      *(float *)(uVar7 + 0x194) = fVar25;
                      uVar7 = *puVar1;
                      fVar26 = fVar19 - fVar20;
                      fVar22 = fVar23 + fVar21;
                      *(float *)(uVar7 + 0x198) = fVar26;
                      *(float *)(uVar7 + 0x19c) = fVar22;
                      uVar7 = *puVar1;
                      fVar19 = fVar20 + fVar19;
                      fVar21 = fVar21 - fVar23;
                      *(float *)(uVar7 + 0x1a0) = fVar19;
                      *(float *)(uVar7 + 0x1a4) = fVar21;
                      uVar7 = *puVar1;
                      fVar20 = fVar20 + fVar29;
                      fVar15 = fVar15 - fVar23;
                      uVar28 = CONCAT44(fVar15,fVar20);
                      *(float *)(uVar7 + 0x1a8) = fVar20;
                      *(float *)(uVar7 + 0x1ac) = fVar15;
                      uVar7 = *puVar1;
                      if (*(int *)(uVar7 + 0x110) == 0) {
                        uVar11 = FUN_005226b2(*(undefined4 *)(uVar7 + 0x8c));
                        FUN_00516b34(fVar24,fVar25,fVar26,fVar22,fVar19,fVar21,fVar20,fVar15);
                      }
                      else {
                        bVar14 = -1 < (int)((uint)*(byte *)(uVar7 + 0x7d) << 0x1b);
                        uVar11 = FUN_0052266e(bVar14,0,bVar14,0);
                        uVar7 = *puVar1;
                        if (0.0 < *(float *)(uVar7 + 0x184)) {
                          local_74 = *(undefined4 *)(uVar7 + 0x164);
                          uStack_70 = *(undefined4 *)(uVar7 + 0x168);
                          local_7c = *(float *)(uVar7 + 0x16c);
                          fStack_78 = *(float *)(uVar7 + 0x170);
                          local_84 = *(float *)(uVar7 + 0x174);
                          fStack_80 = *(float *)(uVar7 + 0x178);
                          local_8c = *(float *)(uVar7 + 0x17c);
                          fStack_88 = *(float *)(uVar7 + 0x180);
                          FUN_00516b34(local_74,uStack_70,local_7c,fStack_78,local_84,fStack_80,
                                       local_8c,fStack_88);
                          uVar7 = *puVar1;
                          if ((int)((uint)(ABS(*(float *)(uVar7 + 0x188) * fVar17 -
                                               *(float *)(uVar7 + 0x18c) * fVar30) < fVar16) << 0x1f
                                   ) < 0) {
                            uVar27 = *(undefined8 *)(uVar7 + 0x16c);
                            uVar28 = *(undefined8 *)(uVar7 + 0x174);
                            goto LAB_00516896;
                          }
                          local_74 = *(undefined4 *)(uVar7 + 0x16c);
                          uStack_70 = *(undefined4 *)(uVar7 + 0x170);
                          local_84 = *(float *)(uVar7 + 0x174);
                          fStack_80 = *(float *)(uVar7 + 0x178);
                          local_8c = fVar20;
                          fStack_88 = fVar15;
                          local_7c = fVar24;
                          fStack_78 = fVar25;
                          iVar8 = FUN_005179d0(&local_74,&local_7c,&local_84,&local_8c,0);
                          if (iVar8 == 0) goto LAB_00516896;
LAB_00516a6a:
                          uVar7 = *puVar1;
                          *(undefined4 *)(uVar7 + 0x114) = 0;
                          *(undefined4 *)(uVar7 + 0x118) = 0;
                          FUN_0051565c();
                          goto LAB_00516a7c;
                        }
LAB_00516896:
                        uVar7 = *puVar1;
                        if ((0.0 < *(float *)(uVar7 + 0x158)) && (*(int *)(uVar7 + 0x128) == 1)) {
                          if ((int)((uint)(ABS(*(float *)(uVar7 + 0x15c) * fVar17 -
                                               *(float *)(uVar7 + 0x160) * fVar30) < fVar16) << 0x1f
                                   ) < 0) {
                            uVar27 = *(undefined8 *)(uVar7 + 0x140);
                            uVar28 = *(undefined8 *)(uVar7 + 0x148);
                          }
                          else {
                            local_74 = *(undefined4 *)(uVar7 + 0x140);
                            uStack_70 = *(undefined4 *)(uVar7 + 0x144);
                            local_7c = (float)uVar27;
                            fStack_78 = (float)((ulonglong)uVar27 >> 0x20);
                            local_84 = *(float *)(uVar7 + 0x148);
                            fStack_80 = *(float *)(uVar7 + 0x14c);
                            local_8c = (float)uVar28;
                            fStack_88 = (float)((ulonglong)uVar28 >> 0x20);
                            iVar8 = FUN_005179d0(&local_74,&local_7c,&local_84,&local_8c,0);
                            if (iVar8 != 0) goto LAB_00516a6a;
                          }
                        }
                        uVar7 = *puVar1;
                        *(int *)(uVar7 + 0x128) = *(int *)(uVar7 + 0x128) + 1;
                        uVar9 = (undefined4)((ulonglong)uVar27 >> 0x20);
                        uVar12 = (undefined4)((ulonglong)uVar28 >> 0x20);
                        if (*(float *)(uVar7 + 0x158) == 0.0) {
                          *(int *)(uVar7 + 0x138) = (int)uVar27;
                          *(undefined4 *)(uVar7 + 0x13c) = uVar9;
                          uVar7 = *puVar1;
                          *(float *)(uVar7 + 0x140) = fVar26;
                          *(float *)(uVar7 + 0x144) = fVar22;
                          uVar7 = *puVar1;
                          *(float *)(uVar7 + 0x148) = fVar19;
                          *(float *)(uVar7 + 0x14c) = fVar21;
                          uVar7 = *puVar1;
                          *(int *)(uVar7 + 0x150) = (int)uVar28;
                          *(undefined4 *)(uVar7 + 0x154) = uVar12;
                          uVar7 = *puVar1;
                          *(float *)(uVar7 + 0x158) = fVar18;
                          *(float *)(uVar7 + 0x15c) = fVar30;
                          *(float *)(uVar7 + 0x160) = fVar17;
                        }
                        else {
                          *(int *)(uVar7 + 0x164) = (int)uVar27;
                          *(undefined4 *)(uVar7 + 0x168) = uVar9;
                          uVar7 = *puVar1;
                          *(float *)(uVar7 + 0x16c) = fVar26;
                          *(float *)(uVar7 + 0x170) = fVar22;
                          uVar7 = *puVar1;
                          *(float *)(uVar7 + 0x174) = fVar19;
                          *(float *)(uVar7 + 0x178) = fVar21;
                          uVar7 = *puVar1;
                          *(int *)(uVar7 + 0x17c) = (int)uVar28;
                          *(undefined4 *)(uVar7 + 0x180) = uVar12;
                          uVar7 = *puVar1;
                          *(float *)(uVar7 + 0x184) = fVar18;
                          *(float *)(uVar7 + 0x188) = fVar30;
                          *(float *)(uVar7 + 0x18c) = fVar17;
                        }
                      }
                      FUN_005226b2(uVar11);
                    }
                  }
                }
                else {
                  FUN_005639e8(*(undefined4 *)(param_3 + 0xc),*(undefined4 *)(param_3 + 0x10),
                               *(undefined4 *)(param_3 + 0x14),*(undefined4 *)(param_3 + 0x18));
                }
              }
              else {
                uVar11 = *(undefined4 *)(uVar7 + 0x2d4);
                uVar12 = *(undefined4 *)(uVar7 + 0x2d0);
                puVar4 = (undefined4 *)FUN_00514aec(7);
                if (puVar4 != (undefined4 *)0x0) {
                  uVar7 = *(uint *)(*puVar1 + 0x8c) & 0x7800000;
                  if (*(char *)(*DAT_005171ec + 8) == '\x01') {
                    uVar7 = uVar7 | *(uint *)(*DAT_005171ec + 0xc) & 0xc0000000;
                  }
                  *puVar4 = 800;
                  uVar9 = *(undefined4 *)(param_3 + 0xc);
                  puVar4[2] = 0x324;
                  puVar4[1] = uVar9;
                  uVar9 = *(undefined4 *)(param_3 + 0x10);
                  puVar4[4] = 0x330;
                  puVar4[3] = uVar9;
                  uVar9 = *(undefined4 *)(param_3 + 0x14);
                  puVar4[6] = 0x334;
                  puVar4[5] = uVar9;
                  uVar9 = *(undefined4 *)(param_3 + 0x18);
                  puVar4[8] = 0x140;
                  puVar4[7] = uVar9;
                  puVar4[9] = uVar12;
                  puVar4[10] = 0x144;
                  puVar4[0xb] = uVar11;
                  puVar4[0xc] = DAT_005171f0;
                  puVar4[0xd] = uVar7 | 4;
                }
              }
LAB_00516a7c:
              *(undefined4 *)(param_3 + 0xc) = *(undefined4 *)(param_3 + 0x14);
              *(undefined4 *)(param_3 + 0x10) = *(undefined4 *)(param_3 + 0x18);
              iVar5 = iVar5 + -1;
            } while (iVar5 != 0);
          }
          if (((*(char *)(*puVar1 + 0x7c) == '\0') ||
              (*(float *)(param_3 + 0x2c) - *(float *)(param_3 + 0x3c) != 0.0)) ||
             (*(float *)(param_3 + 0x30) - *(float *)(param_3 + 0x40) != 0.0)) {
            cVar3 = '\x01';
          }
          else {
            cVar3 = '\0';
          }
          param_3[1] = cVar3;
          return 0;
        }
        if (bVar13) {
          *(float *)(param_3 + 0x14) = fVar15;
          *(int *)(param_3 + 4) = iVar5 + 1;
          iVar6 = iVar5 + 2;
          *(undefined4 *)(param_3 + 0x18) = *(undefined4 *)(iVar8 + (iVar5 + 1) * 4);
        }
        else {
          *(float *)(param_3 + 0x14) = fVar15 + *(float *)(param_3 + 0x2c);
          *(int *)(param_3 + 4) = iVar5 + 1;
          *(float *)(param_3 + 0x18) =
               *(float *)(iVar8 + (iVar5 + 1) * 4) + *(float *)(param_3 + 0x30);
          iVar6 = iVar5 + 2;
        }
        goto LAB_00515a7c;
      }
      fVar15 = *(float *)(*(int *)((int)param_1 + 0xc) + *(int *)(param_3 + 4) * 4);
      if (!bVar13) {
        fVar15 = *(float *)(param_3 + 0x2c) + fVar15;
      }
      *(float *)(param_3 + 0x14) = fVar15;
      *(int *)(param_3 + 4) = *(int *)(param_3 + 4) + 1;
      *(undefined4 *)(param_3 + 0x18) = *(undefined4 *)(param_3 + 0x30);
    }
    if (((*(char *)(*puVar1 + 0x7c) == '\0') ||
        (*(float *)(param_3 + 0x14) - *(float *)(param_3 + 0x3c) != 0.0)) ||
       (*(float *)(param_3 + 0x18) - *(float *)(param_3 + 0x40) != 0.0)) {
      cVar2 = '\x01';
    }
    else {
      cVar2 = '\0';
    }
  }
  param_3[1] = cVar2;
LAB_00516b1a:
  *(undefined4 *)(param_3 + 0x2c) = *(undefined4 *)(param_3 + 0x14);
  *(undefined4 *)(param_3 + 0x30) = *(undefined4 *)(param_3 + 0x18);
  param_3[0x44] = cVar3;
  return 0;
}

