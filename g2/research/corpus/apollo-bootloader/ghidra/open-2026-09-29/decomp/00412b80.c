
int FUN_00412b80(int param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined4 *puVar6;
  bool bVar7;
  undefined *local_a0;
  undefined *local_9c;
  char local_98;
  undefined *local_94;
  undefined *local_90;
  undefined *local_8c;
  undefined *local_88;
  byte local_75;
  undefined4 local_6c;
  undefined *local_68;
  uint local_4c;
  undefined4 *local_48;
  uint local_44 [2];
  uint local_3c;
  undefined4 *local_38;
  uint local_34 [2];
  int local_2c;
  undefined4 *local_28;
  
  for (puVar6 = *(undefined4 **)(param_1 + 0x28); puVar6 != (undefined4 *)0x0;
      puVar6 = (undefined4 *)*puVar6) {
    if ((((param_2 != puVar6 + 2) && (iVar3 = FUN_00410af2(puVar6 + 2,param_2), iVar3 == 0)) &&
        (*(char *)((int)puVar6 + 6) == '\x01')) &&
       (((int)(puVar6[0xc] << 0xb) < 0 &&
        (*(uint *)(*(int *)(param_1 + 0x68) + 0x28) < (uint)puVar6[0xb])))) {
      iVar3 = FUN_0041397c(param_1,puVar6);
      if (iVar3 != 0) {
        return iVar3;
      }
      iVar3 = FUN_004139a4(param_1,puVar6);
      if (iVar3 != 0) {
        return iVar3;
      }
    }
  }
  local_94 = (undefined *)*param_2;
  local_90 = (undefined *)param_2[1];
  FUN_004156ac(&local_6c,param_2,0x20);
  iVar3 = FUN_00412784(param_1,&local_6c,param_2,param_3,param_4,&local_8c);
  if (iVar3 < 0) {
    return iVar3;
  }
  iVar4 = FUN_00410af2(param_2,&local_94);
  if (iVar4 == 0) {
    FUN_004156ac(param_2,&local_6c,0x20);
  }
  if (iVar3 == 2) {
    iVar3 = FUN_00411c04(param_1,param_2,param_1 + 0x48);
    if (iVar3 != 0) {
      return iVar3;
    }
    local_94 = local_8c;
    local_90 = local_88;
    FUN_00410b5c(param_2 + 6);
    local_4c = DAT_00412f88 | (*(byte *)((int)param_2 + 0x17) + 0x600) * 0x100000;
    local_48 = param_2 + 6;
    iVar3 = FUN_00412784(param_1,&local_8c,&local_94,&local_4c,1,0);
    FUN_00410b46(param_2 + 6);
    if (iVar3 < 0) {
      return iVar3;
    }
    FUN_004156ac(&local_6c,&local_8c,0x20);
  }
  local_98 = '\0';
  do {
    while( true ) {
      uVar1 = DAT_00412f70;
      if (iVar3 != 1) {
        if (local_98 == '\0') {
          iVar3 = 0;
        }
        else {
          iVar3 = 3;
        }
        return iVar3;
      }
      local_9c = &DAT_00412f68;
      local_a0 = local_68;
      FUN_00415fae(DAT_00413828,DAT_00412f70,0x9ad,local_94,local_90,local_6c);
      iVar3 = 0;
      iVar4 = FUN_00410af2(&local_94,param_1 + 0x20);
      if (iVar4 == 0) {
        *(undefined4 *)(param_1 + 0x20) = local_6c;
        *(undefined **)(param_1 + 0x24) = local_68;
      }
      for (puVar6 = *(undefined4 **)(param_1 + 0x28); puVar6 != (undefined4 *)0x0;
          puVar6 = (undefined4 *)*puVar6) {
        iVar4 = FUN_00410af2(&local_94,puVar6 + 2);
        if (iVar4 == 0) {
          puVar6[2] = local_6c;
          puVar6[3] = local_68;
        }
        if ((*(char *)((int)puVar6 + 6) == '\x02') &&
           (iVar4 = FUN_00410af2(&local_94,puVar6 + 0xb), iVar4 == 0)) {
          puVar6[0xb] = local_6c;
          puVar6[0xc] = local_68;
        }
      }
      iVar4 = FUN_00414baa(param_1,&local_94,&local_8c);
      if ((iVar4 < 0) && (iVar4 != -2)) {
        return iVar4;
      }
      bVar7 = iVar4 != -2;
      if (iVar4 != -2) break;
LAB_00412e3c:
      iVar4 = FUN_00414ada(param_1,&local_94,&local_8c);
      if ((iVar4 != 0) && (iVar4 != -2)) {
        return iVar4;
      }
      if ((bVar7) && (iVar4 == -2)) {
        FUN_00415734(DAT_00413978,uVar1,0x9fb);
      }
      if (iVar4 != -2) {
        iVar3 = FUN_00410c14(param_1 + 0x30);
        if ((iVar3 != 0) && (iVar3 = FUN_00414c40(param_1,(int)(char)-bVar7), iVar3 != 0)) {
          return iVar3;
        }
        uVar2 = 0x3ff;
        iVar3 = FUN_00410c64(param_1 + 0x30,&local_8c);
        if (iVar3 != 0) {
          uVar2 = lfs_tag_id(*(undefined4 *)(param_1 + 0x30));
          local_a0 = &DAT_00412f68;
          FUN_00415fae(DAT_0041382c,uVar1,0xa0e,local_8c,local_88,uVar2);
          FUN_00414cbc(param_1,0x3ff,0);
        }
        local_94 = local_8c;
        local_90 = local_88;
        FUN_00410b5c(&local_6c);
        FUN_00415ff4(local_44,0x10);
        if (uVar2 == 0x3ff) {
          local_44[0] = 0;
        }
        else {
          local_44[0] = DAT_00413830 | (uint)uVar2 << 10;
        }
        local_3c = DAT_00412f88 | (local_75 + 0x600) * 0x100000;
        local_38 = &local_6c;
        iVar3 = FUN_00412784(param_1,&local_8c,&local_94,local_44,2,0);
        FUN_00410b46(&local_6c);
        if (iVar3 < 0) {
          return iVar3;
        }
        FUN_004156ac(&local_6c,&local_8c,0x20);
      }
    }
    iVar3 = FUN_00414c40(param_1,1);
    if (iVar3 != 0) {
      return iVar3;
    }
    uVar2 = 0x3ff;
    iVar3 = FUN_00410c64(param_1 + 0x30,&local_8c);
    if (iVar3 != 0) {
      uVar2 = lfs_tag_id(*(undefined4 *)(param_1 + 0x30));
      local_a0 = &DAT_00412f68;
      FUN_00415fae(DAT_0041382c,uVar1,0x9da,local_8c,local_88,uVar2);
      FUN_00414cbc(param_1,0x3ff,0);
      uVar5 = lfs_tag_id(iVar4);
      if (uVar2 < uVar5) {
        iVar4 = iVar4 + -0x400;
      }
    }
    local_a0 = local_8c;
    local_9c = local_88;
    FUN_00410b5c(&local_6c);
    FUN_00415ff4(local_34,0x10);
    if (uVar2 == 0x3ff) {
      local_34[0] = 0;
    }
    else {
      local_34[0] = DAT_00413830 | (uint)uVar2 << 10;
    }
    local_28 = &local_6c;
    local_2c = iVar4;
    iVar3 = FUN_00412784(param_1,&local_8c,&local_a0,local_34,2,0);
    FUN_00410b46(&local_6c);
    if (iVar3 < 0) {
      return iVar3;
    }
    if (iVar3 != 1) goto LAB_00412e3c;
    local_94 = local_a0;
    local_90 = local_9c;
    FUN_004156ac(&local_6c,&local_8c,0x20);
    local_98 = '\x01';
  } while( true );
}

