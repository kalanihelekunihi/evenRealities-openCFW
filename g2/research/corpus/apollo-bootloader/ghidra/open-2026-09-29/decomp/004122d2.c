
uint FUN_004122d2(int param_1,int param_2,undefined *param_3,undefined4 param_4,undefined4 param_5,
                 ushort param_6,ushort param_7)

{
  char cVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  byte bVar5;
  undefined *local_70;
  undefined4 local_6c;
  undefined4 local_68;
  undefined4 local_64;
  uint local_60;
  uint local_5c;
  uint local_58;
  undefined4 local_54;
  int *local_50;
  undefined4 local_4c;
  uint local_48;
  undefined4 local_44;
  int local_38;
  int local_34;
  undefined4 *local_30;
  undefined *local_2c;
  undefined4 local_28;
  
  bVar5 = 0;
  local_2c = param_3;
  local_28 = param_4;
  cVar1 = FUN_004122a6(param_1,param_2);
  *(int *)(param_2 + 8) = *(int *)(param_2 + 8) + 1;
  if (cVar1 == '\0') goto LAB_00412374;
  local_64 = *DAT_00412f6c;
  local_60 = DAT_00412f6c[1];
  iVar2 = FUN_00410af2(param_2,&local_64);
  if (iVar2 == 0) goto LAB_00412374;
  do {
    bVar5 = 1;
    FUN_00410522(param_1,param_1 + 0x10);
    if (cVar1 == '\0') {
      local_70 = &DAT_004125a4;
      FUN_00415fae(DAT_00412f74,DAT_00412f70,0x836,*(undefined4 *)(param_2 + 4));
    }
    local_5c = *DAT_00412f78;
    local_58 = DAT_00412f78[1];
    iVar2 = FUN_00410af2(param_2,&local_5c);
    if (iVar2 == 0) {
      local_70 = &DAT_004125a4;
      FUN_00415fae(DAT_00413204,DAT_00412f70,0x83c,*(undefined4 *)(param_2 + 4));
      return 0xffffffe4;
    }
    uVar3 = FUN_00410e8e(param_1,param_2 + 4);
    if (uVar3 != 0) {
      if (uVar3 != 0xffffffe4) {
        return uVar3;
      }
      if (cVar1 == '\0') {
        return 0xffffffe4;
      }
    }
    cVar1 = '\0';
LAB_00412374:
    FUN_004156ac(&local_4c,DAT_00412f7c,0x18);
    local_4c = *(undefined4 *)(param_2 + 4);
    if (*(int *)(*(int *)(param_1 + 0x68) + 0x4c) == 0) {
      local_38 = *(int *)(*(int *)(param_1 + 0x68) + 0x1c);
    }
    else {
      local_38 = *(int *)(*(int *)(param_1 + 0x68) + 0x4c);
    }
    local_38 = local_38 + -8;
    uVar3 = FUN_00410a36(param_1,*(undefined4 *)(param_2 + 4));
    if (uVar3 == 0) {
      uVar4 = lfs_tole32(*(undefined4 *)(param_2 + 8));
      *(undefined4 *)(param_2 + 8) = uVar4;
      uVar3 = FUN_00411e60(param_1,&local_4c,param_2 + 8,4);
      uVar4 = lfs_fromle32(*(undefined4 *)(param_2 + 8));
      *(undefined4 *)(param_2 + 8) = uVar4;
      if (uVar3 == 0) {
        local_30 = &local_4c;
        local_50 = &local_34;
        local_54 = DAT_00412f80;
        local_58 = (uint)(short)-param_6;
        local_5c = (uint)param_7;
        local_60 = (uint)param_6;
        local_64 = 0;
        local_68 = DAT_00412f84;
        local_6c = local_28;
        local_70 = local_2c;
        local_34 = param_1;
        uVar3 = FUN_004112b4(param_1,param_5,0,0xffffffff);
        if (uVar3 == 0) {
          iVar2 = FUN_00410ad8(param_2 + 0x18);
          if (iVar2 == 0) {
            FUN_00410b5c(param_2 + 0x18);
            uVar3 = FUN_00411e9c(param_1,&local_4c,
                                 DAT_00412b7c | (*(byte *)(param_2 + 0x17) + 0x600) * 0x100000,
                                 param_2 + 0x18);
            FUN_00410b46(param_2 + 0x18);
            if (uVar3 != 0) goto joined_r0x004124f0;
          }
          FUN_0041560c(&local_70,0xc,0);
          if (bVar5 == 0) {
            FUN_00410bdc(&local_70,param_1 + 0x3c);
            FUN_00410bdc(&local_70,param_1 + 0x30);
          }
          FUN_00410bdc(&local_70,param_1 + 0x48);
          local_70 = (undefined *)((uint)local_70 & 0xfffffc00);
          uVar3 = FUN_00411c04(param_1,param_2,&local_70);
          if (uVar3 != 0) {
            return uVar3;
          }
          iVar2 = FUN_00410bfa(&local_70);
          if (iVar2 == 0) {
            FUN_00410ca8(&local_70);
            uVar3 = FUN_00411e9c(param_1,&local_4c,DAT_00413154,&local_70);
            if (uVar3 != 0) goto joined_r0x004124f0;
          }
          uVar3 = FUN_00411f52(param_1,&local_4c);
          if (uVar3 == 0) {
            uVar3 = *(uint *)(*(int *)(param_1 + 0x68) + 0x18);
            if (local_48 != uVar3 * (local_48 / uVar3)) {
              FUN_00415734(DAT_00413158,DAT_00412f70,0x824);
            }
            FUN_00410ace(param_2);
            *(ushort *)(param_2 + 0x14) = param_7 - param_6;
            *(uint *)(param_2 + 0xc) = local_48;
            *(undefined4 *)(param_2 + 0x10) = local_44;
            *(undefined4 *)(param_1 + 0x48) = 0;
            *(undefined4 *)(param_1 + 0x4c) = 0;
            *(undefined4 *)(param_1 + 0x50) = 0;
            if (bVar5 == 0) {
              *(undefined4 *)(param_1 + 0x3c) = *(undefined4 *)(param_1 + 0x30);
              *(undefined4 *)(param_1 + 0x40) = *(undefined4 *)(param_1 + 0x34);
              *(undefined4 *)(param_1 + 0x44) = *(undefined4 *)(param_1 + 0x38);
            }
            return (uint)bVar5;
          }
        }
      }
    }
joined_r0x004124f0:
    if (uVar3 != 0xffffffac) {
      return uVar3;
    }
  } while( true );
}

