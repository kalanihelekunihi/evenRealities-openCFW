
void FUN_0053ecfc(int param_1,int param_2)

{
  bool bVar1;
  float fVar2;
  char cVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  uint in_fpscr;
  uint uVar8;
  uint uVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  undefined4 local_80;
  undefined4 local_7c;
  undefined4 local_78;
  int local_74;
  int local_70;
  int local_6c;
  int local_68;
  undefined1 auStack_64 [36];
  
  if (((*(int *)(param_2 + 0x30) != 0) && (2 < *(byte *)(param_2 + 0x3c))) &&
     ((uVar8 = in_fpscr & 0xfffffff, *(float *)(param_2 + 0x1c) != *(float *)(param_2 + 0x24) ||
      (*(float *)(param_2 + 0x20) != *(float *)(param_2 + 0x28))))) {
    if (*(float *)(param_2 + 0x24) <= *(float *)(param_2 + 0x1c)) {
      fVar10 = *(float *)(param_2 + 0x24);
    }
    else {
      fVar10 = *(float *)(param_2 + 0x1c);
    }
    local_74 = (int)fVar10 - *(int *)(param_2 + 0x30) / 2;
    if (*(float *)(param_2 + 0x1c) <= *(float *)(param_2 + 0x24)) {
      fVar10 = *(float *)(param_2 + 0x24);
    }
    else {
      fVar10 = *(float *)(param_2 + 0x1c);
    }
    local_6c = *(int *)(param_2 + 0x30) / 2 + (int)fVar10;
    if (*(float *)(param_2 + 0x28) <= *(float *)(param_2 + 0x20)) {
      fVar10 = *(float *)(param_2 + 0x28);
    }
    else {
      fVar10 = *(float *)(param_2 + 0x20);
    }
    local_70 = (int)fVar10 - *(int *)(param_2 + 0x30) / 2;
    if (*(float *)(param_2 + 0x20) <= *(float *)(param_2 + 0x28)) {
      fVar10 = *(float *)(param_2 + 0x28);
    }
    else {
      fVar10 = *(float *)(param_2 + 0x20);
    }
    local_68 = *(int *)(param_2 + 0x30) / 2 + (int)fVar10;
    cVar3 = FUN_00450bcc(&local_74,&local_74,param_1 + 0x38);
    if (cVar3 != '\0') {
      iVar5 = *(int *)(param_1 + 0x4c);
      iVar7 = *(int *)(param_1 + 0x48);
      FUN_00439be4(&local_80,param_2 + 0x2c,3);
      uVar4 = FUN_004b06a8(local_80,*(undefined1 *)(param_2 + 0x3c));
      uVar6 = DAT_0053f098;
      if (*(char *)(iVar7 + 0x14) != '\x10') {
        uVar6 = 0x504;
      }
      fVar10 = (float)VectorSignedToFloat(*(undefined4 *)(iVar7 + 4),(byte)(uVar8 >> 0x16) & 3);
      fVar10 = *(float *)(param_2 + 0x1c) - fVar10;
      fVar11 = (float)VectorSignedToFloat(*(undefined4 *)(iVar7 + 8),(byte)(uVar8 >> 0x16) & 3);
      fVar11 = *(float *)(param_2 + 0x20) - fVar11;
      fVar12 = (float)VectorSignedToFloat(*(undefined4 *)(iVar7 + 4),(byte)(uVar8 >> 0x16) & 3);
      fVar12 = *(float *)(param_2 + 0x24) - fVar12;
      fVar13 = (float)VectorSignedToFloat(*(undefined4 *)(iVar7 + 8),(byte)(uVar8 >> 0x16) & 3);
      fVar13 = *(float *)(param_2 + 0x28) - fVar13;
      fVar17 = (float)VectorSignedToFloat(*(undefined4 *)(param_2 + 0x30),(byte)(uVar8 >> 0x16) & 3)
      ;
      uVar8 = uVar8 & 0xfffffff;
      uVar9 = uVar8 | (uint)(*(float *)(param_2 + 0x24) == *(float *)(param_2 + 0x1c)) << 0x1e;
      if ((byte)(uVar9 >> 0x1e) == 0) {
        fVar14 = (float)FUN_00524260((fVar13 - fVar11) / (fVar12 - fVar10));
        uVar8 = uVar9;
      }
      else {
        fVar14 = DAT_0053f088;
        if (*(float *)(param_2 + 0x20) < *(float *)(param_2 + 0x28)) {
          fVar14 = DAT_0053f084;
        }
      }
      if ((*(int *)(param_2 + 0x38) == 0) || (*(int *)(param_2 + 0x34) == 0)) {
        bVar1 = false;
      }
      else {
        bVar1 = true;
      }
      if (bVar1) {
        local_78 = 5;
        local_7c = 0;
        local_80 = 1;
        FUN_004b1298(1,*(undefined4 *)(*(int *)(iVar5 + 0x3c) + 0x10),
                     *(uint *)(*(int *)(iVar5 + 0x3c) + 4) & 0xffff,1);
        FUN_005fa7c0(*(undefined4 *)(param_2 + 0x34),*(undefined4 *)(param_2 + 0x38),uVar4,1);
        local_7c = 1;
        local_80 = 0xffffffff;
        FUN_004b06c0(iVar5,uVar6,0,1);
        uVar8 = uVar8 & 0xfffffff |
                (uint)(*(float *)(param_2 + 0x24) < *(float *)(param_2 + 0x1c)) << 0x1f;
        fVar2 = fVar14;
        if (SUB41(uVar8 >> 0x1f,0) !=
            (NAN(*(float *)(param_2 + 0x24)) || NAN(*(float *)(param_2 + 0x1c)))) {
          fVar2 = fVar14 + DAT_0053f08c;
        }
        fVar15 = (float)VectorSignedToFloat(*(int *)(param_2 + 0x34) + *(int *)(param_2 + 0x38),
                                            (byte)(uVar8 >> 0x16) & 3);
        fVar16 = (float)VectorUnsignedToFloat
                                  (*(uint *)(*(int *)(iVar5 + 0x3c) + 4) & 0xffff,
                                   (byte)(uVar8 >> 0x16) & 3);
        FUN_00561810(auStack_64);
        FUN_005618b8(fVar15 / fVar16,fVar17,auStack_64);
        FUN_00561856(DAT_0053f090,fVar17 * -0.5,auStack_64);
        FUN_00561964(fVar2,auStack_64);
        FUN_00561856(fVar10,fVar11,auStack_64);
        FUN_00561b38(auStack_64);
        FUN_00522848(auStack_64);
      }
      else {
        FUN_004b0730(iVar5,uVar6);
        FUN_00522a16(uVar4);
      }
      FUN_0053ebbc(fVar10,fVar11,fVar12,fVar13,fVar17);
      if (((int)((uint)*(byte *)(param_2 + 0x3d) << 0x1f) < 0) && (1 < *(int *)(param_2 + 0x30))) {
        FUN_0052330c(fVar10,fVar11,fVar17 * 0.25,fVar17 * 0.5,fVar14 + DAT_0053f084,
                     fVar14 + DAT_0053f094);
      }
      if (((*(byte *)(param_2 + 0x3d) & 3) >> 1 != 0) && (1 < *(int *)(param_2 + 0x30))) {
        FUN_0052330c(fVar12,fVar13,fVar17 * 0.25,fVar17 * 0.5,fVar14 + DAT_0053f088,
                     fVar14 + DAT_0053f084);
      }
    }
  }
  return;
}

