
undefined4 FUN_005c5f38(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  int iVar10;
  uint in_fpscr;
  uint uVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  int local_148;
  undefined1 auStack_140 [8];
  int local_138;
  uint local_134;
  int local_130;
  float local_124;
  float local_120;
  float local_11c;
  float local_118;
  undefined1 auStack_114 [4];
  int local_110;
  byte local_103;
  int local_100;
  int local_fc;
  int local_f8;
  int local_f4;
  int local_f0;
  int local_ec;
  int local_e8;
  int local_e4;
  int local_e0;
  int local_dc;
  int local_d8 [2];
  int local_d0;
  undefined1 auStack_c8 [8];
  int local_c0;
  int local_bc;
  int local_b8;
  undefined1 auStack_a7 [79];
  undefined1 auStack_58 [16];
  undefined1 auStack_48 [16];
  
  iVar3 = FUN_00450bcc(auStack_48,param_1 + 0x14,param_2 + 0x18);
  if (iVar3 != 0) {
    FUN_00439c04(local_d8,param_2 + 0x18,0x10);
    FUN_00439c04(param_2 + 0x18,auStack_48,0x10);
    if (1 < *(uint *)(param_1 + 0x70)) {
      iVar3 = FUN_005c579c(param_1,0);
      iVar4 = FUN_005c5772(param_1,0);
      iVar5 = FUN_005c575e(param_1,0);
      local_fc = FUN_0043fe16(param_1);
      iVar6 = FUN_0043fe70(param_1);
      iVar7 = FUN_0044e586(param_1);
      iVar7 = (iVar3 + iVar4 + *(int *)(param_1 + 0x14)) - iVar7;
      local_100 = FUN_0044e4aa(param_1);
      local_100 = (iVar3 + iVar5 + *(int *)(param_1 + 0x18)) - local_100;
      cVar2 = FUN_00450bcc(auStack_58,param_1 + 0x14,param_2 + 0x18);
      if (cVar2 != '\0') {
        FUN_005c6fbc(auStack_140);
        local_130 = param_2;
        FUN_00452b0e(param_1,0x50000,auStack_140);
        FUN_00451b9c(auStack_c8);
        local_b8 = param_2;
        FUN_00452616(param_1,0x20000,auStack_c8);
        iVar4 = FUN_005c574a(param_1,0x20000);
        iVar4 = iVar4 / 2;
        iVar5 = FUN_005c5754(param_1,0x20000);
        iVar5 = iVar5 / 2;
        iVar3 = iVar5;
        if (iVar4 < iVar5) {
          iVar3 = iVar4;
        }
        if (local_110 / 2 < iVar3) {
          local_103 = local_103 | 4;
        }
        if (local_110 == 1) {
          local_103 = local_103 | 4;
        }
        bVar1 = *(int *)(param_1 + 0x70) < local_fc;
        local_138 = FUN_00482d02(param_1 + 0x2c);
        local_138 = local_138 + -1;
        local_c0 = local_138;
        for (iVar3 = FUN_00482ce4(param_1 + 0x2c); iVar3 != 0;
            iVar3 = FUN_00482cfa(param_1 + 0x2c,iVar3)) {
          if (-1 < (int)((uint)*(byte *)(iVar3 + 0x10) << 0x1f)) {
            FUN_00439be4(auStack_114,iVar3 + 8,3);
            FUN_00439be4(auStack_a7,iVar3 + 8,3);
            local_134 = 0;
            local_bc = 0;
            if ((*(byte *)(param_1 + 0x74) & 0x1f) >> 3 == 0) {
              local_148 = *(int *)(iVar3 + 0xc);
            }
            else {
              local_148 = 0;
            }
            local_124 = (float)VectorSignedToFloat(iVar7,(byte)(in_fpscr >> 0x16) & 3);
            local_11c = (float)VectorSignedToFloat(iVar7,(byte)(in_fpscr >> 0x16) & 3);
            fVar12 = (float)VectorSignedToFloat(local_100 +
                                                (iVar6 - (iVar6 * (*(int *)(*(int *)(iVar3 + 4) +
                                                                           local_148 * 4) -
                                                                  *(int *)(param_1 + ((*(int *)(
                                                  iVar3 + 0x10) << 0x1b) >> 0x1f) * -4 + 0x44))) /
                                                  (*(int *)(param_1 + ((*(int *)(iVar3 + 0x10) <<
                                                                       0x1b) >> 0x1f) * -4 + 0x4c) -
                                                  *(int *)(param_1 + ((*(int *)(iVar3 + 0x10) <<
                                                                      0x1b) >> 0x1f) * -4 + 0x44))),
                                                (byte)(in_fpscr >> 0x16) & 3);
            iVar10 = local_148;
            fVar16 = fVar12;
            local_118 = fVar12;
            for (uVar8 = 0; uVar8 < *(uint *)(param_1 + 0x70); uVar8 = uVar8 + 1) {
              local_124 = local_11c;
              local_120 = local_118;
              fVar14 = (float)VectorSignedToFloat(iVar4 + local_d0 + 1,(byte)(in_fpscr >> 0x16) & 3)
              ;
              uVar11 = in_fpscr & 0xfffffff;
              in_fpscr = uVar11;
              if (fVar14 < local_11c) break;
              fVar14 = (float)VectorUnsignedToFloat
                                        ((uVar8 * local_fc) / (*(int *)(param_1 + 0x70) - 1U),
                                         (byte)(uVar11 >> 0x16) & 3);
              fVar15 = (float)VectorSignedToFloat(iVar7,(byte)(uVar11 >> 0x16) & 3);
              fVar14 = fVar14 + fVar15;
              iVar9 = (uVar8 + local_148) -
                      *(uint *)(param_1 + 0x70) * ((uVar8 + local_148) / *(uint *)(param_1 + 0x70));
              fVar15 = (float)VectorSignedToFloat(local_100 +
                                                  (iVar6 - (iVar6 * (*(int *)(*(int *)(iVar3 + 4) +
                                                                             iVar9 * 4) -
                                                                    *(int *)(param_1 + ((*(int *)(
                                                  iVar3 + 0x10) << 0x1b) >> 0x1f) * -4 + 0x44))) /
                                                  (*(int *)(param_1 + ((*(int *)(iVar3 + 0x10) <<
                                                                       0x1b) >> 0x1f) * -4 + 0x4c) -
                                                  *(int *)(param_1 + ((*(int *)(iVar3 + 0x10) <<
                                                                      0x1b) >> 0x1f) * -4 + 0x44))),
                                                  (byte)(uVar11 >> 0x16) & 3);
              fVar13 = (float)VectorSignedToFloat((local_d8[0] - iVar4) + -1,
                                                  (byte)(uVar11 >> 0x16) & 3);
              if ((fVar13 <= fVar14) && (uVar8 != 0)) {
                if (bVar1) {
                  local_e8 = (int)local_11c - iVar4;
                  local_e0 = iVar4 + (int)local_11c;
                  local_e4 = (int)local_118 - iVar5;
                  local_dc = iVar5 + (int)local_118;
                  local_11c = fVar14;
                  local_118 = fVar15;
                  if ((*(int *)(*(int *)(iVar3 + 4) + iVar10 * 4) != 0x7fffffff) &&
                     (*(int *)(*(int *)(iVar3 + 4) + iVar9 * 4) != 0x7fffffff)) {
                    local_134 = uVar8;
                    FUN_005c6fea(param_2,auStack_140);
                  }
                  in_fpscr = uVar11;
                  fVar14 = local_11c;
                  fVar15 = local_118;
                  if (((iVar4 != 0) && (iVar5 != 0)) &&
                     (*(int *)(*(int *)(iVar3 + 4) + iVar10 * 4) != 0x7fffffff)) {
                    local_bc = uVar8 - 1;
                    FUN_00451c6e(param_2,auStack_c8,&local_e8);
                    in_fpscr = uVar11;
                    fVar14 = local_11c;
                    fVar15 = local_118;
                  }
                }
                else if ((*(int *)(*(int *)(iVar3 + 4) + iVar10 * 4) != 0x7fffffff) &&
                        (*(int *)(*(int *)(iVar3 + 4) + iVar9 * 4) != 0x7fffffff)) {
                  local_118 = fVar12;
                  if (fVar12 <= fVar15) {
                    local_118 = fVar15;
                  }
                  if (fVar15 <= fVar16) {
                    fVar16 = fVar15;
                  }
                  in_fpscr = uVar11 | (uint)(local_11c == fVar14) << 0x1e;
                  fVar12 = local_118;
                  if ((byte)(in_fpscr >> 0x1e) == 0) {
                    local_124 = fVar14 + -1.0;
                    in_fpscr = uVar11 | (uint)(fVar16 == local_118) << 0x1e;
                    if ((byte)(in_fpscr >> 0x1e) != 0) {
                      local_118 = local_118 + 1.0;
                    }
                    local_120 = fVar16;
                    local_11c = local_124;
                    FUN_005c6fea(param_2,auStack_140);
                    fVar12 = fVar15;
                    fVar16 = fVar15;
                    fVar14 = local_11c + 1.0;
                    fVar15 = local_118;
                  }
                }
              }
              local_118 = fVar15;
              local_11c = fVar14;
              iVar10 = iVar9;
            }
            if (((bVar1) && (uVar8 == *(uint *)(param_1 + 0x70))) &&
               (*(int *)(*(int *)(iVar3 + 4) + iVar10 * 4) != 0x7fffffff)) {
              local_f8 = (int)local_11c - iVar4;
              local_f0 = iVar4 + (int)local_11c;
              local_f4 = (int)local_118 - iVar5;
              local_ec = iVar5 + (int)local_118;
              local_bc = uVar8 - 1;
              FUN_00451c6e(param_2,auStack_c8,&local_f8);
            }
          }
          local_c0 = local_c0 + -1;
          local_138 = local_138 + -1;
        }
        FUN_00439c04(param_2 + 0x18,local_d8,0x10);
      }
    }
  }
  return param_4;
}

