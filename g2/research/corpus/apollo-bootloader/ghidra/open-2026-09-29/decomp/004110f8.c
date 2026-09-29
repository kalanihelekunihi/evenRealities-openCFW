
int FUN_004110f8(int param_1,undefined4 param_2,int *param_3,int *param_4,int param_5,
                undefined4 param_6,undefined4 param_7,uint param_8,int param_9,int param_10)

{
  int iVar1;
  undefined4 uVar2;
  
  if (*(uint *)(*(int *)(param_1 + 0x68) + 0x1c) < param_10 + param_8) {
    iVar1 = -0x54;
  }
  else {
LAB_0041114e:
    do {
      if (param_10 == 0) {
        return 0;
      }
      iVar1 = param_10;
      if (((param_3 != (int *)0x0) && (*param_3 == -2)) &&
         (param_8 < (uint)(param_3[2] + param_3[1]))) {
        if ((uint)param_3[1] <= param_8) {
          iVar1 = lfs_min(param_10,param_3[1] + (param_3[2] - param_8));
          FUN_0041568c(param_9,(param_8 - param_3[1]) + param_3[3],iVar1);
          param_9 = param_9 + iVar1;
          param_8 = iVar1 + param_8;
          param_10 = param_10 - iVar1;
          goto LAB_0041114e;
        }
        iVar1 = lfs_min(param_10,param_3[1] - param_8);
      }
      if ((*param_4 == -2) && (param_8 < (uint)(param_4[2] + param_4[1]))) {
        if ((uint)param_4[1] <= param_8) {
          iVar1 = lfs_min(iVar1,param_4[1] + (param_4[2] - param_8));
          FUN_0041568c(param_9,(param_8 - param_4[1]) + param_4[3],iVar1);
          param_9 = param_9 + iVar1;
          param_8 = iVar1 + param_8;
          param_10 = param_10 - iVar1;
          goto LAB_0041114e;
        }
        lfs_min(iVar1,param_4[1] - param_8);
      }
      *param_4 = -2;
      iVar1 = lfs_aligndown(param_8,*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x14));
      param_4[1] = iVar1;
      uVar2 = lfs_alignup(param_5 + param_8,*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x14));
      iVar1 = lfs_min(uVar2,*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x28));
      param_4[2] = iVar1;
      iVar1 = FUN_00410f42(param_1,param_2,param_6,param_7,param_4[1],param_4[3],param_4[2]);
    } while (-1 < iVar1);
  }
  return iVar1;
}

