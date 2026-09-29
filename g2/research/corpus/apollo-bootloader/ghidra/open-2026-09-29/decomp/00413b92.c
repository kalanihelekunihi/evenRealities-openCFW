
int FUN_00413b92(int param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  if (*(uint *)(param_2 + 0x34) < *(uint *)(param_2 + 0x2c)) {
    iVar1 = lfs_min(param_4,*(int *)(param_2 + 0x2c) - *(int *)(param_2 + 0x34));
    for (iVar4 = iVar1; iVar4 != 0; iVar4 = iVar4 - iVar3) {
      if ((-1 < *(int *)(param_2 + 0x30) << 0xd) ||
         (*(int *)(param_2 + 0x3c) == *(int *)(*(int *)(param_1 + 0x68) + 0x1c))) {
        if (*(int *)(param_2 + 0x30) << 0xb < 0) {
          *(undefined4 *)(param_2 + 0x38) = 0xfffffffe;
          *(undefined4 *)(param_2 + 0x3c) = *(undefined4 *)(param_2 + 0x34);
        }
        else {
          iVar3 = FUN_00413278(param_1,0,param_2 + 0x40,*(undefined4 *)(param_2 + 0x28),
                               *(undefined4 *)(param_2 + 0x2c),*(undefined4 *)(param_2 + 0x34),
                               param_2 + 0x38,param_2 + 0x3c);
          if (iVar3 != 0) {
            return iVar3;
          }
        }
        *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) | 0x40000;
      }
      iVar3 = lfs_min(iVar4,*(int *)(*(int *)(param_1 + 0x68) + 0x1c) - *(int *)(param_2 + 0x3c));
      if (*(int *)(param_2 + 0x30) << 0xb < 0) {
        iVar2 = FUN_004110f8(param_1,param_2 + 8,0,param_2 + 0x40,
                             *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x1c),DAT_00413fe8,
                             DAT_00413fd8 | (uint)*(ushort *)(param_2 + 4) << 10,
                             *(undefined4 *)(param_2 + 0x3c),param_3,iVar3,param_4);
      }
      else {
        iVar2 = FUN_00410544(param_1,0,param_2 + 0x40,
                             *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x1c),
                             *(undefined4 *)(param_2 + 0x38),*(undefined4 *)(param_2 + 0x3c),param_3
                             ,iVar3);
      }
      if (iVar2 != 0) {
        return iVar2;
      }
      *(int *)(param_2 + 0x34) = iVar3 + *(int *)(param_2 + 0x34);
      *(int *)(param_2 + 0x3c) = iVar3 + *(int *)(param_2 + 0x3c);
      param_3 = param_3 + iVar3;
    }
  }
  else {
    iVar1 = 0;
  }
  return iVar1;
}

