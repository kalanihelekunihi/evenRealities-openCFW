
void FUN_005ca1e2(int *param_1,undefined4 param_2,int param_3,undefined2 param_4,undefined4 param_5,
                 int *param_6,int param_7)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  int *local_e0;
  int local_dc;
  undefined4 local_d8;
  int local_d4;
  int local_d0;
  int local_cc;
  int local_c8;
  int local_c4;
  int local_c0;
  undefined1 auStack_b4 [16];
  undefined1 auStack_a4 [20];
  undefined1 auStack_90 [28];
  undefined4 local_74;
  uint local_60;
  int local_4c;
  int iStack_48;
  
  local_e0 = param_1;
  local_d8 = FUN_00451960(param_2);
  FUN_0043bb00(auStack_a4,0,0x14);
  if (local_e0[0xe] == 0) {
    snprintf(auStack_a4,0x14,&LAB_005ca484,param_5);
    *(undefined1 **)(param_3 + 0x1c) = auStack_a4;
    *(byte *)(param_3 + 0x54) = *(byte *)(param_3 + 0x54) | 1;
  }
  else {
    FUN_005cb2c8(param_1,param_3,param_4);
  }
  iVar1 = FUN_005c9d8e(param_1,0x20000);
  iVar2 = FUN_005c9d98(param_1,0x20000);
  uVar3 = FUN_005c9dac(param_1,0x20000);
  if (((((char)local_e0[0xf] == '\x02') || ((char)local_e0[0xf] == '\x04')) ||
      ((char)local_e0[0xf] == '\x01')) || ((char)local_e0[0xf] == '\0')) {
    local_e0 = (int *)(iVar1 + *param_6);
    local_dc = iVar2 + param_6[1];
    FUN_005cad90(param_1,param_3,&local_e0,auStack_b4);
    uVar10 = uVar3 & 0x7ffff;
  }
  else {
    if (((char)local_e0[0xf] != '\x10') && ((char)local_e0[0xf] != '\b')) {
      return;
    }
    local_dc = FUN_005c9da2(param_1,0x20000);
    iVar5 = FUN_005c9dde(param_1,0x20000);
    FUN_0043feca(param_1,&local_c4);
    iVar6 = FUN_00451598(&local_c4);
    iVar7 = FUN_004515a4(&local_c4);
    if (iVar6 / 2 < iVar7 / 2) {
      iVar6 = FUN_00451598(&local_c4);
    }
    else {
      iVar6 = FUN_004515a4(&local_c4);
    }
    iVar6 = iVar6 / 2;
    local_d4 = iVar6 + local_c4;
    local_d0 = iVar6 + local_c0;
    iVar7 = FUN_005c9d84(param_1,0x20000);
    iVar8 = local_e0[0x15] * 10 +
            local_dc * 10 + (uint)(local_e0[0x14] * param_7 * 10) / ((local_e0[0x12] & 0x7fffU) - 1)
    ;
    iVar9 = 0;
    if ((char)local_e0[0xf] == '\b') {
      iVar9 = ((iVar6 - iVar7) - (iVar5 + 0xf)) - *(int *)(param_3 + 0x2c);
    }
    else if ((char)local_e0[0xf] == '\x10') {
      iVar9 = *(int *)(param_3 + 0x2c) + iVar5 + 0xf + iVar7 + iVar6;
    }
    local_cc = iVar1 + iVar9 + local_d4;
    local_c8 = iVar2 + local_d0;
    if ((int)(uVar3 << 0xb) < 0) {
      uVar10 = iVar8 + (uVar3 & 0x7ffff);
      if ((int)(uVar3 << 0xc) < 0) {
        for (; 0xe10 < (int)uVar10; uVar10 = uVar10 - 0xe10) {
        }
        if (uVar10 - 0x385 < 0x5db) {
          uVar10 = uVar10 + 0x708;
        }
      }
    }
    else {
      uVar10 = uVar3 & 0x7ffff;
    }
    local_dc = 0;
    local_e0 = &local_d4;
    FUN_004513ae(&local_cc,iVar8,0x100,0x100);
    FUN_005cad90(param_1,param_3,&local_cc,auStack_b4);
  }
  if ((int)uVar10 < 1) {
    FUN_00489fe0(local_d8,param_3,auStack_b4);
  }
  else {
    uVar4 = FUN_0048475e(local_d8,0x10,auStack_b4);
    FUN_00489fe0(uVar4,param_3,auStack_b4);
    iVar1 = FUN_00451598(auStack_b4);
    iVar2 = FUN_004515a4(auStack_b4);
    FUN_00488918(auStack_90);
    local_74 = uVar4;
    local_60 = uVar10;
    local_4c = iVar1 / 2;
    iStack_48 = iVar2 / 2;
    FUN_0048895e(local_d8,auStack_90,auStack_b4);
  }
  if ((int)((uint)*(byte *)(param_3 + 0x54) << 0x1f) < 0) {
    *(undefined4 *)(param_3 + 0x1c) = 0;
    *(byte *)(param_3 + 0x54) = *(byte *)(param_3 + 0x54) & 0xfe;
  }
  return;
}

