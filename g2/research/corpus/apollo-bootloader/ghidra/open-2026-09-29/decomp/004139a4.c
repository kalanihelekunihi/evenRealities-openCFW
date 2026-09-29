
int FUN_004139a4(int *param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined *local_68;
  undefined1 auStack_64 [40];
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_30;
  undefined1 auStack_24 [20];
  
  if (*(int *)(param_2 + 0x30) << 0xd < 0) {
    if (-1 < *(int *)(param_2 + 0x30) << 0xb) {
      FUN_00410522(param_1,param_2 + 0x40);
    }
    *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) & 0xfffbffff;
  }
  if (*(int *)(param_2 + 0x30) << 0xe < 0) {
    uVar3 = *(undefined4 *)(param_2 + 0x34);
    if (*(int *)(param_2 + 0x30) << 0xb < 0) {
      uVar2 = lfs_max(*(undefined4 *)(param_2 + 0x34),*(undefined4 *)(param_2 + 0x2c));
      *(undefined4 *)(param_2 + 0x34) = uVar2;
    }
    else {
      FUN_004156ac(auStack_64,DAT_00413fec,0x54);
      local_3c = *(undefined4 *)(param_2 + 0x28);
      local_38 = *(undefined4 *)(param_2 + 0x2c);
      local_30 = *(undefined4 *)(param_2 + 0x34);
      FUN_004156ac(auStack_24,param_1,0x10);
      FUN_00410522(param_1,param_1);
      while (*(uint *)(param_2 + 0x34) < *(uint *)(param_2 + 0x2c)) {
        iVar1 = FUN_00413b92(param_1,auStack_64,&local_68,1);
        if (iVar1 < 0) {
          return iVar1;
        }
        iVar1 = FUN_00413cf0(param_1,param_2,&local_68,1);
        if (iVar1 < 0) {
          return iVar1;
        }
        if (*param_1 != -1) {
          FUN_00410522(param_1,auStack_24);
          FUN_00410522(param_1,param_1);
        }
      }
      while (iVar1 = FUN_00410802(param_1,param_2 + 0x40,param_1,1), iVar1 != 0) {
        if (iVar1 != -0x54) {
          return iVar1;
        }
        local_68 = &DAT_00413ab0;
        FUN_00415fae(DAT_00413fe4,DAT_00413f04,0xd50,*(undefined4 *)(param_2 + 0x38));
        iVar1 = FUN_0041385e(param_1,param_2);
        if (iVar1 != 0) {
          return iVar1;
        }
      }
    }
    *(undefined4 *)(param_2 + 0x28) = *(undefined4 *)(param_2 + 0x38);
    *(undefined4 *)(param_2 + 0x2c) = *(undefined4 *)(param_2 + 0x34);
    *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) & 0xfffdffff;
    *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) | 0x10000;
    *(undefined4 *)(param_2 + 0x34) = uVar3;
  }
  return 0;
}

