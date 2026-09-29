
void FUN_005c215c(int *param_1)

{
  ushort uVar1;
  byte bVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  uint uVar11;
  undefined4 uVar12;
  int local_210;
  int local_20c;
  int local_208;
  int local_204;
  int local_200;
  int local_1fc;
  undefined4 local_1f8;
  undefined4 local_1f4;
  undefined4 local_1f0;
  int local_1ec;
  int local_1e8;
  int local_1e4;
  int local_1e0;
  int local_1dc;
  int local_1d8;
  undefined1 auStack_1cc [8];
  uint local_1c4;
  undefined4 local_1bc;
  undefined4 local_1b0;
  undefined4 local_1ac;
  undefined4 local_1a4;
  undefined4 local_1a0;
  byte local_179;
  byte local_178;
  undefined1 auStack_168 [8];
  uint local_160;
  undefined4 local_158;
  byte local_11f;
  undefined1 auStack_f8 [16];
  undefined4 local_e8;
  undefined1 auStack_94 [16];
  undefined4 local_84;
  
  iVar4 = *param_1;
  if (*(int *)(iVar4 + 0x38) != 0) {
    uVar5 = FUN_00451960(param_1);
    *(ushort *)(iVar4 + 0x2a) = *(ushort *)(iVar4 + 0x2a) | 8;
    FUN_0043fc2a(iVar4,&local_1dc);
    iVar9 = 0;
    uVar1 = *(ushort *)(iVar4 + 0x28);
    *(undefined2 *)(iVar4 + 0x28) = 0;
    *(ushort *)(iVar4 + 0x2a) = *(ushort *)(iVar4 + 0x2a) | 8;
    FUN_00451b9c(auStack_94);
    local_84 = uVar5;
    FUN_00489f5e(auStack_f8);
    local_e8 = uVar5;
    FUN_00452616(iVar4,0x50000,auStack_94);
    FUN_00452988(iVar4,0x50000,auStack_f8);
    *(ushort *)(iVar4 + 0x2a) = *(ushort *)(iVar4 + 0x2a) & 0xfff7;
    *(ushort *)(iVar4 + 0x28) = uVar1;
    local_1e0 = FUN_005c1606(iVar4,0);
    local_1e4 = FUN_005c1610(iVar4,0);
    local_1e8 = FUN_005c161a(iVar4,0);
    local_1ec = FUN_005c1624(iVar4,0);
    for (uVar10 = 0; uVar10 < *(uint *)(iVar4 + 0x38); uVar10 = uVar10 + 1) {
      while (iVar8 = FUN_004547be(*(undefined4 *)(*(int *)(iVar4 + 0x2c) + iVar9 * 4),&DAT_005c25c0)
            , iVar8 == 0) {
        iVar9 = iVar9 + 1;
      }
      iVar8 = FUN_005c25d6(*(undefined2 *)(*(int *)(iVar4 + 0x34) + uVar10 * 2));
      if (iVar8 == 0) {
        iVar8 = FUN_005c2618(*(undefined2 *)(*(int *)(iVar4 + 0x34) + uVar10 * 2));
        uVar11 = (uint)(iVar8 != 0);
        iVar8 = FUN_005c25f4(*(undefined2 *)(*(int *)(iVar4 + 0x34) + uVar10 * 2));
        if (iVar8 == 0) {
          if (uVar10 == *(uint *)(iVar4 + 0x40)) {
            if ((int)((uint)uVar1 << 0x1a) < 0) {
              uVar11 = uVar11 | 0x20;
            }
            if ((int)((uint)uVar1 << 0x1e) < 0) {
              uVar11 = uVar11 | 2;
            }
            if ((int)((uint)uVar1 << 0x1d) < 0) {
              uVar11 = uVar11 | 4;
            }
            if ((int)((uint)uVar1 << 0x1c) < 0) {
              uVar11 = uVar11 | 8;
            }
          }
        }
        else {
          uVar11 = uVar11 | 0x80;
        }
        FUN_005c15e8(&local_210,uVar10 * 0x10 + *(int *)(iVar4 + 0x30));
        local_210 = local_1dc + local_210;
        local_20c = local_1d8 + local_20c;
        local_208 = local_1dc + local_208;
        local_204 = local_1d8 + local_204;
        if (uVar11 == 0) {
          FUN_00454738(auStack_168,auStack_94,0x70);
          FUN_00454738(auStack_1cc,auStack_f8,100);
        }
        else {
          *(short *)(iVar4 + 0x28) = (short)uVar11;
          *(ushort *)(iVar4 + 0x2a) = *(ushort *)(iVar4 + 0x2a) | 8;
          FUN_00451b9c(auStack_168);
          local_158 = uVar5;
          FUN_00489f5e(auStack_1cc);
          local_1bc = uVar5;
          FUN_00452616(iVar4,0x50000,auStack_168);
          FUN_00452988(iVar4,0x50000,auStack_1cc);
          *(ushort *)(iVar4 + 0x28) = uVar1;
          *(ushort *)(iVar4 + 0x2a) = *(ushort *)(iVar4 + 0x2a) & 0xfff7;
        }
        cVar3 = FUN_005c28fa(*(undefined2 *)(*(int *)(iVar4 + 0x34) + uVar10 * 2));
        if (cVar3 == '\0') {
          local_179 = local_179 & 0xbf;
        }
        else {
          local_179 = local_179 | 0x40;
        }
        if ((int)((uint)local_11f << 0x1b) < 0) {
          bVar2 = local_11f & 0xe0;
          local_11f = bVar2 | 0xf;
          if (local_210 == local_1e8 + *(int *)(iVar4 + 0x14)) {
            local_11f = bVar2 | 0xb;
          }
          if (local_208 == *(int *)(iVar4 + 0x1c) - local_1ec) {
            local_11f = local_11f & 0xf7;
          }
          if (local_20c == local_1e0 + *(int *)(iVar4 + 0x18)) {
            local_11f = local_11f & 0xfd;
          }
          if (local_204 == *(int *)(iVar4 + 0x20) - local_1e4) {
            local_11f = local_11f & 0xfe;
          }
        }
        local_160 = uVar10;
        iVar8 = FUN_004515a4(&local_210);
        if (((int)(uVar11 << 0x1a) < 0) &&
           ((int)((uint)*(ushort *)(*(int *)(iVar4 + 0x34) + uVar10 * 2) << 0x15) < 0)) {
          local_20c = local_20c - iVar8;
        }
        FUN_00451c6e(uVar5,auStack_168,&local_210);
        local_1f0 = local_1ac;
        local_1f4 = local_1a0;
        local_1f8 = local_1a4;
        uVar12 = *(undefined4 *)(*(int *)(iVar4 + 0x2c) + iVar9 * 4);
        uVar6 = FUN_00451598(&local_1dc);
        FUN_00489546(&local_200,uVar12,local_1f0,local_1f4,local_1f8,uVar6,local_179 >> 3);
        iVar7 = FUN_00451598(&local_210);
        local_210 = (iVar7 - local_200) / 2 + local_210;
        iVar7 = FUN_004515a4(&local_210);
        local_20c = (iVar7 - local_1fc) / 2 + local_20c;
        local_208 = local_200 + local_210;
        local_204 = local_1fc + local_20c;
        if (((int)(uVar11 << 0x1a) < 0) &&
           ((int)((uint)*(ushort *)(*(int *)(iVar4 + 0x34) + uVar10 * 2) << 0x15) < 0)) {
          local_20c = local_20c - iVar8 / 2;
          local_204 = local_204 - iVar8 / 2;
        }
        local_178 = local_178 | 1;
        local_1c4 = uVar10;
        local_1b0 = uVar12;
        FUN_00489fe0(uVar5,auStack_1cc,&local_210);
      }
      iVar9 = iVar9 + 1;
    }
    *(ushort *)(iVar4 + 0x2a) = *(ushort *)(iVar4 + 0x2a) & 0xfff7;
  }
  return;
}

