
void FUN_0043a1b0(float param_1,float param_2,float param_3,int param_4,int param_5,
                 undefined4 *param_6,float *param_7)

{
  undefined1 auVar1 [12];
  bool bVar2;
  byte bVar3;
  undefined4 *puVar4;
  int iVar5;
  undefined4 uVar6;
  int *piVar7;
  undefined1 uVar9;
  undefined4 uVar10;
  float *pfVar11;
  int iVar12;
  char cVar13;
  undefined1 auVar14 [12];
  float fVar19;
  undefined1 in_q3 [16];
  undefined1 auVar15 [16];
  undefined1 auVar16 [16];
  undefined1 auVar17 [16];
  float fVar20;
  undefined1 auVar18 [16];
  undefined1 local_60 [20];
  undefined1 local_4c;
  undefined1 local_4b;
  undefined1 local_4a;
  float local_48 [3];
  int aiStack_3c [4];
  int *piVar8;
  
  param_6[1] = 0x40000000;
  *param_6 = 0x3f800000;
  FUN_00439e90(param_6 + 2,param_4,0x40);
  param_6[0x12] = *(undefined4 *)(param_4 + 0x40);
  uVar6 = DAT_0043a550;
  param_6[0x13] = *(undefined4 *)(param_4 + 0x44);
  param_6[0x14] = uVar6;
  puVar4 = DAT_0043a548;
  param_6[0x15] = *(undefined4 *)(param_4 + 0x48);
  uVar10 = *puVar4;
  param_6[0x16] = *(undefined4 *)(param_4 + 0x4c);
  param_6[0x17] = *(undefined4 *)(param_4 + 0x50);
  param_6[0x18] = *(undefined4 *)(param_4 + 0x54);
  param_6[0x19] = *(undefined4 *)(param_4 + 0x58);
  param_6[0x1a] = *(undefined4 *)(param_4 + 0x5c);
  param_6[0x1b] = *(undefined4 *)(param_4 + 0x60);
  param_6[0x1c] = *(undefined4 *)(param_4 + 100);
  uVar6 = *(undefined4 *)(param_4 + 0x68);
  *(undefined1 *)(param_6 + 0x25) = 0;
  param_6[0x1e] = 0;
  param_6[0x1f] = 0;
  param_6[0x20] = 0;
  param_6[0x21] = uVar10;
  param_6[0x22] = uVar10;
  param_6[0x23] = uVar10;
  param_6[0x24] = uVar10;
  param_6[0x1d] = uVar6;
  param_6[0x26] = 0;
  param_6[0x27] = uVar10;
  param_6[0x28] = uVar10;
  param_6[0x29] = uVar10;
  param_6[0x2a] = uVar10;
  auVar15._12_4_ = in_q3._12_4_;
  auVar15._0_8_ = in_q3._0_8_;
  auVar15._8_4_ = *(float *)(param_5 + 0x324);
  fVar19 = *(float *)(param_5 + 0x328);
  auVar1._4_8_ = auVar15._8_8_;
  auVar1._0_4_ = fVar19;
  auVar17._0_12_ = auVar1 << 0x20;
  bVar3 = (byte)(((uint)(auVar15._8_4_ == fVar19) << 0x1e) >> 0x18);
  cVar13 = -((char)((byte)(((uint)(auVar15._8_4_ < fVar19) << 0x1f) >> 0x18) | bVar3) >> 7);
  if ((bool)cVar13 == (NAN(auVar15._8_4_) || NAN(fVar19))) {
    auVar17._12_4_ = auVar15._8_4_;
    uVar9 = 1;
  }
  else {
    if (cVar13 == '\0') {
      auVar16._4_12_ = auVar1;
      auVar16._0_4_ = auVar15._8_4_;
      auVar14 = auVar16._0_12_;
      if (!(bool)(bVar3 >> 6) && (!NAN(auVar15._8_4_) && !NAN(fVar19))) {
        auVar14._0_8_ = auVar16._0_8_;
        auVar14._8_4_ = fVar19;
      }
    }
    else {
      auVar18._4_12_ = auVar1;
      auVar18._0_4_ = fVar19;
      auVar14 = auVar18._0_12_;
    }
    auVar17._12_4_ = *(float *)(param_5 + 0x32c);
    auVar17._0_12_ = auVar14;
    fVar19 = auVar14._0_4_;
    if (auVar17._12_4_ <= auVar14._4_4_) {
      auVar17._12_4_ = fVar19;
      uVar9 = 2;
LAB_0043a2a4:
      auVar15._8_4_ = auVar17._8_4_;
    }
    else {
      auVar15._8_4_ = auVar14._8_4_;
      if (-1 < (int)((uint)(fVar19 < auVar17._12_4_) << 0x1f)) {
        if (auVar17._12_4_ < auVar15._8_4_) {
          auVar17._0_8_ = auVar14._0_8_;
          auVar17._8_4_ = auVar17._12_4_;
          uVar9 = 3;
          auVar17._12_4_ = fVar19;
        }
        else {
          auVar17._12_4_ = fVar19;
          uVar9 = 3;
        }
        goto LAB_0043a2a4;
      }
      uVar9 = 3;
    }
    if ((int)((uint)(param_3 < auVar15._8_4_) << 0x1f) < 0) {
      auVar15._8_4_ = auVar17._8_4_;
    }
    else {
      fVar19 = auVar17._12_4_;
      auVar15._8_4_ =
           (float)((uint)(fVar19 < param_3) * (int)fVar19 + (uint)(param_3 <= fVar19) * (int)param_3
                  );
    }
  }
  iVar12 = param_5 + 0x324;
  *(undefined1 *)(param_6 + 0x2d) = uVar9;
  param_6[0x2b] = auVar17._12_4_;
  param_6[0x2c] = auVar17._8_4_;
  uVar6 = FUN_00439e9c(iVar12);
  uVar6 = FUN_00439efc(auVar15._8_4_,uVar6);
  uVar10 = FUN_00439f24(iVar12);
  fVar19 = (float)FUN_00439f88(uVar6,uVar10);
  local_4c = *(float *)(param_5 + 0x324) == fVar19;
  local_4b = *(float *)(param_5 + 0x328) == fVar19;
  local_4a = *(float *)(param_5 + 0x32c) == fVar19;
  iVar5 = FUN_00439fb4(&local_4c,aiStack_3c);
  if (iVar5 == 0) {
    fVar19 = (float)FUN_0043a5dc(fVar19,iVar12,param_5 + 0x1578);
  }
  else {
    fVar19 = local_48[0];
    if (0 < iVar5) {
      piVar7 = aiStack_3c;
      pfVar11 = local_48;
      do {
        piVar8 = piVar7 + 1;
        *pfVar11 = *(float *)(param_5 + (*piVar7 + 0x55d) * 4);
        piVar7 = piVar8;
        pfVar11 = pfVar11 + 1;
        fVar19 = local_48[0];
      } while (piVar8 != aiStack_3c + iVar5);
    }
  }
  param_6[0x2e] = DAT_0043a54c;
  param_1 = param_1 + param_2 * fVar19;
  fVar20 = *(float *)(param_5 + 0x514);
  auVar15._8_4_ = *(float *)(param_5 + 0x330);
  if (fVar20 <= param_1) {
    if (auVar15._8_4_ < param_1) {
      bVar2 = param_1 < fVar20;
    }
    else {
      bVar2 = false;
    }
  }
  else if (auVar15._8_4_ < param_1) {
    bVar2 = param_1 < fVar20;
  }
  else {
    if (NAN(auVar15._8_4_) || NAN(param_1)) goto LAB_0043a456;
    bVar2 = false;
  }
  if (bVar2) {
    FUN_0043a5a0((param_1 - auVar15._8_4_) / (*(float *)(param_5 + 0x334) - auVar15._8_4_));
  }
LAB_0043a456:
  FUN_0043a0f4(param_1);
  VectorLoadRegister(local_60,2,4,0);
  VectorStoreRegister(param_6 + 0x2f,2,4,0);
  VectorStoreRegister(param_6 + 0x33,2,4,0);
  param_6[0x37] = fVar19;
  *param_7 = param_1;
  return;
}

