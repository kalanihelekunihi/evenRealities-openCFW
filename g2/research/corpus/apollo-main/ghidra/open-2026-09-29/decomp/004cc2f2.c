
int FUN_004cc2f2(int param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  byte local_38 [4];
  int local_34;
  undefined4 local_30;
  undefined4 uStack_2c;
  undefined4 local_28;
  undefined4 local_24;
  
  uVar1 = lfs_min(param_2[1] + 0x14,*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x1c));
  uVar2 = lfs_alignup(uVar1,*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x18));
  iVar4 = 0;
  iVar5 = 0;
  while ((uint)param_2[1] < uVar2) {
    iVar3 = lfs_min((uVar2 - param_2[1]) + -4,0x3fe);
    uVar6 = param_2[1] + iVar3 + 4;
    if (uVar6 < uVar2) {
      uVar6 = lfs_min(uVar6,uVar2 - 0x14);
    }
    local_38[0] = 0xff;
    if ((uVar2 <= uVar6) &&
       (uVar6 <= (uint)(*(int *)(*(int *)(param_1 + 0x68) + 0x1c) -
                       *(int *)(*(int *)(param_1 + 0x68) + 0x18)))) {
      iVar3 = FUN_004ca83c(param_1,0,param_1,*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x18),
                           *param_2,uVar6,local_38,1);
      if ((iVar3 != 0) && (iVar3 != -0x54)) {
        return iVar3;
      }
      uStack_2c = *(undefined4 *)(DAT_004ccf70 + 4);
      local_30 = *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x18);
      iVar3 = FUN_004caa88(param_1,0,param_1,*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x18),
                           *param_2,uVar6,local_30,&uStack_2c);
      if ((iVar3 != 0) && (iVar3 != -0x54)) {
        return iVar3;
      }
      FUN_004cafd4(&local_30);
      iVar3 = FUN_004cc23c(param_1,param_2,DAT_004ccf74,&local_30);
      if (iVar3 != 0) {
        return iVar3;
      }
    }
    uVar7 = (uVar6 - param_2[1]) - 4 | (((~(uint)local_38[0] & 0xff) >> 7) + 0x500) * 0x100000 |
            0xffc00;
    local_28 = lfs_tobe32(param_2[2] ^ uVar7);
    uVar1 = FUN_00541af8(param_2[3],&local_28,4);
    param_2[3] = uVar1;
    local_24 = lfs_tole32(param_2[3]);
    iVar3 = FUN_004cac04(param_1,param_1 + 0x10,param_1,0,*param_2,param_2[1],&local_28,8);
    if (iVar3 != 0) {
      return iVar3;
    }
    if (iVar4 == 0) {
      iVar4 = param_2[1] + 4;
      iVar5 = param_2[3];
    }
    param_2[1] = uVar6;
    param_2[2] = (~(uint)local_38[0] & 0x80) << 0x18 ^ uVar7;
    param_2[3] = 0xffffffff;
    if (((uVar2 <= uVar6) ||
        ((uint)(*(int *)(*(int *)(param_1 + 0x68) + 0x28) + *(int *)(param_1 + 0x14)) <= uVar6)) &&
       (iVar3 = FUN_004cabbc(param_1,param_1 + 0x10,param_1,0), iVar3 != 0)) {
      return iVar3;
    }
  }
  local_34 = -1;
  iVar3 = FUN_004caa88(param_1,0,param_1,iVar4 + 4,*param_2,param_2[4],iVar4 - param_2[4],&local_34)
  ;
  if (iVar3 != 0) {
    return iVar3;
  }
  if (local_34 != iVar5) {
    return -0x54;
  }
  iVar4 = FUN_004caa88(param_1,0,param_1,4,*param_2,iVar4,4,&local_34);
  if (iVar4 != 0) {
    return iVar4;
  }
  if (local_34 != 0) {
    return -0x54;
  }
  return 0;
}

