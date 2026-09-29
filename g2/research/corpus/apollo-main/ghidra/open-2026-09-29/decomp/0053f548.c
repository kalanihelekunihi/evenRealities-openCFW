
void FUN_0053f548(float param_1,int param_2,int *param_3)

{
  byte bVar1;
  byte bVar2;
  bool bVar3;
  bool bVar4;
  bool bVar5;
  bool bVar6;
  char cVar7;
  uint uVar8;
  undefined4 uVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  uint uVar13;
  undefined4 uVar14;
  int iVar15;
  uint in_fpscr;
  float fVar16;
  float fVar17;
  undefined4 uVar18;
  float local_148;
  float local_144;
  int local_140;
  int local_13c;
  int local_138;
  int local_134;
  float local_130;
  float local_12c;
  float local_128;
  float local_124;
  float local_120;
  float local_11c;
  undefined4 local_118;
  undefined1 auStack_114 [36];
  undefined1 auStack_f0 [36];
  undefined1 auStack_cc [16];
  undefined1 auStack_bc [44];
  int local_90;
  undefined1 auStack_70 [44];
  undefined4 local_44;
  
  bVar5 = false;
  if ((*(ushort *)(param_2 + 0x50) & 0x1fff) >> 0xc != 0) {
    uVar8 = *(uint *)(param_2 + 0x24) & 0xffff;
    uVar12 = *(uint *)(param_2 + 0x24) >> 0x10;
    if ((uVar8 == 0) || ((uVar8 & uVar8 - 1) != 0)) {
      bVar2 = 0;
    }
    else {
      bVar2 = 1;
    }
    if ((uVar12 == 0) || ((uVar12 & uVar12 - 1) != 0)) {
      bVar1 = 0;
    }
    else {
      bVar1 = 1;
    }
    if (!(bool)(bVar2 & bVar1)) {
      bVar5 = true;
    }
  }
  if ((-1 < (int)((uint)*(ushort *)(param_2 + 0x50) << 0x13)) || (bVar5)) {
    uVar14 = 8;
  }
  else {
    uVar14 = 4;
  }
  if ((((*(int *)(param_2 + 0x30) == 0) && (*(int *)(param_2 + 0x34) == 0x100)) &&
      (*(int *)(param_2 + 0x38) == 0x100)) &&
     ((*(int *)(param_2 + 0x40) == 0 && (*(int *)(param_2 + 0x3c) == 0)))) {
    bVar3 = false;
  }
  else {
    bVar3 = true;
  }
  FUN_00439be4(&local_118,param_2 + 0x4c,3);
  local_144 = (float)FUN_004b06a8(local_118,*(undefined1 *)(param_2 + 0x4f));
  cVar7 = FUN_004b0f50(*(undefined4 *)(param_2 + 0x1c),bVar3,auStack_70,0);
  if (cVar7 == '\x01') {
    FUN_00439be4(&local_118,param_2 + 0x4c,3);
    uVar9 = FUN_004b06a8(local_118,*(undefined1 *)(param_2 + 0x50));
    uVar8 = FUN_004b0d38(local_44,uVar9,uVar14);
    bVar6 = false;
    iVar15 = 0;
    if (*(int *)(param_2 + 0x68) != 0) {
      cVar7 = FUN_004b0f50(*(undefined4 *)(param_2 + 0x68),0,auStack_bc,1);
      if (cVar7 == '\x01') {
        if (((*(uint *)(local_90 + 4) & 0xffff) != (*(uint *)(param_2 + 0x24) & 0xffff)) ||
           (*(uint *)(local_90 + 4) >> 0x10 != *(uint *)(param_2 + 0x24) >> 0x10)) {
          local_148 = DAT_0053fa8c;
          FUN_0044d25c(2,DAT_0053fa6c,0xb7,DAT_0053fa84);
          local_90 = iVar15;
        }
        bVar6 = true;
        iVar15 = local_90;
      }
      else {
        local_148 = DAT_0053fa88;
        FUN_0044d25c(2,DAT_0053fa6c,0xac,DAT_0053fa84);
      }
    }
    uVar12 = 0;
    if (iVar15 != 0) {
      uVar12 = FUN_004b0ea6(iVar15,1);
    }
    iVar15 = *(int *)((int)param_1 + 0x48);
    if ((*(byte *)(param_2 + 0x51) & 7) == 1) {
      uVar13 = 0x101;
    }
    else {
      uVar13 = DAT_0053fa90;
      if (*(char *)(iVar15 + 0x14) != '\x10') {
        uVar13 = 0x504;
      }
    }
    uVar12 = uVar12 | uVar8 | uVar13;
    bVar4 = false;
    if (((((*(uint *)(param_2 + 0x20) & 0xffff) >> 8 == 0xb) ||
         ((*(uint *)(param_2 + 0x20) & 0xffff) >> 8 == 0xc)) ||
        ((*(uint *)(param_2 + 0x20) & 0xffff) >> 8 == 0xd)) ||
       ((*(uint *)(param_2 + 0x20) & 0xffff) >> 8 == 0xe)) {
      bVar4 = true;
    }
    local_148 = param_1;
    if ((2 < *(byte *)(param_2 + 0x4f)) && (!bVar4)) {
      uVar12 = uVar12 | 0x100000;
      FUN_00513e4c(local_144);
    }
    if ((*(ushort *)(param_2 + 0x50) & 0xfff) >> 0xb == 0) {
      uVar14 = FUN_0052266e(0,0,0,0);
    }
    else {
      uVar14 = FUN_0052266e(1,1,1,1);
    }
    FUN_004b0748(*(undefined4 *)((int)local_148 + 0x4c),uVar12);
    if (bVar3) {
      FUN_00561810(auStack_114);
      uVar18 = VectorSignedToFloat(-*(int *)(param_2 + 0x48),(byte)(in_fpscr >> 0x16) & 3);
      uVar9 = VectorSignedToFloat(-*(int *)(param_2 + 0x44),(byte)(in_fpscr >> 0x16) & 3);
      FUN_00561856(uVar9,uVar18,auStack_114);
      fVar16 = (float)VectorSignedToFloat(*(undefined4 *)(param_2 + 0x38),
                                          (byte)(in_fpscr >> 0x16) & 3);
      fVar17 = (float)VectorSignedToFloat(*(undefined4 *)(param_2 + 0x34),
                                          (byte)(in_fpscr >> 0x16) & 3);
      FUN_005618b8(fVar17 / DAT_0053fa60,fVar16 / DAT_0053fa60,auStack_114);
      fVar16 = (float)VectorSignedToFloat(*(undefined4 *)(param_2 + 0x30),
                                          (byte)(in_fpscr >> 0x16) & 3);
      FUN_00561964(fVar16 / 10.0,auStack_114);
      fVar16 = (float)VectorSignedToFloat(*(undefined4 *)(param_2 + 0x40),
                                          (byte)(in_fpscr >> 0x16) & 3);
      fVar17 = (float)VectorSignedToFloat(*(undefined4 *)(param_2 + 0x3c),
                                          (byte)(in_fpscr >> 0x16) & 3);
      FUN_00561902(fVar17 / 10.0,fVar16 / 10.0,auStack_114);
      uVar18 = VectorSignedToFloat(*(undefined4 *)(param_2 + 0x48),(byte)(in_fpscr >> 0x16) & 3);
      uVar9 = VectorSignedToFloat(*(undefined4 *)(param_2 + 0x44),(byte)(in_fpscr >> 0x16) & 3);
      FUN_00561856(uVar9,uVar18,auStack_114);
      uVar18 = VectorSignedToFloat(param_3[1] - *(int *)(iVar15 + 8),(byte)(in_fpscr >> 0x16) & 3);
      uVar9 = VectorSignedToFloat(*param_3 - *(int *)(iVar15 + 4),(byte)(in_fpscr >> 0x16) & 3);
      FUN_00561856(uVar9,uVar18,auStack_114);
      FUN_00561830(auStack_f0,auStack_114);
      FUN_00561b38(auStack_114);
      FUN_005226e8(auStack_114);
      local_144 = 0.0;
      local_148 = 0.0;
      uVar9 = FUN_00451598(param_3);
      fVar16 = (float)VectorSignedToFloat(uVar9,(byte)(in_fpscr >> 0x16) & 3);
      local_11c = fVar16 + local_144 + -1.0;
      local_120 = local_148;
      uVar9 = FUN_00451598(param_3);
      fVar16 = (float)VectorSignedToFloat(uVar9,(byte)(in_fpscr >> 0x16) & 3);
      local_124 = fVar16 + local_144 + -1.0;
      uVar9 = FUN_004515a4(param_3);
      fVar16 = (float)VectorSignedToFloat(uVar9,(byte)(in_fpscr >> 0x16) & 3);
      local_128 = fVar16 + local_148 + -1.0;
      local_12c = local_144;
      uVar9 = FUN_004515a4(param_3);
      fVar16 = (float)VectorSignedToFloat(uVar9,(byte)(in_fpscr >> 0x16) & 3);
      local_130 = fVar16 + local_148 + -1.0;
      FUN_00561ad4(auStack_f0,&local_144,&local_148);
      FUN_00561ad4(auStack_f0,&local_11c,&local_120);
      FUN_00561ad4(auStack_f0,&local_124,&local_128);
      FUN_00561ad4(auStack_f0,&local_12c,&local_130);
      FUN_00522db4(local_144,local_148,local_11c,local_120,local_124,local_128,local_12c,local_130);
    }
    else if (bVar5) {
      uVar8 = *(uint *)(param_2 + 0x24) & 0xffff;
      uVar12 = *(uint *)(param_2 + 0x24) & 0xffff;
      iVar10 = FUN_00451598(param_2 + 0x58);
      if (iVar10 < 0) {
        FUN_00439c04(&local_140,param_3,0x10);
      }
      else {
        FUN_00439c04(&local_140,param_2 + 0x58,0x10);
      }
      FUN_00450b6c(&local_140,uVar8);
      FUN_00450b76(&local_140,uVar12);
      iVar10 = local_140;
      for (; local_140 = iVar10, local_13c <= param_3[3]; local_13c = uVar12 + local_13c) {
        for (; local_140 <= param_3[2]; local_140 = uVar8 + local_140) {
          iVar11 = FUN_00450bcc(auStack_cc,&local_140,param_3);
          if (iVar11 != 0) {
            FUN_004b1b48(local_140 - *(int *)(iVar15 + 4),local_13c - *(int *)(iVar15 + 8));
          }
          local_138 = uVar8 + local_138;
        }
        local_134 = uVar12 + local_134;
        local_138 = uVar8 + iVar10 + -1;
      }
    }
    else {
      FUN_004b1b48(*param_3 - *(int *)(iVar15 + 4),param_3[1] - *(int *)(iVar15 + 8));
    }
    if ((*(ushort *)(param_2 + 0x50) & 0xfff) >> 0xb != 0) {
      FUN_005226b2(uVar14);
    }
    uVar14 = FUN_005144fa();
    FUN_00514cf2(uVar14);
    FUN_00514d00(uVar14);
    FUN_00514384(uVar14);
    FUN_0048908c(auStack_70);
    if (bVar6) {
      FUN_0048908c(auStack_bc);
    }
  }
  else {
    local_148 = DAT_0053fa80;
    FUN_0044d25c(3,DAT_0053fa6c,0x9b,DAT_0053fa84);
  }
  return;
}

