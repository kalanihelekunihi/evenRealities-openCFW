
undefined4 FUN_0053dc38(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  byte bVar9;
  uint uVar10;
  uint in_fpscr;
  float fVar11;
  float fVar12;
  float fVar13;
  undefined4 uVar14;
  ulonglong uVar15;
  int local_a0 [4];
  undefined4 local_90;
  float local_84 [2];
  undefined1 auStack_7c [36];
  float local_58 [8];
  
  if (2 < *(byte *)(param_2 + 0x20)) {
    iVar7 = *(int *)(param_1 + 0x4c);
    iVar8 = *(int *)(param_1 + 0x48);
    bVar9 = *(byte *)(param_2 + 0x2f) & 0xf;
    FUN_00439be4(local_a0,param_2 + 0x21,3);
    uVar1 = FUN_004b06a8(local_a0[0],*(undefined1 *)(param_2 + 0x20));
    FUN_0053dc24(local_a0 + 3,param_3);
    FUN_00450bb2(local_a0 + 3,-*(int *)(iVar8 + 4),-*(int *)(iVar8 + 8));
    iVar2 = FUN_00451598(local_a0 + 3);
    iVar3 = FUN_004515a4(local_a0 + 3);
    iVar6 = iVar3;
    if (iVar2 < iVar3) {
      iVar6 = iVar2;
    }
    iVar6 = iVar6 >> 1;
    if (*(int *)(param_2 + 0x1c) < iVar6) {
      iVar6 = *(int *)(param_2 + 0x1c);
    }
    uVar14 = DAT_0053def0;
    if (*(char *)(iVar8 + 0x14) != '\x10') {
      uVar14 = 0x504;
    }
    if (bVar9 == 0) {
      FUN_004b0730(iVar7,uVar14);
      FUN_00522a16(uVar1);
      if (iVar6 == 0) {
        FUN_00522ae0(local_a0[3],local_90,iVar2,iVar3);
      }
      else {
        local_a0[0] = iVar6;
        FUN_00522b30(local_a0[3],local_90,iVar2,iVar3);
      }
    }
    else {
      uVar10 = (uint)*(byte *)(param_2 + 0x2e);
      if (2 < uVar10) {
        local_a0[0] = DAT_0053def4;
        FUN_0044d25c(2,DAT_0053defc,0x57,DAT_0053def8);
        uVar10 = 2;
      }
      for (uVar4 = 0; uVar4 < uVar10; uVar4 = uVar4 + 1) {
        fVar11 = (float)VectorUnsignedToFloat
                                  ((uint)*(byte *)(uVar4 * 5 + param_2 + 0x28),
                                   (byte)(in_fpscr >> 0x16) & 3);
        local_84[uVar4] = fVar11 / DAT_0053dee4;
        fVar11 = (float)VectorUnsignedToFloat
                                  ((uint)*(byte *)(uVar4 * 5 + param_2 + 0x26),
                                   (byte)(in_fpscr >> 0x16) & 3);
        local_58[uVar4 * 4] = fVar11;
        fVar11 = (float)VectorUnsignedToFloat
                                  ((uint)*(byte *)(uVar4 * 5 + param_2 + 0x25),
                                   (byte)(in_fpscr >> 0x16) & 3);
        local_58[uVar4 * 4 + 1] = fVar11;
        fVar11 = (float)VectorUnsignedToFloat
                                  ((uint)*(byte *)(uVar4 * 5 + param_2 + 0x24),
                                   (byte)(in_fpscr >> 0x16) & 3);
        local_58[uVar4 * 4 + 2] = fVar11;
        fVar11 = (float)VectorUnsignedToFloat
                                  ((uint)*(byte *)(uVar4 * 5 + param_2 + 0x27),
                                   (byte)(in_fpscr >> 0x16) & 3);
        fVar12 = (float)VectorUnsignedToFloat
                                  ((uint)*(byte *)(param_2 + 0x20),(byte)(in_fpscr >> 0x16) & 3);
        local_58[uVar4 * 4 + 3] = (fVar11 * fVar12) / DAT_0053dee4;
      }
      uVar5 = *(undefined4 *)(*(int *)(iVar7 + 0x3c) + 4);
      local_a0[2] = 1;
      local_a0[1] = 0;
      local_a0[0] = 1;
      FUN_004b1298(1,*(undefined4 *)(*(int *)(iVar7 + 0x3c) + 0x10),
                   *(uint *)(*(int *)(iVar7 + 0x3c) + 4) & 0xffff,1);
      FUN_005fa238(uVar10,local_84,local_58,1);
      local_a0[1] = 1;
      local_a0[0] = -1;
      FUN_004b06c0(iVar7,uVar14,0,1);
      uVar1 = DAT_0053deec;
      if (bVar9 == 2) {
        uVar1 = DAT_0053dee8;
      }
      uVar15 = CONCAT44(uVar1,uVar5) & 0xffffffff0000ffff;
      uVar1 = (undefined4)uVar15;
      if (bVar9 == 2) {
        fVar11 = (float)VectorSignedToFloat(iVar2,(byte)(in_fpscr >> 0x16) & 3);
        fVar12 = (float)VectorUnsignedToFloat(uVar1,(byte)(in_fpscr >> 0x16) & 3);
        fVar11 = fVar11 / fVar12;
        fVar12 = (float)VectorSignedToFloat(iVar3,(byte)(in_fpscr >> 0x16) & 3);
      }
      else {
        fVar11 = (float)VectorSignedToFloat(iVar2,(byte)(in_fpscr >> 0x16) & 3);
        fVar12 = (float)VectorSignedToFloat(iVar3,(byte)(in_fpscr >> 0x16) & 3);
        fVar13 = (float)VectorUnsignedToFloat(uVar1,(byte)(in_fpscr >> 0x16) & 3);
        fVar12 = fVar12 / fVar13;
      }
      FUN_00561810(auStack_7c);
      FUN_00561964((int)(uVar15 >> 0x20),auStack_7c);
      FUN_005618b8(fVar11,fVar12,auStack_7c);
      uVar14 = VectorSignedToFloat(local_90,(byte)(in_fpscr >> 0x16) & 3);
      uVar1 = VectorSignedToFloat(local_a0[3],(byte)(in_fpscr >> 0x16) & 3);
      FUN_00561856(uVar1,uVar14,auStack_7c);
      FUN_00561b38(auStack_7c);
      FUN_00522848(auStack_7c);
      if (iVar6 == 0) {
        FUN_00522ae0(local_a0[3],local_90,iVar2,iVar3);
      }
      else {
        local_a0[0] = iVar6;
        FUN_00522b30(local_a0[3],local_90,iVar2,iVar3);
      }
    }
  }
  return param_4;
}

