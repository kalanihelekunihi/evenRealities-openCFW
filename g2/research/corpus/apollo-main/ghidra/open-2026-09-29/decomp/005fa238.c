
void FUN_005fa238(int param_1,int param_2,uint param_3,int param_4)

{
  byte bVar1;
  bool bVar2;
  undefined1 auVar3 [12];
  undefined1 auVar4 [12];
  undefined1 auVar5 [12];
  undefined1 auVar6 [12];
  float *pfVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  uint uVar13;
  int iVar14;
  float *pfVar15;
  int iVar16;
  float *pfVar17;
  uint in_fpscr;
  uint uVar18;
  uint uVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  float fVar24;
  undefined1 auVar25 [12];
  float fVar43;
  undefined1 in_q3 [16];
  undefined1 auVar27 [16];
  undefined1 auVar28 [16];
  undefined1 auVar29 [16];
  undefined4 uVar46;
  undefined1 auVar30 [16];
  undefined1 auVar26 [12];
  undefined1 auVar31 [16];
  float fVar45;
  undefined1 auVar32 [16];
  undefined1 auVar33 [16];
  float fVar47;
  undefined1 auVar34 [16];
  undefined1 auVar35 [16];
  undefined1 auVar36 [16];
  undefined1 auVar37 [16];
  undefined1 auVar38 [16];
  float fVar48;
  undefined1 auVar39 [16];
  undefined1 auVar40 [16];
  undefined1 auVar41 [16];
  undefined1 auVar42 [16];
  float fVar49;
  undefined8 uVar50;
  float fVar51;
  undefined1 auStack_d0 [40];
  undefined1 *local_a8;
  undefined4 *local_a4;
  undefined4 *puStack_a0;
  uint local_94;
  uint local_90;
  uint local_8c;
  uint local_88;
  int local_84;
  undefined1 auStack_80 [16];
  undefined4 local_70;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  float fVar44;
  
  iVar14 = *(int *)(*DAT_005fa4b0 + param_4 * 0x18 + 0x3c);
  local_8c = param_3;
  FUN_004b1516(0,0,iVar14,1);
  iVar12 = 0;
  FUN_00513924(1,param_4,0xffffffff);
  FUN_004b1588(1);
  iVar9 = 0;
  iVar16 = 1;
  auVar27._0_12_ = in_q3._0_12_;
  auVar27._12_4_ = DAT_005fa4bc;
  auVar28._8_8_ = auVar27._8_8_;
  auVar28._0_8_ = 0x3f80000000000000;
  iVar11 = 0;
  iVar8 = iVar11;
  if (0 < param_1) {
    do {
      pfVar7 = (float *)(param_2 + iVar9 * 4);
      iVar10 = param_1 - iVar9;
      iVar11 = iVar8;
      auVar27 = auVar28;
      while( true ) {
        auVar25._0_8_ = auVar27._0_8_;
        auVar25._8_4_ = auVar27._12_4_;
        auVar28._12_4_ = *pfVar7;
        auVar28._0_12_ = auVar25;
        pfVar7 = pfVar7 + 1;
        in_fpscr = in_fpscr & 0xfffffff;
        if (auVar28._12_4_ < auVar27._12_4_) break;
        uVar13 = in_fpscr | (uint)(auVar28._12_4_ < 0.0) << 0x1f;
        uVar18 = uVar13 | (uint)NAN(auVar28._12_4_) << 0x1c;
        if (((byte)(uVar13 >> 0x1f) == ((byte)(uVar18 >> 0x1c) & 1)) &&
           (uVar18 = in_fpscr | (uint)(auVar28._12_4_ == auVar27._4_4_) << 0x1e |
                     (uint)(auVar27._4_4_ <= auVar28._12_4_) << 0x1d, bVar1 = (byte)(uVar18 >> 0x18)
           , !(bool)(bVar1 >> 5 & 1) || (bool)(bVar1 >> 6))) {
          if (iVar11 == 0) {
            uVar13 = in_fpscr | (uint)(auVar28._12_4_ < 0.0) << 0x1f |
                     (uint)(auVar28._12_4_ == 0.0) << 0x1e;
            in_fpscr = uVar13 | (uint)NAN(auVar28._12_4_) << 0x1c;
            bVar1 = (byte)(uVar13 >> 0x18);
            if (!(bool)(bVar1 >> 6 & 1) && bVar1 >> 7 == ((byte)(in_fpscr >> 0x1c) & 1)) {
              iVar11 = 2;
              bVar2 = false;
              iVar12 = iVar9;
              goto LAB_005fa344;
            }
            iVar11 = 1;
            uVar18 = in_fpscr;
          }
          else {
            iVar11 = iVar11 + 1;
            if (1 < iVar11) {
              bVar2 = false;
              iVar12 = iVar9;
              in_fpscr = uVar18;
              goto LAB_005fa344;
            }
          }
        }
        in_fpscr = uVar18;
        iVar9 = iVar9 + 1;
        iVar10 = iVar10 + -1;
        auVar27 = auVar28;
        if (iVar10 == 0) goto joined_r0x005fa2e8;
      }
      bVar2 = true;
      iVar16 = 0;
LAB_005fa344:
      if ((iVar11 == iVar8) || (bVar2)) goto LAB_005fa370;
      if ((iVar12 != 0) || (iVar9 = iVar12, uVar46 = DAT_005fa4bc, 1 < iVar11)) {
        iVar9 = iVar12 + 1;
        uVar46 = *(undefined4 *)(param_2 + iVar12 * 4);
      }
      auVar28._12_4_ = (float)uVar46;
      iVar8 = iVar11;
    } while (iVar9 < param_1);
  }
joined_r0x005fa2e8:
  if (iVar16 != 0) {
    if (0 < iVar11) {
      fVar45 = *(float *)(param_2 + iVar12 * 4);
      auVar6._4_8_ = 0;
      auVar6._0_4_ = fVar45;
      auVar28._0_12_ = auVar6 << 0x40;
      auVar28._12_4_ = 1.0;
      in_fpscr = in_fpscr & 0xfffffff;
      iVar16 = 1;
      if (1.0 <= fVar45) goto LAB_005fa376;
      if (iVar11 == -1) goto LAB_005fa2ec;
LAB_005fa37a:
      uVar50 = CONCAT44(DAT_005fa4b8,DAT_005fa4b8);
      iVar9 = 0;
      iVar11 = 0;
      iVar12 = 0;
      fVar45 = DAT_005fa4b8;
      fVar47 = DAT_005fa4b8;
      fVar49 = DAT_005fa4b8;
      fVar43 = DAT_005fa4b8;
      local_90 = iVar14;
      local_88 = iVar16;
      local_84 = iVar16;
      auVar41._0_4_ = DAT_005fa4b8;
      fVar51 = DAT_005fa4b8;
      do {
        auVar29._0_12_ = auVar28._0_12_;
        if ((iVar11 != 0) || (iVar8 = iVar11, uVar46 = DAT_005fa4bc, 1 < iVar12)) {
          iVar8 = iVar11 + 1;
          uVar46 = *(undefined4 *)(param_2 + iVar11 * 4);
        }
        auVar29._12_4_ = uVar46;
        iVar14 = iVar12;
        if (iVar8 < param_1) {
          auVar30._8_8_ = auVar29._8_8_;
          auVar30._0_8_ = 0x3f80000000000000;
          pfVar7 = (float *)(param_2 + iVar8 * 4);
          iVar10 = param_1 - iVar8;
          do {
            while( true ) {
              auVar26._0_8_ = auVar30._0_8_;
              auVar26._8_4_ = auVar30._12_4_;
              auVar31._12_4_ = *pfVar7;
              auVar31._0_12_ = auVar26;
              pfVar7 = pfVar7 + 1;
              in_fpscr = in_fpscr & 0xfffffff;
              uVar13 = local_84;
              if (auVar31._12_4_ < auVar30._12_4_) {
                local_88 = 0;
                iVar8 = iVar11;
                goto LAB_005fa4c8;
              }
              uVar18 = in_fpscr | (uint)(auVar31._12_4_ < 0.0) << 0x1f;
              uVar19 = uVar18 | (uint)NAN(auVar31._12_4_) << 0x1c;
              if (((byte)(uVar18 >> 0x1f) == ((byte)(uVar19 >> 0x1c) & 1)) &&
                 (uVar19 = in_fpscr | (uint)(auVar31._12_4_ == auVar30._4_4_) << 0x1e |
                           (uint)(auVar30._4_4_ <= auVar31._12_4_) << 0x1d,
                 bVar1 = (byte)(uVar19 >> 0x18), !(bool)(bVar1 >> 5 & 1) || (bool)(bVar1 >> 6)))
              break;
LAB_005fa3de:
              in_fpscr = uVar19;
              iVar10 = iVar10 + -1;
              iVar8 = iVar8 + 1;
              auVar30 = auVar31;
              if (iVar10 == 0) goto LAB_005fa42a;
            }
            if (iVar14 != 0) {
              iVar14 = iVar14 + 1;
              if (iVar14 < 2) goto LAB_005fa3de;
              iVar9 = iVar11;
              uVar13 = 0;
              in_fpscr = uVar19;
              goto LAB_005fa4c8;
            }
            uVar18 = in_fpscr | (uint)(auVar31._12_4_ < 0.0) << 0x1f |
                     (uint)(auVar31._12_4_ == 0.0) << 0x1e;
            in_fpscr = uVar18 | (uint)NAN(auVar31._12_4_) << 0x1c;
            bVar1 = (byte)(uVar18 >> 0x18);
            if (!(bool)(bVar1 >> 6 & 1) && bVar1 >> 7 == ((byte)(in_fpscr >> 0x1c) & 1)) {
              iVar14 = 2;
              iVar9 = iVar8;
              uVar13 = 0;
              goto LAB_005fa4c8;
            }
            iVar10 = iVar10 + -1;
            iVar14 = 1;
            iVar8 = iVar8 + 1;
            auVar30 = auVar31;
          } while (iVar10 != 0);
LAB_005fa42a:
          iVar8 = iVar11;
          if ((local_88 != 0) && (uVar13 = local_88, 0 < iVar14)) {
            pfVar7 = (float *)(param_2 + iVar11 * 4);
            auVar26._8_4_ = *pfVar7;
            in_fpscr = in_fpscr & 0xfffffff;
            if (auVar26._8_4_ < 1.0) {
              iVar14 = iVar14 + 1;
              if (iVar14 != iVar12) goto LAB_005fa62c;
              break;
            }
          }
LAB_005fa4c8:
          if (iVar14 == iVar12) break;
          pfVar17 = (float *)(param_2 + iVar8 * 4);
          pfVar7 = pfVar17;
          if (iVar9 == iVar8) goto LAB_005fa62c;
          auVar32._12_4_ = local_90;
          auVar32._0_12_ = auVar26;
          auVar3._4_8_ = auVar32._8_8_;
          auVar3._0_4_ = local_90 + -1;
          auVar42._0_8_ = auVar3._0_8_ << 0x20;
          pfVar7 = (float *)(param_2 + iVar9 * 4);
          fVar24 = (float)VectorUnsignedToFloat(local_90,(byte)(in_fpscr >> 0x16) & 3);
LAB_005fa4fc:
          auVar33._8_4_ =
               (float)VectorUnsignedToFloat
                                ((int)((ulonglong)auVar42._0_8_ >> 0x20),
                                 (byte)(in_fpscr >> 0x16) & 3);
          auVar33._0_8_ = auVar42._0_8_;
          auVar33._12_4_ = *pfVar7 * auVar33._8_4_;
          fVar43 = auVar33._12_4_ + 0.5;
          auVar4._4_8_ = auVar33._8_8_;
          auVar4._0_4_ = fVar43;
          auVar34._0_8_ = auVar4._0_8_ << 0x20;
          local_94 = (uint)(*pfVar7 * fVar24);
          fVar47 = (float)VectorSignedToFloat((int)fVar43,(byte)(in_fpscr >> 0x16) & 3);
          auVar34._8_4_ = auVar33._8_4_ * *pfVar17 + 0.5;
          pfVar7 = (float *)(local_8c + iVar9 * 0x10);
          pfVar15 = (float *)(iVar8 * 0x10 + local_8c);
          auVar41._0_4_ = pfVar15[3];
          auVar34._12_4_ = fVar43 - fVar47;
          fVar20 = *pfVar7;
          fVar21 = pfVar7[1];
          fVar23 = pfVar7[2];
          auVar35._4_12_ = auVar34._4_12_;
          auVar35._0_4_ = pfVar7[3];
          uVar18 = (int)(*pfVar17 * fVar24) - local_94;
          fVar43 = *pfVar15;
          fVar47 = pfVar15[2];
          fVar49 = pfVar15[1];
        }
        else {
          if ((local_88 == 0) || (iVar12 < 1)) break;
          pfVar7 = (float *)(param_2 + iVar11 * 4);
          auVar26._0_8_ = auVar28._0_8_;
          auVar26._8_4_ = *pfVar7;
          in_fpscr = in_fpscr & 0xfffffff;
          iVar8 = iVar11;
          uVar13 = local_88;
          if (1.0 <= auVar26._8_4_) goto LAB_005fa4c8;
          iVar14 = iVar12 + 1;
          uVar13 = local_88;
LAB_005fa62c:
          auVar39._12_4_ = *pfVar7;
          auVar39._8_4_ = local_90;
          auVar39._0_8_ = auVar26._0_8_;
          fVar24 = (float)VectorUnsignedToFloat(local_90,(byte)(in_fpscr >> 0x16) & 3);
          auVar5._4_8_ = auVar39._8_8_;
          auVar5._0_4_ = local_90 + -1;
          auVar40._0_8_ = auVar5._0_8_ << 0x20;
          fVar43 = (float)VectorUnsignedToFloat(local_90 + -1,(byte)(in_fpscr >> 0x16) & 3);
          auVar40._8_4_ = fVar43 * auVar39._12_4_;
          auVar40._12_4_ = (uint)(auVar39._12_4_ * fVar24);
          pfVar17 = (float *)(local_8c + iVar8 * 0x10);
          fVar20 = *pfVar17;
          fVar21 = pfVar17[1];
          fVar23 = pfVar17[2];
          auVar41._4_12_ = auVar40._4_12_;
          auVar41._0_4_ = pfVar17[3];
          auVar42._0_8_ = auVar41._0_8_;
          auVar42._8_4_ = auVar40._8_4_ + 0.5;
          iVar9 = iVar8;
          fVar43 = fVar20;
          fVar47 = fVar23;
          fVar49 = fVar21;
          if (iVar14 == 2) {
            auVar42._12_4_ = 0x3f000000;
            auVar35._8_8_ = auVar42._8_8_;
            auVar35._4_4_ = 0x3f000000;
            auVar35._0_4_ = auVar41._0_4_;
            local_94 = 0;
            uVar18 = auVar40._12_4_;
          }
          else {
            pfVar17 = pfVar7;
            if (iVar14 < 3) goto LAB_005fa4fc;
            fVar22 = (float)VectorSignedToFloat((int)auVar42._8_4_,(byte)(in_fpscr >> 0x16) & 3);
            auVar35._4_4_ = auVar42._8_4_;
            auVar35._0_4_ = auVar41._0_4_;
            auVar35._12_4_ = auVar42._8_4_ - fVar22;
            auVar35._8_4_ = fVar24 - 0.5;
            uVar18 = local_90 - auVar40._12_4_;
            local_94 = auVar40._12_4_;
          }
        }
        auVar36._12_4_ = auVar35._12_4_;
        uVar19 = in_fpscr & 0xfffffff | (uint)(auVar36._12_4_ < 0.5) << 0x1f |
                 (uint)(auVar36._12_4_ == 0.5) << 0x1e;
        in_fpscr = uVar19 | (uint)NAN(auVar36._12_4_) << 0x1c;
        auVar36._0_8_ = auVar35._0_8_;
        auVar36._8_4_ = auVar35._8_4_ - auVar35._4_4_;
        bVar1 = (byte)(uVar19 >> 0x18);
        auVar37._8_8_ = auVar36._8_8_;
        fVar44 = auVar41._0_4_ - auVar35._0_4_;
        auVar37._0_8_ = CONCAT44(fVar44,auVar35._0_4_);
        fVar24 = (fVar43 - fVar20) / auVar36._8_4_;
        fVar22 = (fVar49 - fVar21) / auVar36._8_4_;
        if ((bool)(bVar1 >> 6 & 1) || bVar1 >> 7 != ((byte)(in_fpscr >> 0x1c) & 1)) {
          auVar38._0_12_ = auVar37._0_12_;
          auVar38._12_4_ = 0.5 - auVar36._12_4_;
        }
        else {
          auVar38._8_4_ = 0x3fc00000;
          auVar38._0_8_ = auVar37._0_8_;
          auVar38._12_4_ = 1.5 - auVar36._12_4_;
        }
        fVar48 = auVar38._12_4_;
        auVar28._0_12_ = auVar38._0_12_;
        auVar28._12_4_ = (fVar44 / auVar36._8_4_) * fVar48;
        fVar44 = auVar28._12_4_ + auVar38._0_4_;
        fVar20 = fVar24 * fVar48 + fVar20;
        fVar21 = fVar22 * fVar48 + fVar21;
        fVar23 = ((fVar47 - fVar23) / auVar36._8_4_) * fVar48 + fVar23;
        FUN_004b199c(fVar20,fVar21,fVar23,fVar44,fVar24,DAT_005fa4b8,fVar22,DAT_005fa4b8);
        local_a8 = (undefined1 *)0xffffffff;
        FUN_004b1ab0(local_94,0,uVar18,1);
        if (iVar16 == 1) {
          uVar50 = CONCAT44(fVar23,fVar20);
          fVar45 = fVar21;
          fVar51 = fVar44;
        }
        iVar11 = iVar8;
        iVar12 = iVar14;
        iVar16 = uVar13;
      } while (uVar13 != 1);
      FUN_004b1588(0);
      local_94 = (uint)(0.0 < fVar51) * (int)fVar51;
      fVar51 = (float)((ulonglong)uVar50 >> 0x20);
      local_90 = (uint)(0.0 < fVar51) * (int)fVar51;
      local_8c = (uint)(0.0 < fVar45) * (int)fVar45;
      local_88 = (uint)(0.0 < (float)uVar50) * (int)(float)uVar50;
      local_a8 = (undefined1 *)
                 FUN_004b15a6(local_88 & 0xff,local_8c & 0xff,local_90 & 0xff,local_94 & 0xff);
      FUN_004b1ab0(0,0,1);
      local_94 = (uint)(0.0 < auVar41._0_4_) * (int)auVar41._0_4_;
      local_90 = (uint)(0.0 < fVar47) * (int)fVar47;
      local_8c = (uint)(0.0 < fVar49) * (int)fVar49;
      local_88 = (uint)(0.0 < fVar43) * (int)fVar43;
      local_a8 = (undefined1 *)
                 FUN_004b15a6(local_88 & 0xff,local_8c & 0xff,local_90 & 0xff,local_94 & 0xff);
      FUN_004b1ab0(0x3f,0,1);
      goto LAB_005fa328;
    }
LAB_005fa370:
    if (iVar16 != 0) {
LAB_005fa376:
      if (iVar11 != 0) goto LAB_005fa37a;
    }
  }
LAB_005fa2ec:
  local_a4 = &local_70;
  local_70 = *DAT_005fa4b4;
  uStack_6c = DAT_005fa4b4[1];
  uStack_68 = DAT_005fa4b4[2];
  uStack_64 = DAT_005fa4b4[3];
  local_a8 = auStack_80;
  VectorStoreRegister(auStack_d0,2,4,0);
  puStack_a0 = local_a4;
  FUN_005f9f14(0,0,iVar14,1);
  local_a8 = (undefined1 *)0xffffffff;
  FUN_004b1ab0(0,0,iVar14,1);
LAB_005fa328:
  FUN_004b1588(0);
  FUN_004b1548();
  return;
}

