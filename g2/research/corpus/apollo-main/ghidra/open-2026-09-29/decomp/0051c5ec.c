
/* WARNING: Instruction at (ram,0x0051cf72) overlaps instruction at (ram,0x0051cf70)
    */

undefined4
FUN_0051c5ec(undefined4 param_1,float param_2,float param_3,undefined4 param_4,float param_5)

{
  uint uVar1;
  char cVar2;
  undefined8 uVar3;
  byte bVar4;
  undefined8 uVar5;
  int *piVar6;
  undefined4 uVar7;
  float *pfVar8;
  int iVar9;
  uint extraout_r1;
  uint extraout_r1_00;
  uint extraout_r1_01;
  uint extraout_r1_02;
  byte bVar10;
  bool bVar11;
  bool bVar12;
  uint in_fpscr;
  uint uVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float extraout_s1;
  float extraout_s1_00;
  float fVar17;
  float extraout_s2;
  float extraout_s2_00;
  float fVar18;
  float fVar19;
  float fVar20;
  float extraout_s4;
  float extraout_s4_00;
  float fVar21;
  float fVar22;
  float afStack_1f4 [4];
  float local_1e4;
  float local_1e0;
  float local_1dc [97];
  
  piVar6 = DAT_0051d2d8;
  iVar9 = *DAT_0051d2d8;
  bVar12 = *(int *)(iVar9 + 0x110) != 0;
  cVar2 = '\0';
  if (bVar12) {
    cVar2 = *(char *)(iVar9 + 0x2e0);
  }
  if (bVar12 && cVar2 != '\0') {
    if (cVar2 == '\x02') {
      fVar14 = *(float *)(iVar9 + 400);
      fVar16 = *(float *)(iVar9 + 0x198);
      uVar13 = in_fpscr & 0xfffffff;
      in_fpscr = uVar13 | (uint)(fVar14 == fVar16) << 0x1e;
      bVar10 = 0;
      if ((byte)(in_fpscr >> 0x1e) != 0) {
        fVar16 = *(float *)(iVar9 + 0x194);
        in_fpscr = uVar13 | (uint)(fVar16 == *(float *)(iVar9 + 0x19c)) << 0x1e;
        bVar10 = (byte)(in_fpscr >> 0x1e);
      }
      if (bVar10 != 0) {
        fVar17 = *(float *)(iVar9 + 0x1a0);
        fVar18 = *(float *)(iVar9 + 0x1a8);
        uVar13 = in_fpscr & 0xfffffff;
        in_fpscr = uVar13 | (uint)(fVar17 == fVar18) << 0x1e;
        bVar10 = 0;
        if ((byte)(in_fpscr >> 0x1e) != 0) {
          fVar18 = *(float *)(iVar9 + 0x1a4);
          in_fpscr = uVar13 | (uint)(fVar18 == *(float *)(iVar9 + 0x1ac)) << 0x1e;
          bVar10 = (byte)(in_fpscr >> 0x1e);
        }
        if (bVar10 != 0) {
          fVar20 = *(float *)(iVar9 + 300) * -0.5;
          bVar12 = -1 < (int)((uint)*(byte *)(iVar9 + 0x7d) << 0x1b);
          uVar7 = FUN_0052266e(bVar12,0,bVar12,bVar12);
          FUN_00516b34(fVar20 + fVar14,fVar16,fVar14,fVar16,fVar17,fVar18,fVar20 + fVar17,fVar18);
          goto LAB_0051c6d8;
        }
      }
      local_1e0 = *(float *)(iVar9 + 0x138);
      local_1dc[0] = *(float *)(iVar9 + 0x13c);
      afStack_1f4[3] = *(float *)(iVar9 + 0x150);
      local_1e4 = *(float *)(iVar9 + 0x154);
      fVar18 = *(float *)(iVar9 + 300) * 0.5;
      uVar13 = in_fpscr & 0xfffffff;
      fVar16 = *(float *)(iVar9 + 0x150);
      uVar3 = *(undefined8 *)(iVar9 + 0x138);
      fVar14 = *(float *)(iVar9 + 0x154);
      bVar10 = 0;
      if (*(float *)(iVar9 + 0x138) < *(float *)(iVar9 + 0x140)) {
        uVar13 = uVar13 | (uint)(fVar16 < *(float *)(iVar9 + 0x148)) << 0x1f;
        bVar10 = (byte)(uVar13 >> 0x1f);
      }
      fVar15 = (float)uVar3;
      fVar21 = fVar16 - fVar15;
      fVar22 = (float)((ulonglong)uVar3 >> 0x20);
      fVar20 = fVar14 - fVar22;
      fVar17 = (float)FUN_00524218(fVar21 * fVar21 + fVar20 * fVar20);
      fVar20 = -(fVar20 / fVar17);
      uVar13 = uVar13 & 0xfffffff | (uint)(fVar20 < 0.0) << 0x1f | (uint)(fVar20 == 0.0) << 0x1e |
               (uint)(0.0 <= fVar20) << 0x1d;
      in_fpscr = uVar13 | (uint)NAN(fVar20) << 0x1c;
      bVar4 = (byte)(uVar13 >> 0x18);
      if (bVar10 == 0) {
        if (!(bool)(bVar4 >> 5 & 1) || (bool)(bVar4 >> 6 & 1)) goto LAB_0051c852;
LAB_0051c810:
        fVar16 = fVar18 * fVar20 + fVar16;
        fVar17 = fVar18 * (fVar21 / fVar17);
        fVar15 = fVar18 * fVar20 + fVar15;
        fVar14 = fVar17 + fVar14;
        fVar17 = fVar17 + fVar22;
      }
      else {
        if ((bool)(bVar4 >> 6 & 1) || bVar4 >> 7 != ((byte)(in_fpscr >> 0x1c) & 1))
        goto LAB_0051c810;
LAB_0051c852:
        fVar16 = fVar16 - fVar18 * fVar20;
        fVar17 = fVar18 * (fVar21 / fVar17);
        fVar15 = fVar15 - fVar18 * fVar20;
        fVar14 = fVar14 - fVar17;
        fVar17 = fVar22 - fVar17;
      }
      bVar12 = -1 < (int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b);
      uVar7 = FUN_0052266e(0,bVar12,bVar12,bVar12);
      FUN_00516b34(local_1e0,local_1dc[0],afStack_1f4[3],local_1e4,fVar16,fVar14,fVar15,fVar17);
      param_2 = extraout_s1_00;
      param_3 = extraout_s2_00;
      param_5 = extraout_s4_00;
      if ((int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b) < 0) goto LAB_0051c6dc;
    }
    else {
      if (cVar2 != '\x01') goto LAB_0051cd0a;
      fVar14 = *(float *)(iVar9 + 400);
      fVar16 = *(float *)(iVar9 + 0x198);
      uVar13 = in_fpscr & 0xfffffff;
      in_fpscr = uVar13 | (uint)(fVar14 == fVar16) << 0x1e;
      bVar10 = 0;
      if ((byte)(in_fpscr >> 0x1e) != 0) {
        fVar16 = *(float *)(iVar9 + 0x194);
        in_fpscr = uVar13 | (uint)(fVar16 == *(float *)(iVar9 + 0x19c)) << 0x1e;
        bVar10 = (byte)(in_fpscr >> 0x1e);
      }
      if (bVar10 != 0) {
        fVar17 = *(float *)(iVar9 + 0x1a0);
        fVar18 = *(float *)(iVar9 + 0x1a8);
        uVar13 = in_fpscr & 0xfffffff;
        in_fpscr = uVar13 | (uint)(fVar17 == fVar18) << 0x1e;
        bVar10 = 0;
        if ((byte)(in_fpscr >> 0x1e) != 0) {
          fVar18 = *(float *)(iVar9 + 0x1a4);
          in_fpscr = uVar13 | (uint)(fVar18 == *(float *)(iVar9 + 0x1ac)) << 0x1e;
          bVar10 = (byte)(in_fpscr >> 0x1e);
        }
        if (bVar10 != 0) {
          fVar20 = *(float *)(iVar9 + 0x2d8);
          fVar21 = (fVar14 - fVar17) / fVar20;
          fVar17 = (fVar14 + fVar17) * 0.5;
          fVar22 = fVar20 * 0.5;
          fVar20 = (fVar16 - fVar18) / fVar20;
          fVar15 = (fVar16 + fVar18) * 0.5;
          iVar9 = FUN_00522f1c(fVar22);
          iVar9 = iVar9 / 2;
          fVar16 = (float)VectorSignedToFloat(iVar9,(byte)(in_fpscr >> 0x16) & 3);
          fVar16 = DAT_0051ccc8 / fVar16;
          fVar14 = (float)FUN_00524130(fVar16);
          fVar18 = (float)FUN_0052405c(fVar16);
          fVar18 = -fVar18;
          local_1e4 = fVar17 - fVar21 * fVar22;
          local_1e0 = fVar15 - fVar20 * fVar22;
          fVar16 = (float)(iVar9 - 1);
          if (1 < iVar9) {
            pfVar8 = afStack_1f4 + 6;
            if (((uint)fVar16 & 3) != 0) {
              do {
                *pfVar8 = fVar17 + fVar22 * fVar21;
                pfVar8[1] = fVar15 + fVar22 * fVar20;
                fVar16 = fVar18 * fVar21;
                fVar21 = fVar14 * fVar21 - fVar18 * fVar20;
                loopEnd();
                pfVar8 = (float *)(extraout_r1 >> 9);
                fVar20 = fVar16 + fVar14 * fVar20;
              } while( true );
            }
            afStack_1f4[3] = fVar16;
            if ((uint)fVar16 >> 2 != 0) {
              do {
                *pfVar8 = fVar17 + fVar22 * fVar21;
                pfVar8[1] = fVar15 + fVar22 * fVar20;
                fVar16 = fVar14 * fVar21 - fVar18 * fVar20;
                pfVar8[2] = fVar17 + fVar22 * fVar16;
                fVar20 = fVar18 * fVar21 + fVar14 * fVar20;
                fVar19 = fVar18 * fVar16 + fVar14 * fVar20;
                fVar16 = fVar14 * fVar16 - fVar18 * fVar20;
                pfVar8[4] = fVar17 + fVar22 * fVar16;
                pfVar8[3] = fVar15 + fVar22 * fVar20;
                fVar21 = fVar18 * fVar16 + fVar14 * fVar19;
                fVar16 = fVar14 * fVar16 - fVar18 * fVar19;
                pfVar8[5] = fVar15 + fVar22 * fVar19;
                pfVar8[6] = fVar17 + fVar22 * fVar16;
                pfVar8[7] = fVar15 + fVar22 * fVar21;
                fVar20 = fVar18 * fVar16 + fVar14 * fVar21;
                fVar21 = fVar14 * fVar16 - fVar18 * fVar21;
                loopEnd();
                pfVar8 = (float *)(extraout_r1 >> 9);
              } while( true );
            }
          }
          uVar7 = FUN_0052266e(0,-(uint)((*(byte *)(*piVar6 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
          FUN_00523a34(afStack_1f4 + 4,fVar16,2);
          bVar12 = -1 < (int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b);
          FUN_0052266e(0,bVar12,bVar12,0);
          FUN_00522a24(local_1e4,local_1e0,afStack_1f4[iVar9 * 2],afStack_1f4[iVar9 * 2 + 1],
                       afStack_1f4[iVar9 * 2 + 2],afStack_1f4[iVar9 * 2 + 3]);
          goto LAB_0051c6d8;
        }
      }
      fVar16 = *(float *)(iVar9 + 0x2d8);
      fVar21 = (*(float *)(iVar9 + 0x150) - *(float *)(iVar9 + 0x138)) / fVar16;
      fVar20 = (*(float *)(iVar9 + 0x150) + *(float *)(iVar9 + 0x138)) * 0.5;
      fVar22 = fVar16 * 0.5;
      fVar16 = (*(float *)(iVar9 + 0x154) - *(float *)(iVar9 + 0x13c)) / fVar16;
      fVar15 = (*(float *)(iVar9 + 0x154) + *(float *)(iVar9 + 0x13c)) * 0.5;
      iVar9 = FUN_00522f1c(fVar22);
      iVar9 = iVar9 / 2;
      fVar14 = (float)VectorSignedToFloat(iVar9,(byte)(in_fpscr >> 0x16) & 3);
      fVar14 = DAT_0051ccc8 / fVar14;
      fVar18 = (float)FUN_00524130(fVar14);
      fVar17 = (float)FUN_0052405c(fVar14);
      fVar17 = -fVar17;
      local_1e4 = fVar20 - fVar21 * fVar22;
      local_1e0 = fVar15 - fVar16 * fVar22;
      fVar14 = (float)(iVar9 - 1);
      if (1 < iVar9) {
        pfVar8 = afStack_1f4 + 6;
        if (((uint)fVar14 & 3) != 0) {
          do {
            *pfVar8 = fVar20 + fVar22 * fVar21;
            pfVar8[1] = fVar15 + fVar22 * fVar16;
            fVar14 = fVar17 * fVar21;
            fVar21 = fVar18 * fVar21 - fVar17 * fVar16;
            loopEnd();
            pfVar8 = (float *)(extraout_r1_00 >> 9);
            fVar16 = fVar14 + fVar18 * fVar16;
          } while( true );
        }
        afStack_1f4[3] = fVar14;
        if ((uint)fVar14 >> 2 != 0) {
          do {
            *pfVar8 = fVar20 + fVar22 * fVar21;
            pfVar8[1] = fVar15 + fVar22 * fVar16;
            fVar14 = fVar18 * fVar21 - fVar17 * fVar16;
            pfVar8[2] = fVar20 + fVar22 * fVar14;
            fVar21 = fVar17 * fVar21 + fVar18 * fVar16;
            fVar19 = fVar17 * fVar14 + fVar18 * fVar21;
            fVar16 = fVar18 * fVar14 - fVar17 * fVar21;
            pfVar8[4] = fVar20 + fVar22 * fVar16;
            pfVar8[3] = fVar15 + fVar22 * fVar21;
            fVar21 = fVar17 * fVar16 + fVar18 * fVar19;
            fVar14 = fVar18 * fVar16 - fVar17 * fVar19;
            pfVar8[5] = fVar15 + fVar22 * fVar19;
            pfVar8[6] = fVar20 + fVar22 * fVar14;
            pfVar8[7] = fVar15 + fVar22 * fVar21;
            fVar16 = fVar17 * fVar14 + fVar18 * fVar21;
            fVar21 = fVar18 * fVar14 - fVar17 * fVar21;
            loopEnd();
            pfVar8 = (float *)(extraout_r1_00 >> 9);
          } while( true );
        }
      }
      uVar7 = FUN_0052266e(0,-(uint)((*(byte *)(*piVar6 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
      FUN_00523a34(afStack_1f4 + 4,fVar14,2);
      bVar12 = -1 < (int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b);
      FUN_0052266e(0,bVar12,bVar12,0);
      FUN_00522a24(local_1e4,local_1e0,afStack_1f4[iVar9 * 2],afStack_1f4[iVar9 * 2 + 1],
                   afStack_1f4[iVar9 * 2 + 2],afStack_1f4[iVar9 * 2 + 3]);
    }
LAB_0051c6d8:
    FUN_005226b2(uVar7);
    param_2 = extraout_s1;
    param_3 = extraout_s2;
    param_5 = extraout_s4;
  }
LAB_0051c6dc:
  iVar9 = *piVar6;
  bVar12 = *(int *)(iVar9 + 0x110) == 0;
  cVar2 = '\0';
  if (!bVar12) {
    cVar2 = *(char *)(iVar9 + 0x2e1);
  }
  if (bVar12 || cVar2 == '\0') {
    return 0;
  }
  if (cVar2 != '\x02') {
    if (cVar2 != '\x01') {
LAB_0051cd0a:
      *(undefined4 *)(iVar9 + 0x114) = 0;
      *(undefined4 *)(iVar9 + 0x118) = 0;
      FUN_0051565c(0x800000);
      return 0x800000;
    }
    fVar16 = *(float *)(iVar9 + 0x198);
    fVar14 = *(float *)(iVar9 + 400);
    uVar13 = in_fpscr & 0xfffffff | (uint)(fVar14 == fVar16) << 0x1e;
    bVar10 = 0;
    if ((byte)(uVar13 >> 0x1e) != 0) {
      param_3 = *(float *)(iVar9 + 0x194);
      uVar13 = in_fpscr & 0xfffffff | (uint)(param_3 == *(float *)(iVar9 + 0x19c)) << 0x1e;
      bVar10 = (byte)(uVar13 >> 0x1e);
    }
    if (bVar10 != 0) {
      fVar17 = *(float *)(iVar9 + 0x1a0);
      fVar18 = *(float *)(iVar9 + 0x1a8);
      uVar1 = uVar13 & 0xfffffff;
      uVar13 = uVar1 | (uint)(fVar17 == fVar18) << 0x1e;
      bVar10 = 0;
      if ((byte)(uVar13 >> 0x1e) != 0) {
        fVar18 = *(float *)(iVar9 + 0x1a4);
        uVar13 = uVar1 | (uint)(fVar18 == *(float *)(iVar9 + 0x1ac)) << 0x1e;
        bVar10 = (byte)(uVar13 >> 0x1e);
      }
      if (bVar10 != 0) {
        fVar16 = *(float *)(iVar9 + 0x2d8);
        fVar21 = (fVar14 - fVar17) / fVar16;
        fVar20 = (fVar14 + fVar17) * 0.5;
        fVar22 = fVar16 * 0.5;
        fVar16 = (param_3 - fVar18) / fVar16;
        fVar15 = (param_3 + fVar18) * 0.5;
        iVar9 = FUN_00522f1c(fVar22);
        iVar9 = iVar9 / 2;
        fVar14 = (float)VectorSignedToFloat(iVar9,(byte)(uVar13 >> 0x16) & 3);
        fVar14 = DAT_0051d090 / fVar14;
        fVar18 = (float)FUN_00524130(fVar14);
        fVar17 = (float)FUN_0052405c(fVar14);
        local_1e4 = fVar20 - fVar21 * fVar22;
        local_1e0 = fVar15 - fVar16 * fVar22;
        fVar14 = (float)(iVar9 - 1);
        if (1 < iVar9) {
          pfVar8 = afStack_1f4 + 6;
          if (((uint)fVar14 & 3) != 0) {
            do {
              *pfVar8 = fVar20 + fVar22 * fVar21;
              pfVar8[1] = fVar15 + fVar22 * fVar16;
              fVar14 = fVar17 * fVar21;
              fVar21 = fVar18 * fVar21 - fVar17 * fVar16;
              loopEnd();
              pfVar8 = (float *)(extraout_r1_01 >> 9);
              fVar16 = fVar14 + fVar18 * fVar16;
            } while( true );
          }
          afStack_1f4[3] = fVar14;
          if ((uint)fVar14 >> 2 != 0) {
            do {
              *pfVar8 = fVar20 + fVar22 * fVar21;
              pfVar8[1] = fVar15 + fVar22 * fVar16;
              fVar14 = fVar18 * fVar21 - fVar17 * fVar16;
              pfVar8[2] = fVar20 + fVar22 * fVar14;
              fVar21 = fVar17 * fVar21 + fVar18 * fVar16;
              fVar19 = fVar17 * fVar14 + fVar18 * fVar21;
              fVar16 = fVar18 * fVar14 - fVar17 * fVar21;
              pfVar8[4] = fVar20 + fVar22 * fVar16;
              pfVar8[3] = fVar15 + fVar22 * fVar21;
              fVar21 = fVar17 * fVar16 + fVar18 * fVar19;
              fVar14 = fVar18 * fVar16 - fVar17 * fVar19;
              pfVar8[5] = fVar15 + fVar22 * fVar19;
              pfVar8[6] = fVar20 + fVar22 * fVar14;
              pfVar8[7] = fVar15 + fVar22 * fVar21;
              fVar16 = fVar17 * fVar14 + fVar18 * fVar21;
              fVar21 = fVar18 * fVar14 - fVar17 * fVar21;
              loopEnd();
              pfVar8 = (float *)(extraout_r1_01 >> 9);
            } while( true );
          }
        }
        uVar7 = FUN_0052266e(0,-(uint)((*(byte *)(*piVar6 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
        FUN_00523a34(afStack_1f4 + 4,fVar14,2);
        bVar12 = -1 < (int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b);
        FUN_0052266e(0,bVar12,bVar12,0);
        FUN_00522a24(local_1e4,local_1e0,afStack_1f4[iVar9 * 2],afStack_1f4[iVar9 * 2 + 1],
                     afStack_1f4[iVar9 * 2 + 2],afStack_1f4[iVar9 * 2 + 3]);
        goto LAB_0051cd56;
      }
    }
    fVar14 = *(float *)(iVar9 + 0x2d8);
    fVar21 = (*(float *)(iVar9 + 0x1a0) - fVar16) / fVar14;
    fVar20 = (*(float *)(iVar9 + 0x1a0) + fVar16) * 0.5;
    fVar22 = fVar14 * 0.5;
    fVar14 = (*(float *)(iVar9 + 0x1a4) - *(float *)(iVar9 + 0x19c)) / fVar14;
    fVar15 = (*(float *)(iVar9 + 0x1a4) + *(float *)(iVar9 + 0x19c)) * 0.5;
    iVar9 = FUN_00522f1c(fVar22);
    iVar9 = iVar9 / 2;
    fVar16 = (float)VectorSignedToFloat(iVar9,(byte)(uVar13 >> 0x16) & 3);
    fVar16 = DAT_0051d2dc / fVar16;
    fVar18 = (float)FUN_00524130(fVar16);
    fVar17 = (float)FUN_0052405c(fVar16);
    local_1e4 = fVar20 - fVar21 * fVar22;
    local_1e0 = fVar15 - fVar14 * fVar22;
    fVar16 = (float)(iVar9 - 1);
    if (1 < iVar9) {
      pfVar8 = afStack_1f4 + 6;
      if (((uint)fVar16 & 3) != 0) {
        do {
          *pfVar8 = fVar20 + fVar22 * fVar21;
          pfVar8[1] = fVar15 + fVar22 * fVar14;
          fVar16 = fVar17 * fVar21;
          fVar21 = fVar18 * fVar21 - fVar17 * fVar14;
          loopEnd();
          pfVar8 = (float *)(extraout_r1_02 >> 9);
          fVar14 = fVar16 + fVar18 * fVar14;
        } while( true );
      }
      afStack_1f4[3] = fVar16;
      if ((uint)fVar16 >> 2 != 0) {
        do {
          *pfVar8 = fVar20 + fVar22 * fVar21;
          pfVar8[1] = fVar15 + fVar22 * fVar14;
          fVar16 = fVar18 * fVar21 - fVar17 * fVar14;
          pfVar8[2] = fVar20 + fVar22 * fVar16;
          fVar14 = fVar17 * fVar21 + fVar18 * fVar14;
          fVar19 = fVar17 * fVar16 + fVar18 * fVar14;
          fVar16 = fVar18 * fVar16 - fVar17 * fVar14;
          pfVar8[4] = fVar20 + fVar22 * fVar16;
          pfVar8[3] = fVar15 + fVar22 * fVar14;
          fVar21 = fVar17 * fVar16 + fVar18 * fVar19;
          fVar16 = fVar18 * fVar16 - fVar17 * fVar19;
          pfVar8[5] = fVar15 + fVar22 * fVar19;
          pfVar8[6] = fVar20 + fVar22 * fVar16;
          pfVar8[7] = fVar15 + fVar22 * fVar21;
          fVar14 = fVar17 * fVar16 + fVar18 * fVar21;
          fVar21 = fVar18 * fVar16 - fVar17 * fVar21;
          loopEnd();
          pfVar8 = (float *)(extraout_r1_02 >> 9);
        } while( true );
      }
    }
    uVar7 = FUN_0052266e(0,-(uint)((*(byte *)(*piVar6 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
    FUN_00523a34(afStack_1f4 + 4,fVar16,2);
    bVar12 = -1 < (int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b);
    FUN_0052266e(0,bVar12,bVar12,0);
    FUN_00522a24(local_1e4,local_1e0,afStack_1f4[iVar9 * 2],afStack_1f4[iVar9 * 2 + 1],
                 afStack_1f4[iVar9 * 2 + 2],afStack_1f4[iVar9 * 2 + 3]);
    goto LAB_0051cd56;
  }
  fVar14 = *(float *)(iVar9 + 0x198);
  fVar16 = *(float *)(iVar9 + 400);
  bVar12 = fVar16 == fVar14;
  if (bVar12) {
    param_2 = *(float *)(iVar9 + 0x194);
    param_3 = *(float *)(iVar9 + 0x19c);
  }
  if (bVar12 && (bVar12 && param_2 == param_3)) {
    fVar17 = *(float *)(iVar9 + 0x1a0);
    fVar18 = *(float *)(iVar9 + 0x1a8);
    bVar12 = fVar17 == fVar18;
    if (bVar12) {
      fVar18 = *(float *)(iVar9 + 0x1a4);
      param_5 = *(float *)(iVar9 + 0x1ac);
    }
    if (bVar12 && (bVar12 && fVar18 == param_5)) {
      fVar14 = *(float *)(iVar9 + 300) * 0.5;
      afStack_1f4[3] = fVar14 + fVar16;
      bVar12 = -1 < (int)((uint)*(byte *)(iVar9 + 0x7d) << 0x1b);
      local_1e4 = param_2;
      local_1e0 = fVar16;
      local_1dc[0] = param_2;
      uVar7 = FUN_0052266e(bVar12,bVar12,bVar12,0);
      FUN_00516b34(local_1e0,local_1dc[0],afStack_1f4[3],local_1e4,fVar14 + fVar17,fVar18,fVar17,
                   fVar18);
      goto LAB_0051cd56;
    }
  }
  bVar12 = fVar16 < fVar14;
  bVar11 = NAN(fVar16) || NAN(fVar14);
  uVar3 = *(undefined8 *)(iVar9 + 0x198);
  uVar5 = *(undefined8 *)(iVar9 + 0x1a0);
  fVar17 = *(float *)(iVar9 + 300) * 0.5;
  fVar16 = *(float *)(iVar9 + 0x1a0);
  fVar20 = *(float *)(iVar9 + 0x19c);
  fVar18 = *(float *)(iVar9 + 0x1a4);
  if (!bVar12) {
    bVar12 = *(float *)(iVar9 + 0x1a8) < fVar16;
    bVar11 = NAN(*(float *)(iVar9 + 0x1a8)) || NAN(fVar16);
  }
  fVar21 = fVar16 - fVar14;
  fVar22 = fVar18 - fVar20;
  fVar15 = (float)FUN_00524218(fVar21 * fVar21 + fVar22 * fVar22);
  fVar22 = -(fVar22 / fVar15);
  if (bVar12 == bVar11) {
    if (fVar22 <= 0.0) goto LAB_0051cdda;
LAB_0051ce1c:
    fVar16 = fVar16 - fVar17 * fVar22;
    fVar15 = fVar17 * (fVar21 / fVar15);
    fVar14 = fVar14 - fVar17 * fVar22;
    fVar18 = fVar18 - fVar15;
    fVar15 = fVar20 - fVar15;
  }
  else {
    if (fVar22 <= 0.0) goto LAB_0051ce1c;
LAB_0051cdda:
    fVar16 = fVar17 * fVar22 + fVar16;
    fVar15 = fVar17 * (fVar21 / fVar15);
    fVar14 = fVar17 * fVar22 + fVar14;
    fVar18 = fVar15 + fVar18;
    fVar15 = fVar15 + fVar20;
  }
  bVar12 = -1 < (int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b);
  uVar7 = FUN_0052266e(0,bVar12,bVar12,bVar12);
  FUN_00516b34((int)uVar3,(int)((ulonglong)uVar3 >> 0x20),(int)uVar5,(int)((ulonglong)uVar5 >> 0x20)
               ,fVar16,fVar18,fVar14,fVar15);
  if ((int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b) < 0) {
    return 0;
  }
LAB_0051cd56:
  FUN_005226b2(uVar7);
  return 0;
}

