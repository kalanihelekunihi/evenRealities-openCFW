
int FUN_004ce1a0(int param_1,int param_2,int param_3,int param_4)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 local_20;
  
  iVar4 = param_4;
  if (((*(int *)(param_2 + 0x30) << 0xb < 0) &&
      (uVar1 = lfs_max(param_4 + *(int *)(param_2 + 0x34),*(undefined4 *)(param_2 + 0x2c)),
      *(uint *)(param_1 + 0x7c) < uVar1)) && (iVar2 = FUN_004cde2c(param_1,param_2), iVar2 != 0)) {
    *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) | 0x80000;
    param_4 = iVar2;
  }
  else {
    for (; iVar4 != 0; iVar4 = iVar4 - iVar2) {
      if ((-1 < *(int *)(param_2 + 0x30) << 0xe) ||
         (*(int *)(param_2 + 0x3c) == *(int *)(*(int *)(param_1 + 0x68) + 0x1c))) {
        if (*(int *)(param_2 + 0x30) << 0xb < 0) {
          *(undefined4 *)(param_2 + 0x38) = 0xfffffffe;
          *(undefined4 *)(param_2 + 0x3c) = *(undefined4 *)(param_2 + 0x34);
        }
        else {
          if ((-1 < *(int *)(param_2 + 0x30) << 0xe) && (*(int *)(param_2 + 0x34) != 0)) {
            local_20 = 0;
            iVar2 = FUN_004cd728(param_1,0,param_2 + 0x40,*(undefined4 *)(param_2 + 0x28),
                                 *(undefined4 *)(param_2 + 0x2c),*(int *)(param_2 + 0x34) + -1,
                                 param_2 + 0x38,&local_20);
            if (iVar2 != 0) {
              *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) | 0x80000;
              return iVar2;
            }
            FUN_004ca822(param_1,param_2 + 0x40);
          }
          lfs_alloc_ckpoint(param_1);
          iVar2 = FUN_004cd7d2(param_1,param_2 + 0x40,param_1,*(undefined4 *)(param_2 + 0x38),
                               *(undefined4 *)(param_2 + 0x34),param_2 + 0x38,param_2 + 0x3c);
          if (iVar2 != 0) {
            *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) | 0x80000;
            return iVar2;
          }
        }
        *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) | 0x20000;
      }
      iVar2 = lfs_min(iVar4,*(int *)(*(int *)(param_1 + 0x68) + 0x1c) - *(int *)(param_2 + 0x3c));
      while (iVar3 = FUN_004cac04(param_1,param_2 + 0x40,param_1,1,*(undefined4 *)(param_2 + 0x38),
                                  *(undefined4 *)(param_2 + 0x3c),param_3,iVar2), iVar3 != 0) {
        if (iVar3 != -0x54) {
          *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) | 0x80000;
          return iVar3;
        }
        iVar3 = FUN_004cdd0e(param_1,param_2);
        if (iVar3 != 0) {
          *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) | 0x80000;
          return iVar3;
        }
      }
      *(int *)(param_2 + 0x34) = iVar2 + *(int *)(param_2 + 0x34);
      *(int *)(param_2 + 0x3c) = iVar2 + *(int *)(param_2 + 0x3c);
      param_3 = param_3 + iVar2;
      lfs_alloc_ckpoint(param_1);
    }
  }
  return param_4;
}

