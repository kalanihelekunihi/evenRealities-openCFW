
void FUN_005cce68(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined2 uVar1;
  char cVar2;
  ushort uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  undefined4 uVar9;
  int iVar10;
  uint uVar11;
  int iVar12;
  byte bVar13;
  byte *pbVar14;
  bool bVar15;
  bool bVar16;
  uint local_258;
  int local_254;
  int local_250;
  int local_24c;
  int local_248;
  int local_244;
  int local_240;
  int local_23c;
  int local_238;
  int local_234;
  int local_230;
  int local_22c;
  int local_228;
  int local_224;
  int local_220;
  int local_21c;
  int local_218;
  int local_214;
  int local_210;
  int local_20c;
  undefined1 auStack_208 [4];
  int local_204;
  undefined1 auStack_200 [4];
  int local_1fc;
  int local_1f4;
  undefined1 auStack_1f0 [16];
  undefined1 auStack_1e0 [8];
  uint local_1d8;
  uint local_1d4;
  int local_1d0;
  int local_1c4;
  undefined4 local_1b8;
  undefined4 local_1b4;
  byte local_18d;
  undefined1 auStack_17c [16];
  int local_16c;
  uint local_138;
  byte local_133;
  undefined1 auStack_10c [16];
  undefined1 auStack_fc [16];
  int local_ec;
  undefined4 local_dc;
  undefined1 auStack_98 [8];
  uint local_90;
  uint local_8c;
  int local_88;
  undefined4 uStack_28;
  
  iVar4 = *param_1;
  uStack_28 = param_4;
  iVar5 = FUN_00451960(param_1);
  iVar6 = FUN_00450bcc(auStack_200,iVar4 + 0x14,iVar5 + 0x18);
  if (iVar6 != 0) {
    FUN_00439c04(auStack_10c,iVar5 + 0x18,0x10);
    FUN_00439c04(iVar5 + 0x18,auStack_200,0x10);
    local_240 = FUN_005ccb72(iVar4,0);
    local_220 = FUN_005ccb4a(iVar4,0);
    local_20c = FUN_005ccb54(iVar4,0);
    local_224 = FUN_005ccb5e(iVar4,0);
    local_228 = FUN_005ccb68(iVar4,0);
    uVar1 = *(undefined2 *)(iVar4 + 0x28);
    *(undefined2 *)(iVar4 + 0x28) = 0;
    *(ushort *)(iVar4 + 0x2a) = *(ushort *)(iVar4 + 0x2a) | 8;
    FUN_00451b9c(auStack_17c);
    local_16c = iVar5;
    FUN_00452616(iVar4,0x50000,auStack_17c);
    FUN_00489f5e(auStack_fc);
    local_ec = iVar5;
    FUN_00452988(iVar4,0x50000,auStack_fc);
    *(undefined2 *)(iVar4 + 0x28) = uVar1;
    *(ushort *)(iVar4 + 0x2a) = *(ushort *)(iVar4 + 0x2a) & 0xfff7;
    iVar12 = 0;
    iVar6 = FUN_0044e498(iVar4);
    local_248 = local_240 + ((local_220 + *(int *)(iVar4 + 0x18) + -1) - iVar6);
    local_254 = 0;
    local_24c = 0;
    local_22c = FUN_0044e486(iVar4);
    iVar6 = FUN_005ccb9a(iVar4,0);
    bVar15 = iVar6 != 1;
    for (local_258 = 0; local_258 < *(uint *)(iVar4 + 0x30); local_258 = local_258 + 1) {
      local_244 = *(int *)(*(int *)(iVar4 + 0x38) + local_258 * 4);
      local_250 = local_248 + 1;
      local_248 = local_244 + local_250 + -1;
      if (local_1f4 < local_250) break;
      if (bVar15) {
        local_24c = local_240 + ((local_224 + *(int *)(iVar4 + 0x14) + -1) - local_22c);
      }
      else {
        local_254 = (((*(int *)(iVar4 + 0x1c) - local_228) + -1) - local_22c) - local_240;
      }
      for (uVar11 = 0; uVar11 < *(uint *)(iVar4 + 0x2c); uVar11 = iVar6 + uVar11 + 1) {
        bVar13 = 0;
        if (*(int *)(*(int *)(iVar4 + 0x34) + iVar12 * 4) != 0) {
          bVar13 = **(byte **)(*(int *)(iVar4 + 0x34) + iVar12 * 4);
        }
        if (bVar15) {
          local_254 = local_24c + 1;
          local_24c = *(int *)(*(int *)(iVar4 + 0x3c) + uVar11 * 4) + local_254 + -1;
        }
        else {
          local_24c = local_254 + -1;
          local_254 = (local_24c - *(int *)(*(int *)(iVar4 + 0x3c) + uVar11 * 4)) + 1;
        }
        for (iVar6 = 0; uVar11 + iVar6 < *(int *)(iVar4 + 0x2c) - 1U; iVar6 = iVar6 + 1) {
          pbVar14 = *(byte **)(*(int *)(iVar4 + 0x34) + (iVar6 + iVar12) * 4);
          iVar10 = FUN_005ccba6(pbVar14);
          if ((iVar10 != 0) || (-1 < (int)((uint)*pbVar14 << 0x1f))) break;
          iVar10 = *(int *)(*(int *)(iVar4 + 0x3c) + (iVar6 + uVar11) * 4 + 4);
          if (bVar15) {
            local_24c = iVar10 + local_24c;
          }
          else {
            local_254 = local_254 - iVar10;
          }
        }
        if (local_1fc <= local_248) {
          FUN_005ccb24(&local_23c,&local_254);
          if (((int)((uint)local_133 << 0x1d) < 0) &&
             (local_224 + *(int *)(iVar4 + 0x14) < local_23c)) {
            local_23c = local_23c - (int)local_138 / 2;
          }
          if (((int)((uint)local_133 << 0x1e) < 0) &&
             (local_220 + *(int *)(iVar4 + 0x18) < local_238)) {
            local_238 = local_238 - (int)local_138 / 2;
          }
          if (((int)((uint)local_133 << 0x1c) < 0) &&
             (local_234 < (*(int *)(iVar4 + 0x1c) - local_228) + -1)) {
            local_234 = (local_138 & 1) + (int)local_138 / 2 + local_234;
          }
          if (((int)((uint)local_133 << 0x1f) < 0) &&
             (local_230 < (*(int *)(iVar4 + 0x20) - local_20c) + -1)) {
            local_230 = (local_138 & 1) + (int)local_138 / 2 + local_230;
          }
          uVar3 = 0;
          if ((local_258 == *(uint *)(iVar4 + 0x44)) && (uVar11 == *(uint *)(iVar4 + 0x40))) {
            if ((*(byte *)(iVar4 + 0x28) & 0x60) == 0x20) {
              uVar3 = 0x20;
            }
            if ((int)((uint)*(byte *)(iVar4 + 0x28) << 0x1e) < 0) {
              uVar3 = uVar3 | 2;
            }
            if ((int)((uint)*(byte *)(iVar4 + 0x28) << 0x1d) < 0) {
              uVar3 = uVar3 | 4;
            }
            if ((int)((uint)*(byte *)(iVar4 + 0x28) << 0x1c) < 0) {
              uVar3 = uVar3 | 8;
            }
          }
          if (uVar3 == 0) {
            FUN_00454738(auStack_98,auStack_17c,0x70);
            FUN_00454738(auStack_1e0,auStack_fc,100);
          }
          else {
            *(ushort *)(iVar4 + 0x28) = uVar3;
            *(ushort *)(iVar4 + 0x2a) = *(ushort *)(iVar4 + 0x2a) | 8;
            FUN_00451b9c(auStack_98);
            local_88 = iVar5;
            FUN_00489f5e(auStack_1e0);
            local_1d0 = iVar5;
            FUN_00452616(iVar4,0x50000,auStack_98);
            FUN_00452988(iVar4,0x50000,auStack_1e0);
            *(undefined2 *)(iVar4 + 0x28) = uVar1;
            *(ushort *)(iVar4 + 0x2a) = *(ushort *)(iVar4 + 0x2a) & 0xfff7;
          }
          local_90 = local_258;
          local_1d8 = local_258;
          local_1d4 = uVar11;
          local_8c = uVar11;
          FUN_00451c6e(iVar5,auStack_98,&local_23c);
          if (*(int *)(*(int *)(iVar4 + 0x34) + iVar12 * 4) != 0) {
            iVar10 = FUN_005ccb5e(iVar4,0x50000);
            iVar7 = FUN_005ccb68(iVar4,0x50000);
            iVar8 = FUN_005ccb4a(iVar4,0x50000);
            local_210 = FUN_005ccb54(iVar4,0x50000);
            local_21c = iVar10 + local_254;
            local_214 = local_24c - iVar7;
            local_218 = iVar8 + local_250;
            local_210 = local_248 - local_210;
            bVar16 = (bVar13 >> 1 & 1) != 0;
            if (bVar16) {
              local_18d = local_18d | 8;
            }
            uVar9 = FUN_00451598(&local_21c);
            FUN_00489546(auStack_208,*(int *)(*(int *)(iVar4 + 0x34) + iVar12 * 4) + 8,local_dc,
                         local_1b4,local_1b8,uVar9,bVar16);
            if ((bVar13 >> 1 & 1) == 0) {
              local_218 = (local_244 / 2 + local_250) - local_204 / 2;
              local_210 = local_204 / 2 + local_244 / 2 + local_250;
            }
            cVar2 = FUN_00450bcc(auStack_1f0,auStack_200,&local_254);
            if (cVar2 != '\0') {
              FUN_00439c04(iVar5 + 0x18,auStack_1f0,0x10);
              local_1c4 = *(int *)(*(int *)(iVar4 + 0x34) + iVar12 * 4) + 8;
              FUN_00489fe0(iVar5,auStack_1e0,&local_21c);
              FUN_00439c04(iVar5 + 0x18,auStack_200,0x10);
            }
          }
        }
        iVar12 = iVar6 + iVar12 + 1;
      }
    }
    FUN_00439c04(iVar5 + 0x18,auStack_10c,0x10);
  }
  return;
}

