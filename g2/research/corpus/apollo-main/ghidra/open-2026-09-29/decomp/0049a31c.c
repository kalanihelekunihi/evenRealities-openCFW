
void FUN_0049a31c(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  char cVar2;
  ushort uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined4 local_c8;
  undefined4 local_c4;
  uint local_c0;
  int local_bc;
  int local_b8;
  undefined1 auStack_b4 [12];
  undefined4 local_a8;
  int local_a4 [2];
  undefined1 auStack_9c [16];
  int local_8c;
  undefined4 local_80;
  int local_7c;
  undefined4 local_74;
  undefined4 local_70;
  int local_6c;
  int local_68;
  int local_60;
  int local_5c;
  undefined1 auStack_58 [3];
  undefined1 auStack_55 [10];
  char local_4b;
  undefined1 uStack_4a;
  byte local_49;
  byte local_48;
  int local_44;
  undefined1 local_40;
  undefined1 auStack_3f [3];
  undefined4 local_3c;
  undefined1 auStack_38 [16];
  undefined1 auStack_28 [16];
  undefined4 uStack_18;
  
  iVar4 = *param_1;
  uStack_18 = param_4;
  iVar5 = FUN_00451960(param_1);
  FUN_0043feca(iVar4,auStack_b4);
  bVar1 = FUN_0049abea(iVar4);
  FUN_00489f5e(auStack_9c);
  local_80 = *(undefined4 *)(iVar4 + 0x2c);
  local_48 = local_48 & 0xfd | (*(byte *)(iVar4 + 0x5c) >> 4 & 1) << 1;
  local_6c = *(int *)(iVar4 + 0x54);
  local_68 = *(int *)(iVar4 + 0x58);
  if (((*(byte *)(iVar4 + 0x5c) & 0xf) != 3) && (iVar6 = FUN_004515a4(auStack_b4), 0x3ff < iVar6)) {
    local_44 = iVar4 + 0x38;
  }
  local_49 = local_49 & 7 | bVar1 << 3;
  local_8c = iVar5;
  FUN_00452988(iVar4,0,auStack_9c);
  FUN_00499354(&local_4b,&uStack_4a,*(undefined4 *)(iVar4 + 0x2c));
  local_60 = FUN_00499ef8(iVar4);
  local_5c = FUN_00499f2a(iVar4);
  if ((local_60 != 0xffff) && (local_5c != 0xffff)) {
    local_c8 = FUN_004993a0(iVar4,0x40000);
    FUN_00439be4(auStack_58,&local_c8,3);
    local_c8 = FUN_00499392(iVar4,0x40000);
    FUN_00439be4(auStack_55,&local_c8,3);
  }
  local_c8 = FUN_004993de(iVar4,0);
  FUN_00439be4(auStack_3f,&local_c8,3);
  local_40 = FUN_004993f6(iVar4,0);
  local_3c = FUN_004993ec(iVar4,0);
  if ((((*(byte *)(iVar4 + 0x5c) & 0xf) == 2) || ((*(byte *)(iVar4 + 0x5c) & 0xf) == 3)) &&
     ((local_4b == '\x02' || (local_4b == '\x03')))) {
    local_c0 = (uint)bVar1;
    local_c4 = 0x1fffffff;
    local_c8 = local_74;
    FUN_00489546(local_a4,*(undefined4 *)(iVar4 + 0x2c),local_7c,local_70);
    iVar6 = FUN_00451598(auStack_b4);
    if (iVar6 < local_a4[0]) {
      local_4b = '\x01';
    }
  }
  cVar2 = FUN_00450bcc(auStack_38,auStack_b4,iVar5 + 0x18);
  if (cVar2 != '\0') {
    if ((*(byte *)(iVar4 + 0x5c) & 0xf) == 0) {
      iVar6 = FUN_0044e4aa(iVar4);
      FUN_00450bb2(auStack_b4,0,-iVar6);
      local_a8 = *(undefined4 *)(iVar4 + 0x20);
    }
    if ((((*(byte *)(iVar4 + 0x5c) & 0xf) == 2) || ((*(byte *)(iVar4 + 0x5c) & 0xf) == 3)) ||
       ((*(byte *)(iVar4 + 0x5c) & 0xf) == 4)) {
      FUN_00439c04(auStack_28,iVar5 + 0x18,0x10);
      FUN_00439c04(iVar5 + 0x18,auStack_38,0x10);
      FUN_00489fe0(iVar5,auStack_9c,auStack_b4);
      FUN_00439c04(iVar5 + 0x18,auStack_28,0x10);
    }
    else {
      FUN_00489fe0(iVar5,auStack_9c,auStack_b4);
    }
    FUN_00439c04(auStack_28,iVar5 + 0x18,0x10);
    FUN_00439c04(iVar5 + 0x18,auStack_38,0x10);
    if ((*(byte *)(iVar4 + 0x5c) & 0xf) == 3) {
      local_c0 = (uint)bVar1;
      local_c4 = 0x1fffffff;
      local_c8 = local_74;
      FUN_00489546(&local_bc,*(undefined4 *)(iVar4 + 0x2c),local_7c,local_70);
      iVar6 = FUN_00451598(auStack_b4);
      if (iVar6 < local_bc) {
        uVar3 = FUN_004d57f4(local_7c,0x20,0x20);
        local_6c = (uint)uVar3 * 3 + local_bc + *(int *)(iVar4 + 0x54);
        local_68 = *(int *)(iVar4 + 0x58);
        FUN_00489fe0(iVar5,auStack_9c,auStack_b4);
      }
      iVar6 = FUN_004515a4(auStack_b4);
      if (iVar6 < local_b8) {
        local_6c = *(int *)(iVar4 + 0x54);
        local_68 = *(int *)(local_7c + 0xc) + local_b8 + *(int *)(iVar4 + 0x58);
        FUN_00489fe0(iVar5,auStack_9c,auStack_b4);
      }
    }
    FUN_00439c04(iVar5 + 0x18,auStack_28,0x10);
  }
  return;
}

