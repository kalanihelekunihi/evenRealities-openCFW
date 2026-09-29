
void FUN_0053e728(int param_1,int param_2)

{
  char cVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  uint uVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  byte bVar8;
  int iVar9;
  uint uVar10;
  uint in_fpscr;
  uint uVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  undefined4 local_c8;
  undefined4 local_c4;
  undefined4 local_c0;
  int local_bc;
  int local_b8;
  int local_b4;
  int local_b0;
  float local_ac [2];
  undefined1 auStack_a4 [36];
  float local_80 [8];
  undefined1 auStack_60 [16];
  
  uVar11 = in_fpscr & 0xfffffff;
  if (*(float *)(param_2 + 0x24) <= *(float *)(param_2 + 0x1c)) {
    fVar12 = *(float *)(param_2 + 0x24);
  }
  else {
    fVar12 = *(float *)(param_2 + 0x1c);
  }
  if (*(float *)(param_2 + 0x2c) <= fVar12) {
    local_bc = (int)*(float *)(param_2 + 0x2c);
  }
  else if (*(float *)(param_2 + 0x24) <= *(float *)(param_2 + 0x1c)) {
    local_bc = (int)*(float *)(param_2 + 0x24);
  }
  else {
    local_bc = (int)*(float *)(param_2 + 0x1c);
  }
  if (*(float *)(param_2 + 0x28) <= *(float *)(param_2 + 0x20)) {
    fVar12 = *(float *)(param_2 + 0x28);
  }
  else {
    fVar12 = *(float *)(param_2 + 0x20);
  }
  if (*(float *)(param_2 + 0x30) <= fVar12) {
    local_b8 = (int)*(float *)(param_2 + 0x30);
  }
  else if (*(float *)(param_2 + 0x28) <= *(float *)(param_2 + 0x20)) {
    local_b8 = (int)*(float *)(param_2 + 0x28);
  }
  else {
    local_b8 = (int)*(float *)(param_2 + 0x20);
  }
  if (*(float *)(param_2 + 0x1c) <= *(float *)(param_2 + 0x24)) {
    fVar12 = *(float *)(param_2 + 0x24);
  }
  else {
    fVar12 = *(float *)(param_2 + 0x1c);
  }
  if (fVar12 <= *(float *)(param_2 + 0x2c)) {
    local_b4 = (int)*(float *)(param_2 + 0x2c);
  }
  else if (*(float *)(param_2 + 0x1c) <= *(float *)(param_2 + 0x24)) {
    local_b4 = (int)*(float *)(param_2 + 0x24);
  }
  else {
    local_b4 = (int)*(float *)(param_2 + 0x1c);
  }
  if (*(float *)(param_2 + 0x20) <= *(float *)(param_2 + 0x28)) {
    fVar12 = *(float *)(param_2 + 0x28);
  }
  else {
    fVar12 = *(float *)(param_2 + 0x20);
  }
  if (fVar12 <= *(float *)(param_2 + 0x30)) {
    local_b0 = (int)*(float *)(param_2 + 0x30);
  }
  else if (*(float *)(param_2 + 0x20) <= *(float *)(param_2 + 0x28)) {
    local_b0 = (int)*(float *)(param_2 + 0x28);
  }
  else {
    local_b0 = (int)*(float *)(param_2 + 0x20);
  }
  cVar1 = FUN_00450bcc(auStack_60,&local_bc,param_1 + 0x38);
  if ((cVar1 != '\0') && (2 < *(byte *)(param_2 + 0x37))) {
    iVar7 = *(int *)(param_1 + 0x4c);
    iVar9 = *(int *)(param_1 + 0x48);
    bVar8 = *(byte *)(param_2 + 0x43) & 0xf;
    FUN_00439be4(&local_c8,param_2 + 0x34,3);
    uVar2 = FUN_004b06a8(local_c8,*(undefined1 *)(param_2 + 0x37));
    fVar12 = (float)VectorSignedToFloat(*(undefined4 *)(iVar9 + 4),(byte)(uVar11 >> 0x16) & 3);
    fVar12 = *(float *)(param_2 + 0x1c) - fVar12;
    fVar13 = (float)VectorSignedToFloat(*(undefined4 *)(iVar9 + 8),(byte)(uVar11 >> 0x16) & 3);
    fVar13 = *(float *)(param_2 + 0x20) - fVar13;
    fVar14 = (float)VectorSignedToFloat(*(undefined4 *)(iVar9 + 4),(byte)(uVar11 >> 0x16) & 3);
    fVar14 = *(float *)(param_2 + 0x24) - fVar14;
    fVar15 = (float)VectorSignedToFloat(*(undefined4 *)(iVar9 + 8),(byte)(uVar11 >> 0x16) & 3);
    fVar15 = *(float *)(param_2 + 0x28) - fVar15;
    fVar16 = (float)VectorSignedToFloat(*(undefined4 *)(iVar9 + 4),(byte)(uVar11 >> 0x16) & 3);
    fVar16 = *(float *)(param_2 + 0x2c) - fVar16;
    fVar17 = (float)VectorSignedToFloat(*(undefined4 *)(iVar9 + 8),(byte)(uVar11 >> 0x16) & 3);
    fVar17 = *(float *)(param_2 + 0x30) - fVar17;
    uVar3 = FUN_0052266e(1,1,1,0);
    uVar5 = DAT_0053ebac;
    if (*(char *)(iVar9 + 0x14) != '\x10') {
      uVar5 = 0x504;
    }
    if (bVar8 == 0) {
      FUN_004b0730(iVar7,uVar5);
      FUN_00522a16(uVar2);
      FUN_00522a24(fVar12,fVar13,fVar14,fVar15,fVar16,fVar17);
    }
    else {
      uVar10 = (uint)*(byte *)(param_2 + 0x42);
      if (2 < uVar10) {
        local_c8 = DAT_0053ebb0;
        FUN_0044d25c(2,DAT_0053ebb8,0x5e,DAT_0053ebb4);
        uVar10 = 2;
      }
      for (uVar4 = 0; uVar4 < uVar10; uVar4 = uVar4 + 1) {
        fVar19 = (float)VectorUnsignedToFloat
                                  ((uint)*(byte *)(uVar4 * 5 + param_2 + 0x3c),
                                   (byte)(uVar11 >> 0x16) & 3);
        local_ac[uVar4] = fVar19 / DAT_0053eba0;
        fVar19 = (float)VectorUnsignedToFloat
                                  ((uint)*(byte *)(uVar4 * 5 + param_2 + 0x3a),
                                   (byte)(uVar11 >> 0x16) & 3);
        local_80[uVar4 * 4] = fVar19;
        fVar19 = (float)VectorUnsignedToFloat
                                  ((uint)*(byte *)(uVar4 * 5 + param_2 + 0x39),
                                   (byte)(uVar11 >> 0x16) & 3);
        local_80[uVar4 * 4 + 1] = fVar19;
        fVar19 = (float)VectorUnsignedToFloat
                                  ((uint)*(byte *)(uVar4 * 5 + param_2 + 0x38),
                                   (byte)(uVar11 >> 0x16) & 3);
        local_80[uVar4 * 4 + 2] = fVar19;
        fVar19 = (float)VectorUnsignedToFloat
                                  ((uint)*(byte *)(uVar4 * 5 + param_2 + 0x3b),
                                   (byte)(uVar11 >> 0x16) & 3);
        fVar20 = (float)VectorUnsignedToFloat
                                  ((uint)*(byte *)(param_2 + 0x37),(byte)(uVar11 >> 0x16) & 3);
        local_80[uVar4 * 4 + 3] = (fVar19 * fVar20) / DAT_0053eba0;
      }
      local_c0 = 1;
      local_c4 = 0;
      local_c8 = 1;
      FUN_004b1298(1,*(undefined4 *)(*(int *)(iVar7 + 0x3c) + 0x10),
                   *(uint *)(*(int *)(iVar7 + 0x3c) + 4) & 0xffff,1);
      FUN_005fa238(uVar10,local_ac,local_80,1);
      local_c4 = 1;
      local_c8 = 0xffffffff;
      FUN_004b06c0(iVar7,uVar5,0,1);
      iVar6 = local_bc - *(int *)(iVar9 + 4);
      iVar9 = local_b8 - *(int *)(iVar9 + 8);
      uVar5 = FUN_00451598(&local_bc);
      uVar2 = FUN_004515a4(&local_bc);
      uVar10 = *(uint *)(*(int *)(iVar7 + 0x3c) + 4) & 0xffff;
      if (bVar8 == 2) {
        fVar19 = (float)VectorUnsignedToFloat(uVar5,(byte)(uVar11 >> 0x16) & 3);
        fVar20 = (float)VectorUnsignedToFloat(uVar10,(byte)(uVar11 >> 0x16) & 3);
        fVar19 = fVar19 / fVar20;
        fVar20 = (float)VectorUnsignedToFloat(uVar2,(byte)(uVar11 >> 0x16) & 3);
        uVar5 = DAT_0053eba4;
      }
      else {
        fVar19 = (float)VectorUnsignedToFloat(uVar5,(byte)(uVar11 >> 0x16) & 3);
        fVar20 = (float)VectorUnsignedToFloat(uVar2,(byte)(uVar11 >> 0x16) & 3);
        fVar18 = (float)VectorUnsignedToFloat(uVar10,(byte)(uVar11 >> 0x16) & 3);
        fVar20 = fVar20 / fVar18;
        uVar5 = DAT_0053eba8;
      }
      FUN_00561810(auStack_a4);
      FUN_00561964(uVar5,auStack_a4);
      FUN_005618b8(fVar19,fVar20,auStack_a4);
      uVar2 = VectorSignedToFloat(iVar9,(byte)(uVar11 >> 0x16) & 3);
      uVar5 = VectorSignedToFloat(iVar6,(byte)(uVar11 >> 0x16) & 3);
      FUN_00561856(uVar5,uVar2,auStack_a4);
      FUN_00561b38(auStack_a4);
      FUN_00522848(auStack_a4);
      FUN_00522a24(fVar12,fVar13,fVar14,fVar15,fVar16,fVar17);
      FUN_005226b2(uVar3);
    }
  }
  return;
}

