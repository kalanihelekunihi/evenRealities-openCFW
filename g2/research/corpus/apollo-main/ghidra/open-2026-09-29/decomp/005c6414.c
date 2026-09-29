
int FUN_005c6414(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int *piVar8;
  undefined4 uVar9;
  uint uVar10;
  int iVar11;
  int iVar12;
  uint in_fpscr;
  float fVar13;
  float fVar14;
  int local_134;
  undefined1 auStack_12c [8];
  int local_124;
  int local_120;
  int local_11c;
  float local_110;
  float local_10c;
  float local_108;
  float local_104;
  undefined1 auStack_100 [4];
  int local_fc;
  byte local_ef;
  int local_ec;
  int local_e8;
  int local_e4;
  int local_e0;
  int local_dc;
  int local_d8;
  int local_d4;
  int local_d0;
  undefined1 auStack_cc [16];
  undefined1 auStack_bc [16];
  undefined1 auStack_ac [8];
  int local_a4;
  uint local_a0;
  int local_9c;
  undefined1 auStack_8b [83];
  
  iVar1 = FUN_00450bcc(auStack_bc,param_1 + 0x14,param_2 + 0x18);
  if (iVar1 != 0) {
    FUN_00439c04(auStack_cc,param_2 + 0x18,0x10);
    FUN_00439c04(param_2 + 0x18,auStack_bc,0x10);
    iVar1 = FUN_005c579c(param_1,0);
    iVar2 = FUN_005c5772(param_1,0);
    iVar3 = FUN_005c575e(param_1,0);
    uVar4 = FUN_0043fe16(param_1);
    uVar5 = FUN_0043fe70(param_1);
    iVar6 = FUN_0044e586(param_1);
    iVar6 = (iVar1 + iVar2 + *(int *)(param_1 + 0x14)) - iVar6;
    iVar2 = FUN_0044e4aa(param_1);
    iVar2 = (iVar1 + iVar3 + *(int *)(param_1 + 0x18)) - iVar2;
    FUN_005c6fbc(auStack_12c);
    local_11c = param_2;
    FUN_00452b0e(param_1,0x50000,auStack_12c);
    FUN_00451b9c(auStack_ac);
    local_9c = param_2;
    FUN_00452616(param_1,0x20000,auStack_ac);
    iVar3 = FUN_005c574a(param_1,0x20000);
    iVar3 = iVar3 / 2;
    iVar7 = FUN_005c5754(param_1,0x20000);
    iVar7 = iVar7 / 2;
    iVar1 = iVar7;
    if (iVar3 < iVar7) {
      iVar1 = iVar3;
    }
    if (local_fc / 2 < iVar1) {
      local_ef = local_ef | 4;
    }
    if (local_fc == 1) {
      local_ef = local_ef | 4;
    }
    for (piVar8 = (int *)FUN_00482ce4(param_1 + 0x2c); piVar8 != (int *)0x0;
        piVar8 = (int *)FUN_00482cfa(param_1 + 0x2c,piVar8)) {
      if (-1 < (int)((uint)*(byte *)(piVar8 + 4) << 0x1f)) {
        FUN_00439be4(auStack_100,piVar8 + 2,3);
        FUN_00439be4(auStack_8b,piVar8 + 2,3);
        if ((*(byte *)(param_1 + 0x74) & 0x1f) >> 3 == 0) {
          local_134 = piVar8[3];
        }
        else {
          local_134 = 0;
        }
        local_110 = (float)VectorSignedToFloat(iVar6,(byte)(in_fpscr >> 0x16) & 3);
        local_108 = (float)VectorSignedToFloat(iVar6,(byte)(in_fpscr >> 0x16) & 3);
        if (*(int *)(piVar8[1] + local_134 * 4) == 10) {
          local_108 = DAT_005c6814;
          local_104 = DAT_005c6814;
        }
        else {
          uVar9 = FUN_004888b4(*(undefined4 *)(*piVar8 + local_134 * 4),
                               *(undefined4 *)(param_1 + ((piVar8[4] << 0x1c) >> 0x1f) * -4 + 0x54),
                               *(undefined4 *)(param_1 + ((piVar8[4] << 0x1c) >> 0x1f) * -4 + 0x5c),
                               0,uVar4);
          fVar13 = (float)VectorSignedToFloat(uVar9,(byte)(in_fpscr >> 0x16) & 3);
          local_108 = (float)VectorSignedToFloat(iVar6,(byte)(in_fpscr >> 0x16) & 3);
          local_108 = local_108 + fVar13;
          uVar9 = FUN_004888b4(*(undefined4 *)(piVar8[1] + local_134 * 4),
                               *(undefined4 *)(param_1 + ((piVar8[4] << 0x1b) >> 0x1f) * -4 + 0x44),
                               *(undefined4 *)(param_1 + ((piVar8[4] << 0x1b) >> 0x1f) * -4 + 0x4c),
                               0,uVar5);
          fVar13 = (float)VectorSignedToFloat(uVar9,(byte)(in_fpscr >> 0x16) & 3);
          fVar14 = (float)VectorSignedToFloat(uVar5,(byte)(in_fpscr >> 0x16) & 3);
          local_104 = (float)VectorSignedToFloat(iVar2,(byte)(in_fpscr >> 0x16) & 3);
          local_104 = local_104 + (fVar14 - fVar13);
        }
        iVar1 = local_134;
        for (uVar10 = 0; uVar10 < *(uint *)(param_1 + 0x70); uVar10 = uVar10 + 1) {
          local_110 = local_108;
          local_10c = local_104;
          iVar12 = (uVar10 + local_134) -
                   *(uint *)(param_1 + 0x70) * ((uVar10 + local_134) / *(uint *)(param_1 + 0x70));
          iVar11 = iVar12;
          if (*(int *)(piVar8[1] + iVar12 * 4) != 0x7fffffff) {
            uVar9 = FUN_004888b4(*(undefined4 *)(piVar8[1] + iVar12 * 4),
                                 *(undefined4 *)
                                  (param_1 + ((piVar8[4] << 0x1b) >> 0x1f) * -4 + 0x44),
                                 *(undefined4 *)
                                  (param_1 + ((piVar8[4] << 0x1b) >> 0x1f) * -4 + 0x4c),0,uVar5);
            fVar13 = (float)VectorSignedToFloat(uVar9,(byte)(in_fpscr >> 0x16) & 3);
            fVar14 = (float)VectorSignedToFloat(uVar5,(byte)(in_fpscr >> 0x16) & 3);
            local_104 = (float)VectorSignedToFloat(iVar2,(byte)(in_fpscr >> 0x16) & 3);
            local_104 = local_104 + (fVar14 - fVar13);
            uVar9 = FUN_004888b4(*(undefined4 *)(*piVar8 + iVar12 * 4),
                                 *(undefined4 *)
                                  (param_1 + ((piVar8[4] << 0x1c) >> 0x1f) * -4 + 0x54),
                                 *(undefined4 *)
                                  (param_1 + ((piVar8[4] << 0x1c) >> 0x1f) * -4 + 0x5c),0,uVar4);
            fVar13 = (float)VectorSignedToFloat(uVar9,(byte)(in_fpscr >> 0x16) & 3);
            local_108 = (float)VectorSignedToFloat(iVar6,(byte)(in_fpscr >> 0x16) & 3);
            local_108 = local_108 + fVar13;
            iVar11 = iVar1;
            if (uVar10 != 0) {
              local_dc = (int)local_110 - iVar3;
              local_d4 = iVar3 + (int)local_110;
              local_d8 = (int)local_10c - iVar7;
              local_d0 = iVar7 + (int)local_10c;
              iVar11 = iVar12;
              if ((*(int *)(piVar8[1] + iVar1 * 4) != 0x7fffffff) &&
                 (*(int *)(piVar8[1] + iVar12 * 4) != 0x7fffffff)) {
                local_120 = uVar10 - 1;
                FUN_005c6fea(param_2,auStack_12c);
                if ((iVar3 != 0) && (iVar7 != 0)) {
                  local_a0 = uVar10 - 1;
                  FUN_00451c6e(param_2,auStack_ac,&local_dc);
                }
              }
            }
            if ((uVar10 == *(int *)(param_1 + 0x70) - 1U) &&
               (*(int *)(piVar8[1] + iVar12 * 4) != 0x7fffffff)) {
              local_ec = (int)local_108 - iVar3;
              local_e4 = iVar3 + (int)local_108;
              local_e8 = (int)local_104 - iVar7;
              local_e0 = iVar7 + (int)local_104;
              local_a0 = uVar10;
              FUN_00451c6e(param_2,auStack_ac,&local_ec);
            }
          }
          iVar1 = iVar11;
        }
        local_124 = local_124 + 1;
        local_a4 = local_a4 + 1;
        FUN_00439c04(param_2 + 0x18,auStack_cc,0x10);
      }
    }
  }
  return param_2;
}

