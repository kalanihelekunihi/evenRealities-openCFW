
undefined8
FUN_004ca83c(int param_1,uint *param_2,uint *param_3,uint param_4,uint param_5,uint param_6,
            int param_7,uint param_8)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint *local_30;
  
  local_30 = param_2;
  if ((*(uint *)(*(int *)(param_1 + 0x68) + 0x1c) < param_8 + param_6) ||
     ((*(int *)(param_1 + 0x6c) != 0 && (*(uint *)(param_1 + 0x6c) <= param_5)))) {
    iVar1 = -0x54;
  }
  else {
LAB_004ca8a0:
    do {
      if (param_8 == 0) {
        iVar1 = 0;
        break;
      }
      uVar2 = param_8;
      if (((param_2 != (uint *)0x0) && (param_5 == *param_2)) && (param_6 < param_2[2] + param_2[1])
         ) {
        if (param_2[1] <= param_6) {
          iVar1 = lfs_min(param_8,param_2[1] + (param_2[2] - param_6));
          FUN_00439be4(param_7,(param_6 - param_2[1]) + param_2[3],iVar1);
          param_7 = param_7 + iVar1;
          param_6 = iVar1 + param_6;
          param_8 = param_8 - iVar1;
          goto LAB_004ca8a0;
        }
        uVar2 = lfs_min(param_8,param_2[1] - param_6);
      }
      if ((param_5 == *param_3) && (param_6 < param_3[2] + param_3[1])) {
        if (param_3[1] <= param_6) {
          iVar1 = lfs_min(uVar2,param_3[1] + (param_3[2] - param_6));
          FUN_00439be4(param_7,(param_6 - param_3[1]) + param_3[3],iVar1);
          param_7 = param_7 + iVar1;
          param_6 = iVar1 + param_6;
          param_8 = param_8 - iVar1;
          goto LAB_004ca8a0;
        }
        uVar2 = lfs_min(uVar2,param_3[1] - param_6);
      }
      if (((param_4 <= param_8) &&
          (uVar4 = *(uint *)(*(int *)(param_1 + 0x68) + 0x14), param_6 == uVar4 * (param_6 / uVar4))
          ) && (*(uint *)(*(int *)(param_1 + 0x68) + 0x14) <= param_8)) {
        local_30 = (uint *)lfs_aligndown(uVar2,*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x14));
        iVar1 = (**(code **)(*(int *)(param_1 + 0x68) + 4))
                          (*(undefined4 *)(param_1 + 0x68),param_5,param_6,param_7);
        if (iVar1 != 0) break;
        param_7 = param_7 + (int)local_30;
        param_6 = (int)local_30 + param_6;
        param_8 = param_8 - (int)local_30;
        goto LAB_004ca8a0;
      }
      if ((*(int *)(param_1 + 0x6c) != 0) && (*(uint *)(param_1 + 0x6c) <= param_5)) {
        FUN_004d09b4(DAT_004cb598,DAT_004cb594,0x6b);
      }
      *param_3 = param_5;
      uVar2 = lfs_aligndown(param_6,*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x14));
      param_3[1] = uVar2;
      uVar3 = lfs_alignup(param_4 + param_6,*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x14));
      iVar1 = lfs_min(uVar3,*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x1c));
      uVar2 = lfs_min(iVar1 - param_3[1],*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x28));
      param_3[2] = uVar2;
      local_30 = (uint *)param_3[2];
      iVar1 = (**(code **)(*(int *)(param_1 + 0x68) + 4))
                        (*(undefined4 *)(param_1 + 0x68),*param_3,param_3[1],param_3[3]);
      if (0 < iVar1) {
        FUN_004d09b4(DAT_004cb59c,DAT_004cb594,0x76);
      }
    } while (iVar1 == 0);
  }
  return CONCAT44(local_30,iVar1);
}

