
uint FUN_004cc6ca(int param_1,int param_2,undefined *param_3,undefined4 param_4,undefined4 param_5,
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
  cVar1 = FUN_004cc69e(param_1,param_2);
  *(int *)(param_2 + 8) = *(int *)(param_2 + 8) + 1;
  if (cVar1 == '\0') goto LAB_004cc76c;
  local_64 = *DAT_004cd368;
  local_60 = DAT_004cd368[1];
  iVar2 = FUN_004cadea(param_2,&local_64);
  if (iVar2 == 0) goto LAB_004cc76c;
  do {
    bVar5 = 1;
    FUN_004ca81a(param_1,param_1 + 0x10);
    if (cVar1 == '\0') {
      local_70 = &DAT_004cc99c;
      FUN_004733ee(DAT_004cd370,DAT_004cd36c,0x836,*(undefined4 *)(param_2 + 4));
    }
    local_5c = *DAT_004cd374;
    local_58 = DAT_004cd374[1];
    iVar2 = FUN_004cadea(param_2,&local_5c);
    if (iVar2 == 0) {
      local_70 = &DAT_004cc99c;
      FUN_004733ee(DAT_004cd600,DAT_004cd36c,0x83c,*(undefined4 *)(param_2 + 4));
      return 0xffffffe4;
    }
    uVar3 = FUN_004cb186(param_1,param_2 + 4);
    if (uVar3 != 0) {
      if (uVar3 != 0xffffffe4) {
        return uVar3;
      }
      if (cVar1 == '\0') {
        return 0xffffffe4;
      }
    }
    cVar1 = '\0';
LAB_004cc76c:
    FUN_00439c04(&local_4c,DAT_004cd378,0x18);
    local_4c = *(undefined4 *)(param_2 + 4);
    if (*(int *)(*(int *)(param_1 + 0x68) + 0x4c) == 0) {
      local_38 = *(int *)(*(int *)(param_1 + 0x68) + 0x1c);
    }
    else {
      local_38 = *(int *)(*(int *)(param_1 + 0x68) + 0x4c);
    }
    local_38 = local_38 + -8;
    uVar3 = FUN_004cad2e(param_1,*(undefined4 *)(param_2 + 4));
    if (uVar3 == 0) {
      uVar4 = lfs_tole32(*(undefined4 *)(param_2 + 8));
      *(undefined4 *)(param_2 + 8) = uVar4;
      uVar3 = FUN_004cc200(param_1,&local_4c,param_2 + 8,4);
      uVar4 = lfs_fromle32(*(undefined4 *)(param_2 + 8));
      *(undefined4 *)(param_2 + 8) = uVar4;
      if (uVar3 == 0) {
        local_30 = &local_4c;
        local_50 = &local_34;
        local_54 = DAT_004cd37c;
        local_58 = (uint)(short)-param_6;
        local_5c = (uint)param_7;
        local_60 = (uint)param_6;
        local_64 = 0;
        local_68 = DAT_004cd380;
        local_6c = local_28;
        local_70 = local_2c;
        local_34 = param_1;
        uVar3 = FUN_004cb5ac(param_1,param_5,0,0xffffffff);
        if (uVar3 == 0) {
          iVar2 = FUN_004cadd0(param_2 + 0x18);
          if (iVar2 == 0) {
            FUN_004cae54(param_2 + 0x18);
            uVar3 = FUN_004cc23c(param_1,&local_4c,
                                 DAT_004ccf78 | (*(byte *)(param_2 + 0x17) + 0x600) * 0x100000,
                                 param_2 + 0x18);
            FUN_004cae3e(param_2 + 0x18);
            if (uVar3 != 0) goto joined_r0x004cc8e8;
          }
          FUN_0043c0e4(&local_70,0xc,0);
          if (bVar5 == 0) {
            FUN_004caed4(&local_70,param_1 + 0x3c);
            FUN_004caed4(&local_70,param_1 + 0x30);
          }
          FUN_004caed4(&local_70,param_1 + 0x48);
          local_70 = (undefined *)((uint)local_70 & 0xfffffc00);
          uVar3 = FUN_004cbefc(param_1,param_2,&local_70);
          if (uVar3 != 0) {
            return uVar3;
          }
          iVar2 = FUN_004caef2(&local_70);
          if (iVar2 == 0) {
            FUN_004cafa0(&local_70);
            uVar3 = FUN_004cc23c(param_1,&local_4c,DAT_004cd550,&local_70);
            if (uVar3 != 0) goto joined_r0x004cc8e8;
          }
          uVar3 = FUN_004cc2f2(param_1,&local_4c);
          if (uVar3 == 0) {
            uVar3 = *(uint *)(*(int *)(param_1 + 0x68) + 0x18);
            if (local_48 != uVar3 * (local_48 / uVar3)) {
              FUN_004d09b4(DAT_004cd554,DAT_004cd36c,0x824);
            }
            FUN_004cadc6(param_2);
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
joined_r0x004cc8e8:
    if (uVar3 != 0xffffffac) {
      return uVar3;
    }
  } while( true );
}

