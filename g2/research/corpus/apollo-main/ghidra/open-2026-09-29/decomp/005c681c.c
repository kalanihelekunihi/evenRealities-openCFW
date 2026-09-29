
void FUN_005c681c(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  uint uVar13;
  int iVar14;
  int iVar15;
  int local_c8;
  int local_c4;
  int local_c0;
  int local_bc;
  int local_b8 [2];
  int local_b0;
  undefined1 auStack_a8 [8];
  int local_a0;
  uint local_9c;
  int local_98;
  int local_8c;
  undefined1 local_88;
  undefined1 auStack_87 [14];
  byte local_79;
  undefined1 auStack_38 [16];
  undefined4 uStack_28;
  
  uStack_28 = param_4;
  iVar1 = FUN_00450bcc(local_b8,param_1 + 0x14,param_2 + 0x18);
  if (iVar1 != 0) {
    FUN_00439c04(auStack_38,param_2 + 0x18,0x10);
    FUN_00439c04(param_2 + 0x18,local_b8,0x10);
    iVar1 = FUN_005c5772(param_1,0);
    iVar2 = FUN_005c575e(param_1,0);
    iVar3 = FUN_0043fe16(param_1);
    iVar4 = FUN_0043fe70(param_1);
    uVar5 = FUN_00482d02(param_1 + 0x2c);
    if (uVar5 != 0) {
      iVar6 = FUN_005c5786(param_1,0);
      uVar7 = (uint)(iVar3 - iVar6 * (*(int *)(param_1 + 0x70) + -1)) / *(uint *)(param_1 + 0x70);
      iVar6 = FUN_005c5786(param_1,0x50000);
      uVar5 = (uVar7 - iVar6 * (uVar5 - 1)) / uVar5;
      if ((int)uVar5 < 1) {
        uVar5 = 1;
      }
      iVar8 = FUN_005c579c(param_1,0);
      iVar9 = FUN_0044e586(param_1);
      iVar10 = FUN_0044e4aa(param_1);
      FUN_00451b9c(auStack_a8);
      local_98 = param_2;
      FUN_00452616(param_1,0x50000,auStack_a8);
      local_79 = local_79 & 0xf0;
      local_88 = 0xff;
      local_bc = local_8c + *(int *)(param_1 + 0x20);
      for (uVar13 = 0; uVar13 < *(uint *)(param_1 + 0x70); uVar13 = uVar13 + 1) {
        if (*(uint *)(param_1 + 0x70) < 2) {
          iVar11 = *(int *)(param_1 + 0x14);
        }
        else {
          iVar11 = *(int *)(param_1 + 0x14) +
                   (uVar13 * (iVar3 - uVar7)) / (*(int *)(param_1 + 0x70) - 1U);
        }
        local_a0 = 0;
        local_9c = uVar13;
        iVar12 = FUN_00482cd8(param_1 + 0x2c);
        iVar11 = iVar8 + (iVar1 - iVar9) + iVar11;
        while (iVar12 != 0) {
          iVar14 = iVar11;
          if (-1 < (int)((uint)*(byte *)(iVar12 + 0x10) << 0x1f)) {
            if ((*(byte *)(param_1 + 0x74) & 0x1f) >> 3 == 0) {
              iVar15 = *(int *)(iVar12 + 0xc);
            }
            else {
              iVar15 = 0;
            }
            local_c0 = uVar5 + iVar11 + -1;
            iVar14 = iVar6 + uVar5 + iVar11;
            local_c8 = iVar11;
            if (local_c0 < local_b8[0]) {
              local_a0 = local_a0 + 1;
            }
            else {
              if (local_b0 < iVar11) break;
              FUN_00439be4(auStack_87,iVar12 + 8,3);
              iVar11 = (uVar13 + iVar15) -
                       *(uint *)(param_1 + 0x70) * ((uVar13 + iVar15) / *(uint *)(param_1 + 0x70));
              local_c4 = iVar8 + (iVar2 - iVar10) +
                         *(int *)(param_1 + 0x18) +
                         (iVar4 - (iVar4 * (*(int *)(*(int *)(iVar12 + 4) + iVar11 * 4) -
                                           *(int *)(param_1 + ((*(int *)(iVar12 + 0x10) << 0x1b) >>
                                                              0x1f) * -4 + 0x44))) /
                                  (*(int *)(param_1 + ((*(int *)(iVar12 + 0x10) << 0x1b) >> 0x1f) *
                                                      -4 + 0x4c) -
                                  *(int *)(param_1 + ((*(int *)(iVar12 + 0x10) << 0x1b) >> 0x1f) *
                                                     -4 + 0x44)));
              if (*(int *)(*(int *)(iVar12 + 4) + iVar11 * 4) != 0x7fffffff) {
                FUN_00451c6e(param_2,auStack_a8,&local_c8);
              }
              local_a0 = local_a0 + 1;
            }
          }
          iVar12 = FUN_00482cf0(param_1 + 0x2c,iVar12);
          iVar11 = iVar14;
        }
      }
      FUN_00439c04(param_2 + 0x18,auStack_38,0x10);
    }
  }
  return;
}

