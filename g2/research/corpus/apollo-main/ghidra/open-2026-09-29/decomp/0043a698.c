
/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Type propagation algorithm not settling */
/* WARNING: Restarted to delay deadcode elimination for space: stack */

void FUN_0043a698(float *param_1,int param_2)

{
  undefined1 auVar1 [16];
  undefined1 auVar2 [16];
  undefined1 auVar3 [16];
  undefined1 auVar4 [16];
  undefined1 auVar5 [16];
  undefined1 auVar6 [16];
  char cVar7;
  undefined1 auVar8 [12];
  undefined1 auVar9 [12];
  undefined1 auVar10 [12];
  undefined1 auVar11 [16];
  int iVar12;
  float *pfVar13;
  int *piVar14;
  float *pfVar16;
  int *piVar17;
  float *pfVar18;
  uint uVar19;
  float *pfVar20;
  int iVar21;
  int iVar22;
  float *pfVar23;
  int iVar24;
  float *pfVar25;
  undefined4 uVar26;
  float fVar27;
  undefined1 in_q0 [16];
  undefined1 auVar28 [16];
  undefined1 auVar29 [16];
  float fVar30;
  float fVar31;
  float fVar43;
  undefined1 auVar32 [16];
  undefined1 auVar33 [16];
  undefined1 auVar34 [16];
  undefined1 auVar35 [16];
  undefined1 auVar36 [16];
  undefined1 auVar37 [16];
  undefined1 auVar38 [16];
  undefined1 auVar39 [16];
  undefined1 auVar40 [16];
  undefined1 auVar41 [16];
  undefined1 auVar42 [16];
  float fVar44;
  undefined1 in_q5 [16];
  float fVar45;
  undefined1 in_q6 [16];
  undefined1 auVar46 [16];
  undefined1 in_q7 [16];
  undefined1 auVar47 [16];
  undefined8 uVar48;
  int local_2c8;
  float *local_2c4;
  float *local_2c0;
  float local_2a4;
  undefined1 local_21c;
  undefined1 local_21b;
  undefined1 local_21a;
  int local_218;
  int local_214;
  undefined1 auStack_210 [8];
  float local_208 [12];
  float local_1d8 [3];
  int aiStack_1cc [2];
  float afStack_1c4 [5];
  float local_1b0 [4];
  float local_1a0 [3];
  float local_194;
  float afStack_190 [4];
  undefined4 local_180;
  undefined4 local_17c;
  float local_178 [6];
  float local_160 [6];
  undefined1 auStack_148 [12];
  float fStack_13c;
  undefined1 auStack_138 [12];
  float afStack_12c [5];
  undefined1 local_118 [16];
  undefined1 local_108 [16];
  undefined1 local_f8 [80];
  undefined1 local_a8 [84];
  undefined8 uStack_54;
  undefined8 uStack_4c;
  undefined8 uStack_44;
  undefined8 uStack_3c;
  undefined8 uStack_34;
  undefined8 uStack_2c;
  int *piVar15;
  
  uStack_54 = in_q5._0_8_;
  uStack_4c = in_q5._8_8_;
  uStack_44 = in_q6._0_8_;
  uStack_3c = in_q6._8_8_;
  uStack_34 = in_q7._0_8_;
  uStack_2c = in_q7._8_8_;
  fVar27 = in_q0._8_4_;
  auVar32._4_8_ = uStack_4c;
  auVar32._0_4_ = fVar27;
  auVar32._12_4_ = 0;
  auVar32 = auVar32 << 0x20;
  fVar31 = in_q0._12_4_;
  fVar44 = param_1[0x2c];
  if (((*(char *)(param_1 + 0x2d) != '\x01') && (-1 < (int)((uint)(fVar27 < fVar44) << 0x1f))) &&
     (fVar44 = param_1[0x2b], -1 < (int)((uint)(param_1[0x2b] < fVar27) << 0x1f))) {
    fVar44 = fVar27;
  }
  iVar22 = param_2 + 0x324;
  FUN_00439e9c(iVar22);
  uVar26 = FUN_00439efc(fVar44);
  FUN_00439f24(iVar22);
  fVar27 = (float)FUN_00439f88(uVar26);
  local_21c = *(float *)(param_2 + 0x324) == fVar27;
  local_21b = *(float *)(param_2 + 0x328) == fVar27;
  local_21a = *(float *)(param_2 + 0x32c) == fVar27;
  iVar12 = FUN_00439fb4(&local_21c,aiStack_1cc);
  if (iVar12 == 0) {
    local_208[3] = (float)FUN_0043a5dc(fVar27,iVar22,param_2 + 0x15b4);
    iVar12 = 1;
  }
  else if (0 < iVar12) {
    pfVar16 = local_208 + 3;
    piVar14 = aiStack_1cc;
    do {
      piVar17 = piVar14 + 1;
      *pfVar16 = *(float *)(param_2 + (*piVar14 + 0x56b) * 4 + 4);
      pfVar16 = pfVar16 + 1;
      piVar14 = piVar17;
    } while (aiStack_1cc + iVar12 != piVar17);
  }
  local_2c4 = local_208 + 3;
  FUN_00439ce0(fVar44,*(undefined1 *)(param_1 + 0x2d),iVar22,param_2 + 0x1584,local_160,auStack_210)
  ;
  FUN_0043ba6c(local_160,auStack_210,afStack_190 + 6,&local_218);
  auVar29._4_12_ = auVar32._4_12_;
  auVar29._0_4_ = -fVar31;
  iVar24 = local_218 * 2;
  if (0 < iVar24) {
    iVar21 = 0;
    pfVar16 = afStack_190 + 6;
    do {
      fVar44 = (float)FUN_0043ba98(auVar29._0_4_ / *pfVar16);
      iVar21 = iVar21 + 1;
      *pfVar16 = fVar44;
      pfVar16 = pfVar16 + 1;
    } while (iVar24 != iVar21);
  }
  uVar19 = (uint)*(byte *)(param_1 + 0x2d);
  if (uVar19 == 3) {
    pfVar16 = afStack_190;
    pfVar18 = (float *)(param_2 + 0x159c);
    do {
      *pfVar16 = *pfVar18;
      loopEnd();
      pfVar16 = pfVar16 + 1;
      pfVar18 = pfVar18 + 1;
    } while( true );
  }
  local_180 = 0;
  local_17c = 0;
  auVar32 = VectorStoreRegister(afStack_190,2,4,0);
  if ((int)(uVar19 << 0x18) < 0) {
    iVar24 = 0x3fc;
LAB_0043a80e:
    FUN_00439e90(local_160,param_2 + 0x159c,iVar24);
    if (*(char *)(param_1 + 0x2d) != '\0') {
      pfVar16 = afStack_190;
      pfVar18 = local_160;
      do {
        *pfVar16 = *pfVar18;
        loopEnd();
        pfVar16 = pfVar16 + 1;
        pfVar18 = pfVar18 + 1;
      } while( true );
    }
  }
  else if ((*(byte *)(param_1 + 0x2d) & 0x7f) != 0) {
    iVar24 = (uVar19 & 0x7f) << 3;
    goto LAB_0043a80e;
  }
  auVar8._4_8_ = auVar32._8_8_;
  auVar8._0_4_ = *(float *)(param_2 + 0x324);
  auVar47._0_8_ = auVar8._0_8_ << 0x20;
  auVar47._8_4_ = *(float *)(param_2 + 0x328);
  local_21c = *(float *)(param_2 + 0x324) == fVar27;
  auVar47._12_4_ = *(float *)(param_2 + 0x32c);
  local_21b = auVar47._8_4_ == fVar27;
  local_21a = auVar47._12_4_ == fVar27;
  iVar24 = FUN_00439fb4(&local_21c,aiStack_1cc);
  if (iVar24 == 0) {
    FUN_00439fe4(fVar27,iVar22,afStack_190,local_a8);
  }
  else if (0 < iVar24) {
    piVar17 = aiStack_1cc + iVar24;
    piVar14 = aiStack_1cc;
    pfVar16 = local_160;
    do {
      piVar15 = piVar14 + 1;
      *pfVar16 = afStack_190[*piVar14 + -1];
      piVar14 = piVar15;
      pfVar16 = pfVar16 + 1;
    } while (piVar15 != piVar17);
    pfVar16 = local_160 + iVar24;
    piVar14 = aiStack_1cc;
    do {
      piVar15 = piVar14 + 1;
      *pfVar16 = afStack_190[*piVar14 + 2];
      pfVar16 = pfVar16 + 1;
      piVar14 = piVar15;
    } while (piVar15 != piVar17);
  }
  auVar9._4_8_ = auVar47._8_8_;
  auVar9._0_4_ = *(float *)(param_2 + 0x324);
  auVar33._0_8_ = auVar9._0_8_ << 0x20;
  auVar33._8_4_ = *(float *)(param_2 + 0x328);
  local_21c = *(float *)(param_2 + 0x324) == fVar27;
  auVar33._12_4_ = *(float *)(param_2 + 0x32c);
  local_21b = auVar33._8_4_ == fVar27;
  local_21a = auVar33._12_4_ == fVar27;
  local_2c8 = FUN_00439fb4(&local_21c,aiStack_1cc);
  if (local_2c8 == 0) {
    local_208[6] = (float)FUN_0043a5dc(fVar27,iVar22,param_2 + 0x1578);
    local_2c8 = 1;
  }
  else if (0 < local_2c8) {
    pfVar16 = local_208 + 6;
    piVar14 = aiStack_1cc;
    do {
      piVar17 = piVar14 + 1;
      *pfVar16 = *(float *)(param_2 + (*piVar14 + 0x55d) * 4);
      pfVar16 = pfVar16 + 1;
      piVar14 = piVar17;
    } while (piVar17 != aiStack_1cc + local_2c8);
  }
  local_2c0 = local_208 + 6;
  auVar34._0_8_ = auVar33._0_8_;
  uVar48 = auVar34._0_8_;
  if (0 < iVar12) {
    auVar34._12_4_ = auVar33._12_4_;
    auVar34._8_4_ = param_1[0x19];
    pfVar16 = local_2c4;
    do {
      uVar48 = auVar34._0_8_;
      auVar34._12_4_ = *pfVar16 * auVar34._8_4_;
      *pfVar16 = auVar34._12_4_;
      pfVar16 = pfVar16 + 1;
    } while (pfVar16 != local_2c4 + iVar12);
  }
  if ((int)((uint)(in_q0._4_4_ < 0.0) << 0x1f) < 0) {
    auVar39._8_4_ = param_1[0x2f];
    auVar39._0_8_ = uVar48;
    auVar39._12_4_ = (int)auVar39._8_4_;
    auVar10._4_8_ = auVar39._8_8_;
    auVar10._0_4_ = param_1[0x1c];
    auVar40._0_12_ = auVar10 << 0x20;
    auVar40._12_4_ = param_1[auVar39._12_4_ + 0x2f];
    if ((int)((uint)(auVar40._12_4_ < param_1[0x1c]) << 0x1f) < 0) {
      if (iVar12 < 1) goto LAB_0043a9ae;
      auVar11._4_8_ = auVar40._8_8_;
      auVar11._0_4_ = param_1[0x17];
      auVar11._12_4_ = 0;
      pfVar16 = local_2c4;
      auVar41 = auVar11 << 0x20;
      do {
        auVar32 = auVar41;
        auVar41._0_12_ = auVar32._0_12_;
        auVar41._12_4_ = *pfVar16 * auVar32._4_4_;
        *pfVar16 = auVar41._12_4_;
        pfVar16 = pfVar16 + 1;
      } while (pfVar16 != local_2c4 + iVar12);
      auVar40._12_4_ = param_1[(int)auVar32._8_4_ + 0x2f];
      auVar40._0_12_ = auVar41._0_12_;
    }
    auVar42._12_4_ = auVar40._12_4_;
    auVar42._0_8_ = auVar40._0_8_;
    if ((((int)((uint)(auVar42._12_4_ < DAT_0043b938) << 0x1f) < 0) &&
        ((int)((uint)(param_1[0x1d] < auVar42._12_4_) << 0x1f) < 0)) && (0 < iVar12)) {
      auVar42._8_4_ = param_1[0x18];
      pfVar16 = local_2c4;
      do {
        auVar42._12_4_ = *pfVar16 * auVar42._8_4_;
        *pfVar16 = auVar42._12_4_;
        pfVar16 = pfVar16 + 1;
      } while (local_2c4 + iVar12 != pfVar16);
    }
  }
LAB_0043a9ae:
  local_2a4 = ABS(in_q0._0_4_ - param_1[0x20]);
  fVar44 = ABS(param_1[0x1e] - in_q0._4_4_);
  uVar48 = FUN_0043a110(fVar44);
  iVar22 = FUN_0043baf4((int)uVar48,(int)((ulonglong)uVar48 >> 0x20),DAT_0043aafc,DAT_0043ab00);
  if (iVar22 != 0) {
    uVar48 = FUN_0043a110(local_2a4);
    iVar22 = FUN_0043baf4((int)uVar48,(int)((ulonglong)uVar48 >> 0x20),DAT_0043aafc,DAT_0043ab00);
    if ((iVar22 != 0) && ((int)((uint)(auVar29._4_4_ < 0.0) << 0x1f) < 0)) {
      local_2a4 = local_2a4 / fVar44;
      goto LAB_0043aa12;
    }
  }
  local_2a4 = param_1[0x34];
LAB_0043aa12:
  auVar35._4_4_ = DAT_0043aaf4;
  auVar35._0_4_ = DAT_0043aaf0;
  auVar35._8_4_ = param_1[0x37] * DAT_0043aaf0;
  auVar35._12_4_ = param_1[0x36] * DAT_0043aaf0;
  auVar36._4_12_ = auVar35._4_12_;
  auVar36._0_4_ = local_2a4;
  auVar37._0_8_ = auVar36._0_8_;
  auVar37._8_4_ = auVar35._8_4_ + local_2a4 * DAT_0043aaf4;
  auVar37._12_4_ = -(auVar35._12_4_ + auVar37._8_4_ * DAT_0043aaf4) + auVar37._8_4_ * 2.0;
  local_208[9] = auVar37._12_4_;
  if (((int)((uint)(param_1[0x2c] < auVar29._4_4_) << 0x1f) < 0) || (0.0 <= auVar29._4_4_)) {
    FUN_00439e90(local_208 + 9,local_2c0,local_2c8 << 2);
  }
  FUN_0043bb00(afStack_12c + 1,0,0x40);
  auVar38._12_4_ = (float)(int)param_1[0x2f];
  pfVar16 = afStack_1c4 + 1;
  VectorStoreRegister(pfVar16,2,4,0);
  afStack_12c[(int)auVar38._12_4_ * 5 + -4] = 1.0;
  if (0 < iVar12) {
    auVar38._0_8_ = auVar37._0_8_;
    auVar38._8_4_ = DAT_0043aaf8;
    pfVar18 = local_2c4;
    do {
      auVar38._12_4_ = *pfVar18 * auVar38._8_4_;
      *pfVar18 = auVar38._12_4_;
      pfVar18 = pfVar18 + 1;
    } while (pfVar18 != local_2c4 + iVar12);
  }
  FUN_0043bb14(auVar29._0_4_,local_2c4,iVar12,local_1d8,auStack_210);
  fVar43 = param_1[1];
  fVar30 = param_1[0x2f];
  fVar44 = param_1[0x1e];
  fVar27 = afStack_190[local_218 + 6];
  iVar24 = (int)*param_1 + -1;
  iVar22 = (int)fVar43 + -1;
  afStack_12c[(int)*param_1 + iVar24 * 4] = local_178[0];
  afStack_12c[(int)fVar43 + iVar22 * 4] = fVar27;
  afStack_1c4[(int)fVar30] = local_1d8[0];
  local_194 = fVar27;
  pfVar16[iVar24] = 1.0 - local_178[0];
  pfVar16[iVar22] = 1.0 - fVar27;
  FUN_0043bb14(fVar44 * DAT_0043ab04 * fVar31,local_2c4,iVar12,local_1d8,auStack_210);
  FUN_0043bc58(local_1d8,auStack_210,local_208,&local_218);
  if (0 < local_214) {
    pfVar18 = local_208;
    pfVar23 = pfVar18 + local_214;
    pfVar20 = pfVar18;
    do {
      *pfVar20 = -*pfVar20;
      pfVar20 = pfVar20 + 1;
    } while (pfVar23 != pfVar20);
    do {
      fVar44 = (float)FUN_0043ba98(*pfVar18);
      *pfVar18 = fVar44;
      pfVar18 = pfVar18 + 1;
    } while (pfVar18 != pfVar23);
  }
  VectorLoadRegister(pfVar16,2,4,0);
  auVar28._8_8_ = DAT_0043af80;
  auVar28._0_8_ = DAT_0043af78;
  auVar32 = VectorStoreRegister(auStack_148,2,4,0);
  fVar44 = param_1[0x1e];
  FloatVectorMult(auVar32,auVar28,2,0x20);
  VectorStoreRegister(auStack_138,2,4,0);
  (&fStack_13c)[(int)param_1[0x2e] * 5] = local_208[0];
  iVar22 = FUN_0043a0f4(fVar44);
  auVar46._4_12_ = in_q6._4_12_;
  if (iVar22 == 0) {
    if (param_1[0x1e] < 0.0) {
      auVar46._0_4_ = 0xbf800000;
    }
    else if (param_1[0x1e] == 0.0) {
      auVar46._0_4_ = DAT_0043b93c;
    }
    else {
      auVar46._0_4_ = 0x3f800000;
    }
  }
  else {
    auVar46._0_4_ = *DAT_0043af88;
  }
  pfVar13 = param_1 + 2;
  FUN_0043bb14(fVar31 * DAT_0043af8c,local_2c4,iVar12,local_1d8,auStack_210);
  FUN_0043bc58(local_1d8,auStack_210,local_2c0,&local_218);
  fVar27 = param_1[0x30];
  fVar31 = param_1[0x32];
  fVar30 = param_1[0x1e];
  fVar43 = param_1[0x33];
  iVar12 = (int)param_1[0x2e];
  (&fStack_13c)[iVar12] = local_208[0] - 1.0;
  fVar44 = param_1[0x31];
  fVar45 = auVar46._0_4_;
  afStack_1c4[iVar12] = -(local_208[6] * local_208[0]) * (param_1[iVar12 + 0x2f] * fVar45 + 1.0);
  uVar48 = CONCAT44(fVar27,fVar27);
  auVar1._8_8_ = uVar48;
  auVar1._0_8_ = uVar48;
  auVar32 = VectorLoadRegister(local_118,2,4,0);
  uVar48 = CONCAT44(fVar31,fVar31);
  auVar2._8_8_ = uVar48;
  auVar2._0_8_ = uVar48;
  uVar48 = CONCAT44(fVar44,fVar44);
  auVar3._8_8_ = uVar48;
  auVar3._0_8_ = uVar48;
  uVar48 = CONCAT44(fVar43,fVar43);
  auVar4._8_8_ = uVar48;
  auVar4._0_8_ = uVar48;
  auVar29 = FloatVectorMult(auVar3,auVar32,2,0x20);
  auVar5._8_8_ = CONCAT44(fVar45,fVar45);
  auVar5._0_8_ = CONCAT44(fVar45,fVar45);
  auVar32 = VectorLoadRegister(auStack_138,2,4,0);
  auVar32 = FloatVectorMult(auVar5,auVar32,2,0x20);
  uVar48 = CONCAT44(fVar30,fVar30);
  auVar6._8_8_ = uVar48;
  auVar6._0_8_ = uVar48;
  auVar47 = VectorLoadRegister(auStack_148,2,4,0);
  auVar47 = FloatVectorMult(auVar6,auVar47,2,0x20);
  FloatVectorAdd(auVar32,auVar47,2);
  VectorStoreRegister(local_1b0,2,4,0);
  auVar32 = VectorLoadRegister(afStack_12c + 1,2,4,0);
  auVar47 = FloatVectorMult(auVar1,auVar32,2,0x20);
  auVar32 = VectorLoadRegister(local_108,2,4,0);
  auVar32 = FloatVectorMult(auVar2,auVar32,2,0x20);
  auVar29 = FloatVectorAdd(auVar29,auVar47,2);
  auVar47 = VectorLoadRegister(local_f8,2,4,0);
  auVar29 = FloatVectorAdd(auVar29,auVar32,2);
  auVar32 = FloatVectorMult(auVar4,auVar47,2,0x20);
  FloatVectorAdd(auVar29,auVar32,2);
  VectorStoreRegister(local_1a0,2,4,0);
  param_1[0x30] = local_1a0[0] + local_1b0[0];
  cVar7 = '\0';
  pfVar16 = (float *)0x340;
  pfVar18 = (float *)0x350;
  pfVar20 = (float *)0x360;
  pfVar23 = (float *)0x370;
  pfVar25 = pfVar13;
  do {
    *pfVar16 = *pfVar25;
    pfVar25 = pfVar25 + 1;
    *pfVar18 = *pfVar25;
    pfVar25 = pfVar25 + 1;
    *pfVar20 = *pfVar25;
    pfVar25 = pfVar25 + 1;
    *pfVar23 = *pfVar25;
    pfVar25 = pfVar25 + 1;
    cVar7 = cVar7 + '\x01';
    pfVar16 = pfVar16 + 1;
    pfVar18 = pfVar18 + 1;
    pfVar20 = pfVar20 + 1;
    pfVar23 = pfVar23 + 1;
  } while (cVar7 != '\x04');
  cVar7 = '\0';
  pfVar16 = (float *)0x348;
  pfVar18 = (float *)0x358;
  pfVar20 = (float *)0x368;
  pfVar23 = (float *)0x378;
  do {
    pfVar13 = pfVar13 + 1;
    *pfVar16 = *pfVar13;
    pfVar13 = pfVar13 + 1;
    *pfVar18 = *pfVar13;
    pfVar13 = pfVar13 + 1;
    *pfVar20 = *pfVar13;
    pfVar13 = pfVar13 + 1;
    *pfVar23 = *pfVar13;
    cVar7 = cVar7 + '\x01';
    pfVar16 = pfVar16 + 1;
    pfVar18 = pfVar18 + 1;
    pfVar20 = pfVar20 + 1;
    pfVar23 = pfVar23 + 1;
  } while (cVar7 != '\x04');
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

