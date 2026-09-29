
int FUN_00412784(int param_1,undefined4 *param_2,undefined4 *param_3,undefined4 *param_4,int param_5
                ,int param_6)

{
  bool bVar1;
  byte bVar2;
  ushort uVar3;
  short sVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  undefined4 *puVar8;
  int iVar9;
  undefined4 *local_68;
  int local_64;
  uint local_60;
  undefined4 local_5c;
  undefined4 local_58;
  undefined4 local_54;
  undefined4 local_50;
  undefined4 local_4c;
  int *local_48;
  undefined4 local_44;
  uint local_40;
  undefined4 local_3c;
  undefined4 local_34;
  int local_30;
  int local_2c;
  undefined4 *local_28;
  
  iVar7 = 0;
  bVar1 = false;
  for (iVar9 = 0; iVar9 < param_5; iVar9 = iVar9 + 1) {
    iVar5 = lfs_tag_type3(param_4[iVar9 * 2]);
    if (iVar5 == 0x401) {
      *(short *)(param_2 + 5) = *(short *)(param_2 + 5) + 1;
    }
    else {
      iVar5 = lfs_tag_type3(param_4[iVar9 * 2]);
      if (iVar5 == 0x4ff) {
        if (*(short *)(param_2 + 5) == 0) {
          FUN_00415734(DAT_00413228,DAT_00412f70,0x8c8);
        }
        *(short *)(param_2 + 5) = *(short *)(param_2 + 5) + -1;
        bVar1 = true;
      }
      else {
        iVar5 = lfs_tag_type1(param_4[iVar9 * 2]);
        if (iVar5 == 0x600) {
          param_2[6] = *(undefined4 *)param_4[iVar9 * 2 + 1];
          param_2[7] = *(undefined4 *)(param_4[iVar9 * 2 + 1] + 4);
          bVar2 = lfs_tag_chunk(param_4[iVar9 * 2]);
          *(byte *)((int)param_2 + 0x17) = bVar2 & 1;
          FUN_00410b46(param_2 + 6);
        }
      }
    }
  }
  if ((bVar1) && (*(short *)(param_2 + 5) == 0)) {
    if (param_6 == 0) {
      FUN_00415734(DAT_0041322c,DAT_00412f70,0x8d5);
    }
    iVar9 = FUN_00414ada(param_1,param_2,param_6);
    if ((iVar9 != 0) && (iVar9 != -2)) {
      return iVar9;
    }
    if ((iVar9 != -2) && (*(char *)(param_6 + 0x17) != '\0')) {
      iVar7 = 2;
      goto LAB_00412a26;
    }
  }
  if (*(char *)((int)param_2 + 0x16) != '\0') {
    FUN_004156ac(&local_44,DAT_00413230,0x18);
    local_44 = *param_2;
    local_40 = param_2[3];
    local_3c = param_2[4];
    local_34 = param_2[3];
    if (*(int *)(*(int *)(param_1 + 0x68) + 0x4c) == 0) {
      local_30 = *(int *)(*(int *)(param_1 + 0x68) + 0x1c);
    }
    else {
      local_30 = *(int *)(*(int *)(param_1 + 0x68) + 0x4c);
    }
    local_30 = local_30 + -8;
    FUN_00410b5c(param_2 + 6);
    local_28 = &local_44;
    local_48 = &local_2c;
    local_4c = DAT_00412f80;
    local_50 = 0;
    local_54 = 0;
    local_58 = 0;
    local_5c = 0;
    local_60 = 0;
    local_64 = param_5;
    local_68 = param_4;
    local_2c = param_1;
    iVar9 = FUN_004112b4(param_1,param_2,param_2[3],param_2[4]);
    FUN_00410b46(param_2 + 6);
    if (iVar9 == 0) {
      FUN_0041560c(&local_68,0xc,0);
      FUN_00410bdc(&local_68,param_1 + 0x30);
      FUN_00410bdc(&local_68,param_1 + 0x3c);
      FUN_00410bdc(&local_68,param_1 + 0x48);
      local_68 = (undefined4 *)((uint)local_68 & 0xfffffc00);
      iVar9 = FUN_00410bfa(&local_68);
      if (iVar9 == 0) {
        iVar9 = FUN_00411c04(param_1,param_2,&local_68);
        if (iVar9 != 0) {
          return iVar9;
        }
        FUN_00410ca8(&local_68);
        iVar9 = FUN_00411e9c(param_1,&local_44,DAT_00413154,&local_68);
        if (iVar9 != 0) goto joined_r0x004129b0;
      }
      iVar9 = FUN_00411f52(param_1,&local_44);
      if (iVar9 == 0) {
        uVar6 = *(uint *)(*(int *)(param_1 + 0x68) + 0x18);
        if (local_40 != uVar6 * (local_40 / uVar6)) {
          FUN_00415734(DAT_00413158,DAT_00412f70,0x91f);
        }
        param_2[3] = local_40;
        param_2[4] = local_3c;
        *(undefined4 *)(param_1 + 0x3c) = *(undefined4 *)(param_1 + 0x30);
        *(undefined4 *)(param_1 + 0x40) = *(undefined4 *)(param_1 + 0x34);
        *(undefined4 *)(param_1 + 0x44) = *(undefined4 *)(param_1 + 0x38);
        *(undefined4 *)(param_1 + 0x48) = 0;
        *(undefined4 *)(param_1 + 0x4c) = 0;
        *(undefined4 *)(param_1 + 0x50) = 0;
        goto LAB_00412a26;
      }
    }
joined_r0x004129b0:
    if ((iVar9 != -0x1c) && (iVar9 != -0x54)) {
      return iVar9;
    }
  }
  FUN_00410522(param_1,param_1 + 0x10);
  local_60 = (uint)*(ushort *)(param_2 + 5);
  local_64 = 0;
  local_68 = param_2;
  iVar7 = FUN_004125a8(param_1,param_2,param_4,param_5);
  if (iVar7 < 0) {
    return iVar7;
  }
LAB_00412a26:
  local_5c = *param_3;
  local_58 = param_3[1];
  puVar8 = *(undefined4 **)(param_1 + 0x28);
  local_68 = param_3;
  do {
    if (puVar8 == (undefined4 *)0x0) {
      return iVar7;
    }
    iVar9 = FUN_00410af2(puVar8 + 2,&local_5c);
    if (iVar9 == 0) {
      FUN_004156ac(puVar8 + 2,param_2,0x20);
      if (puVar8 + 2 != local_68) {
        for (iVar9 = 0; iVar9 < param_5; iVar9 = iVar9 + 1) {
          iVar5 = lfs_tag_type3(param_4[iVar9 * 2]);
          if ((iVar5 == 0x4ff) &&
             (sVar4 = lfs_tag_id(param_4[iVar9 * 2]), *(short *)(puVar8 + 1) == sVar4)) {
            puVar8[2] = 0xffffffff;
            puVar8[3] = 0xffffffff;
          }
          else {
            iVar5 = lfs_tag_type3(param_4[iVar9 * 2]);
            if ((iVar5 == 0x4ff) &&
               (uVar3 = lfs_tag_id(param_4[iVar9 * 2]), uVar3 < *(ushort *)(puVar8 + 1))) {
              *(short *)(puVar8 + 1) = *(short *)(puVar8 + 1) + -1;
              if (*(char *)((int)puVar8 + 6) == '\x02') {
                puVar8[10] = puVar8[10] + -1;
              }
            }
            else {
              iVar5 = lfs_tag_type3(param_4[iVar9 * 2]);
              if (((iVar5 == 0x401) &&
                  (uVar3 = lfs_tag_id(param_4[iVar9 * 2]), uVar3 <= *(ushort *)(puVar8 + 1))) &&
                 (*(short *)(puVar8 + 1) = *(short *)(puVar8 + 1) + 1,
                 *(char *)((int)puVar8 + 6) == '\x02')) {
                puVar8[10] = puVar8[10] + 1;
              }
            }
          }
        }
      }
      while ((*(ushort *)(puVar8 + 7) <= *(ushort *)(puVar8 + 1) &&
             (*(char *)((int)puVar8 + 0x1f) != '\0'))) {
        iVar9 = FUN_00410af2(puVar8 + 8,param_1 + 0x20);
        if (iVar9 != 0) {
          *(short *)(puVar8 + 1) = *(short *)(puVar8 + 1) - *(short *)(puVar8 + 7);
        }
        iVar9 = FUN_00411be4(param_1,puVar8 + 2,puVar8 + 8);
        if (iVar9 != 0) {
          return iVar9;
        }
      }
    }
    puVar8 = (undefined4 *)*puVar8;
  } while( true );
}

