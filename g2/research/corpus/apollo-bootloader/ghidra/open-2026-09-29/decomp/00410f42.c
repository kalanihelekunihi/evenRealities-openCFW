
int FUN_00410f42(int param_1,undefined4 *param_2,uint param_3,int param_4,int param_5,int param_6,
                int param_7)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uVar5;
  int iVar6;
  uint uVar7;
  uint local_30;
  int local_2c;
  int iStack_28;
  
  uVar7 = param_2[3];
  local_30 = param_2[4];
  iVar6 = 0;
  iStack_28 = param_4;
  iVar1 = FUN_00410c64(param_1 + 0x3c,param_2);
  if ((iVar1 != 0) && (iVar1 = lfs_tag_id(param_3), iVar1 != 0)) {
    uVar2 = lfs_tag_id(*(undefined4 *)(param_1 + 0x3c));
    uVar3 = lfs_tag_id(param_4);
    if ((uVar2 & 0xffff) == uVar3) {
      return -2;
    }
    uVar2 = lfs_tag_id(*(undefined4 *)(param_1 + 0x3c));
    uVar3 = lfs_tag_id(param_4);
    if ((uVar2 & 0xffff) < uVar3) {
      iVar6 = -0x400;
    }
  }
  do {
    iVar1 = FUN_00410bc6(local_30);
    if (uVar7 < iVar1 + 4U) {
      return -2;
    }
    iVar1 = FUN_00410bc6(local_30);
    uVar2 = local_30;
    uVar7 = uVar7 - iVar1;
    iVar1 = FUN_00410544(param_1,0,param_1,4,*param_2,uVar7,&local_30,4);
    if (iVar1 != 0) {
      return iVar1;
    }
    uVar3 = lfs_frombe32(local_30);
    local_30 = (uVar3 ^ uVar2) & 0x7fffffff;
    iVar1 = lfs_tag_id(param_3);
    if ((iVar1 != 0) && (iVar1 = lfs_tag_type1(uVar2), iVar1 == 0x400)) {
      uVar3 = lfs_tag_id(param_4 - iVar6);
      uVar4 = lfs_tag_id(uVar2);
      if (uVar4 <= (uVar3 & 0xffff)) {
        if (uVar2 == (param_4 - iVar6 & DAT_00411c40 | DAT_00411c44)) {
          return -2;
        }
        iVar1 = FUN_00410bae(uVar2);
        iVar6 = iVar6 + iVar1 * 0x400;
      }
    }
  } while ((uVar2 & param_3) != (param_4 - iVar6 & param_3));
  iVar1 = FUN_00410b7c(uVar2);
  if (iVar1 == 0) {
    uVar5 = FUN_00410bc0(uVar2);
    local_2c = lfs_min(uVar5,param_7);
    iVar1 = FUN_00410544(param_1,0,param_1,local_2c,*param_2,param_5 + uVar7 + 4,param_6,local_2c);
    if (iVar1 == 0) {
      FUN_0041560c(param_6 + local_2c,param_7 - local_2c,0);
      iVar1 = iVar6 + uVar2;
    }
  }
  else {
    iVar1 = -2;
  }
  return iVar1;
}

