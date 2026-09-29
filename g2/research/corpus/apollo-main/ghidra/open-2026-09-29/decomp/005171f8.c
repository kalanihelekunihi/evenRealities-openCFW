
int FUN_005171f8(uint *param_1)

{
  byte bVar1;
  float fVar2;
  int *piVar3;
  float fVar4;
  int iVar5;
  int iVar6;
  undefined4 *puVar7;
  undefined4 uVar8;
  uint uVar9;
  uint uVar10;
  byte bVar11;
  uint uVar12;
  bool bVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  undefined8 uVar24;
  undefined4 uVar25;
  undefined8 uVar26;
  undefined4 uVar27;
  float fVar28;
  float fVar29;
  float local_d4;
  float fStack_d0;
  undefined4 local_cc;
  undefined4 uStack_c8;
  float local_c4;
  float fStack_c0;
  undefined4 local_bc;
  undefined4 uStack_b8;
  undefined1 local_b4 [2];
  char local_b2;
  float local_a8;
  float local_a4;
  float local_a0;
  float local_9c;
  undefined4 local_98;
  undefined4 local_94;
  
  FUN_0048949c(local_b4,0x48);
  piVar3 = DAT_00517850;
  fVar2 = DAT_00517408;
  local_b4[0] = 1;
  local_b2 = '\x01';
  uVar12 = 0;
LAB_0051726c:
  do {
    do {
      if (*param_1 <= uVar12) {
        return 0;
      }
      bVar1 = *(byte *)(param_1[2] + uVar12);
      uVar12 = uVar12 + 1;
      iVar5 = FUN_005156b8(param_1,bVar1,local_b4);
      uVar25 = local_94;
      uVar8 = local_98;
      fVar23 = local_9c;
      fVar22 = local_a0;
      fVar16 = local_a4;
      fVar4 = local_a8;
      bVar11 = bVar1 & 0x6f;
      if (iVar5 != 0) goto LAB_00517294;
    } while ((local_b2 != '\0') || ((int)((uint)bVar1 << 0x18) < 0));
    if (bVar11 == 5 || bVar11 == 7) {
      iVar5 = *piVar3;
      bVar13 = false;
      if (*(char *)(iVar5 + 0x7c) == '\0') {
        if (*(int *)(iVar5 + 0x110) == 1) {
          FUN_00519290(local_a8,local_a4,local_98,local_94,local_a0,local_9c);
          goto LAB_0051726c;
        }
        bVar13 = true;
      }
      uVar9 = 6;
      if (bVar13) {
        uVar9 = 8;
      }
      uVar10 = 0;
      if (*(int *)(iVar5 + 0x88) != 0) {
        if ((*(int *)(iVar5 + 0x114) == 0) || (bVar13)) {
          uVar10 = 0x7800000;
        }
        else {
          uVar10 = 0x4000000;
        }
      }
      uVar10 = uVar10 & *(uint *)(iVar5 + 0x8c);
      if (*(char *)(*DAT_00517858 + 8) == '\x01') {
        uVar10 = uVar10 | *(uint *)(*DAT_00517858 + 0xc) & 0xc0000000;
      }
      puVar7 = (undefined4 *)FUN_00514aec(7);
      if (puVar7 != (undefined4 *)0x0) {
        *puVar7 = 800;
        puVar7[2] = 0x324;
        puVar7[4] = 0x330;
        puVar7[6] = 0x334;
        puVar7[8] = 0x340;
        uVar27 = DAT_00517e04;
        puVar7[1] = fVar4;
        puVar7[3] = fVar16;
        puVar7[5] = uVar8;
        puVar7[7] = uVar25;
        puVar7[9] = fVar22;
        puVar7[10] = 0x344;
        puVar7[0xb] = fVar23;
        puVar7[0xc] = uVar27;
        puVar7[0xd] = uVar9 | uVar10;
      }
      goto LAB_0051726c;
    }
    if ((bVar11 == 6) || (bVar11 == 8)) {
      iVar5 = FUN_00516cf8(local_b4);
    }
    else {
      if ((bVar1 & 0xf) != 9) {
        if (bVar11 != 10 && bVar11 != 0xb) {
          iVar5 = *piVar3;
          if (*(int *)(iVar5 + 0x110) != 0) {
            fVar28 = local_a0 - local_a8;
            fVar29 = local_9c - local_a4;
            if ((int)((uint)(ABS(fVar28 * fVar28 + fVar29 * fVar29) < DAT_00517788) << 0x1f) < 0) {
              *(float *)(iVar5 + 0x198) = local_a8;
              *(float *)(iVar5 + 0x19c) = local_a4 + *(float *)(iVar5 + 0x130) * -0.5;
              *(float *)(iVar5 + 0x1a0) = local_a8;
              *(float *)(iVar5 + 0x1a4) = local_a4 + *(float *)(iVar5 + 0x130) * 0.5;
              *(undefined4 *)(iVar5 + 400) = *(undefined4 *)(iVar5 + 0x198);
              *(undefined4 *)(iVar5 + 0x194) = *(undefined4 *)(iVar5 + 0x19c);
              iVar5 = *piVar3;
              *(undefined4 *)(iVar5 + 0x1a8) = *(undefined4 *)(iVar5 + 0x1a0);
              *(undefined4 *)(iVar5 + 0x1ac) = *(undefined4 *)(iVar5 + 0x1a4);
              goto LAB_0051726c;
            }
            fVar14 = (float)FUN_004397a8();
            fVar28 = fVar28 * (1.0 / fVar14);
            fVar29 = fVar29 * (1.0 / fVar14);
            fVar15 = *(float *)(iVar5 + 0x130) * 0.5 * fVar29;
            fVar18 = fVar4 - fVar15;
            fVar17 = *(float *)(iVar5 + 0x134) * 0.5 * fVar28;
            fVar19 = fVar17 + fVar16;
            uVar26 = CONCAT44(fVar19,fVar18);
            *(float *)(iVar5 + 400) = fVar18;
            *(float *)(iVar5 + 0x194) = fVar19;
            iVar5 = *piVar3;
            fVar20 = fVar22 - fVar15;
            fVar21 = fVar17 + fVar23;
            *(float *)(iVar5 + 0x198) = fVar20;
            *(float *)(iVar5 + 0x19c) = fVar21;
            iVar5 = *piVar3;
            fVar22 = fVar15 + fVar22;
            fVar23 = fVar23 - fVar17;
            *(float *)(iVar5 + 0x1a0) = fVar22;
            *(float *)(iVar5 + 0x1a4) = fVar23;
            iVar5 = *piVar3;
            fVar15 = fVar15 + fVar4;
            fVar16 = fVar16 - fVar17;
            uVar24 = CONCAT44(fVar16,fVar15);
            *(float *)(iVar5 + 0x1a8) = fVar15;
            *(float *)(iVar5 + 0x1ac) = fVar16;
            iVar5 = *piVar3;
            if (*(int *)(iVar5 + 0x110) == 0) {
              uVar8 = FUN_005226b2(*(undefined4 *)(iVar5 + 0x8c));
              FUN_00516b34(fVar18,fVar19,fVar20,fVar21,fVar22,fVar23,fVar15,fVar16);
            }
            else {
              bVar13 = -1 < (int)((uint)*(byte *)(iVar5 + 0x7d) << 0x1b);
              uVar8 = FUN_0052266e(bVar13,0,bVar13,0);
              iVar5 = *piVar3;
              if (0.0 < *(float *)(iVar5 + 0x184)) {
                local_bc = *(undefined4 *)(iVar5 + 0x164);
                uStack_b8 = *(undefined4 *)(iVar5 + 0x168);
                local_c4 = *(float *)(iVar5 + 0x16c);
                fStack_c0 = *(float *)(iVar5 + 0x170);
                local_cc = *(undefined4 *)(iVar5 + 0x174);
                uStack_c8 = *(undefined4 *)(iVar5 + 0x178);
                local_d4 = *(float *)(iVar5 + 0x17c);
                fStack_d0 = *(float *)(iVar5 + 0x180);
                FUN_00516b34(local_bc,uStack_b8,local_c4,fStack_c0,local_cc,uStack_c8,local_d4,
                             fStack_d0);
                iVar5 = *piVar3;
                if ((int)((uint)(ABS(*(float *)(iVar5 + 0x188) * fVar29 -
                                     *(float *)(iVar5 + 0x18c) * fVar28) < fVar2) << 0x1f) < 0) {
                  uVar26 = *(undefined8 *)(iVar5 + 0x16c);
                  uVar24 = *(undefined8 *)(iVar5 + 0x174);
                  goto LAB_0051759a;
                }
                local_bc = *(undefined4 *)(iVar5 + 0x16c);
                uStack_b8 = *(undefined4 *)(iVar5 + 0x170);
                local_cc = *(undefined4 *)(iVar5 + 0x174);
                uStack_c8 = *(undefined4 *)(iVar5 + 0x178);
                local_d4 = fVar15;
                fStack_d0 = fVar16;
                local_c4 = fVar18;
                fStack_c0 = fVar19;
                iVar5 = FUN_005179d0(&local_bc,&local_c4,&local_cc,&local_d4,0);
                if (iVar5 == 0) goto LAB_0051759a;
LAB_0051772c:
                iVar5 = *piVar3;
                *(undefined4 *)(iVar5 + 0x114) = 0;
                *(undefined4 *)(iVar5 + 0x118) = 0;
                FUN_0051565c();
                goto LAB_0051726c;
              }
LAB_0051759a:
              iVar5 = *piVar3;
              if ((0.0 < *(float *)(iVar5 + 0x158)) && (*(int *)(iVar5 + 0x128) == 1)) {
                if ((int)((uint)(ABS(*(float *)(iVar5 + 0x15c) * fVar29 -
                                     *(float *)(iVar5 + 0x160) * fVar28) < fVar2) << 0x1f) < 0) {
                  uVar26 = *(undefined8 *)(iVar5 + 0x140);
                  uVar24 = *(undefined8 *)(iVar5 + 0x148);
                }
                else {
                  local_bc = *(undefined4 *)(iVar5 + 0x140);
                  uStack_b8 = *(undefined4 *)(iVar5 + 0x144);
                  local_c4 = (float)uVar26;
                  fStack_c0 = (float)((ulonglong)uVar26 >> 0x20);
                  local_cc = *(undefined4 *)(iVar5 + 0x148);
                  uStack_c8 = *(undefined4 *)(iVar5 + 0x14c);
                  local_d4 = (float)uVar24;
                  fStack_d0 = (float)((ulonglong)uVar24 >> 0x20);
                  iVar5 = FUN_005179d0(&local_bc,&local_c4,&local_cc,&local_d4,0);
                  if (iVar5 != 0) goto LAB_0051772c;
                }
              }
              iVar5 = *piVar3;
              *(int *)(iVar5 + 0x128) = *(int *)(iVar5 + 0x128) + 1;
              uVar27 = (undefined4)((ulonglong)uVar26 >> 0x20);
              uVar25 = (undefined4)((ulonglong)uVar24 >> 0x20);
              if (*(float *)(iVar5 + 0x158) == 0.0) {
                *(int *)(iVar5 + 0x138) = (int)uVar26;
                *(undefined4 *)(iVar5 + 0x13c) = uVar27;
                iVar5 = *piVar3;
                *(float *)(iVar5 + 0x140) = fVar20;
                *(float *)(iVar5 + 0x144) = fVar21;
                iVar5 = *piVar3;
                *(float *)(iVar5 + 0x148) = fVar22;
                *(float *)(iVar5 + 0x14c) = fVar23;
                iVar5 = *piVar3;
                *(int *)(iVar5 + 0x150) = (int)uVar24;
                *(undefined4 *)(iVar5 + 0x154) = uVar25;
                iVar5 = *piVar3;
                *(float *)(iVar5 + 0x158) = fVar14;
                *(float *)(iVar5 + 0x15c) = fVar28;
                *(float *)(iVar5 + 0x160) = fVar29;
              }
              else {
                *(int *)(iVar5 + 0x164) = (int)uVar26;
                *(undefined4 *)(iVar5 + 0x168) = uVar27;
                iVar5 = *piVar3;
                *(float *)(iVar5 + 0x16c) = fVar20;
                *(float *)(iVar5 + 0x170) = fVar21;
                iVar5 = *piVar3;
                *(float *)(iVar5 + 0x174) = fVar22;
                *(float *)(iVar5 + 0x178) = fVar23;
                iVar5 = *piVar3;
                *(int *)(iVar5 + 0x17c) = (int)uVar24;
                *(undefined4 *)(iVar5 + 0x180) = uVar25;
                iVar5 = *piVar3;
                *(float *)(iVar5 + 0x184) = fVar14;
                *(float *)(iVar5 + 0x188) = fVar28;
                *(float *)(iVar5 + 0x18c) = fVar29;
              }
            }
            FUN_005226b2(uVar8);
            goto LAB_0051726c;
          }
          uVar9 = 0;
          if (*(int *)(iVar5 + 0x88) != 0) {
            uVar9 = 0x7800000;
          }
          uVar9 = uVar9 & *(uint *)(iVar5 + 0x8c);
          if (*(char *)(*DAT_00517858 + 8) == '\x01') {
            uVar9 = uVar9 | *(uint *)(*DAT_00517858 + 0xc) & 0xc0000000;
          }
          puVar7 = (undefined4 *)FUN_00514aec(5);
          if (puVar7 != (undefined4 *)0x0) {
            *puVar7 = 800;
            puVar7[2] = 0x324;
            puVar7[4] = 0x330;
            uVar8 = DAT_00517e04;
            puVar7[1] = fVar4;
            puVar7[3] = fVar16;
            puVar7[5] = fVar22;
            puVar7[6] = 0x334;
            puVar7[7] = fVar23;
            puVar7[8] = uVar8;
            puVar7[9] = uVar9 | 10;
          }
        }
        goto LAB_0051726c;
      }
      iVar5 = FUN_0051a8ec(param_1,local_b4);
    }
    if (iVar5 != 0) {
LAB_00517294:
      iVar6 = *piVar3;
      *(undefined4 *)(iVar6 + 0x114) = 0;
      *(undefined4 *)(iVar6 + 0x118) = 0;
      FUN_0051565c(iVar5);
      return iVar5;
    }
  } while( true );
}

