
void FUN_00492114(int param_1,int param_2,uint param_3)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = 0;
  while (param_3 != 0) {
    uVar3 = param_3;
    if (0x400U - *(int *)(param_1 + 0x6424) < param_3) {
      uVar3 = 0x400 - *(int *)(param_1 + 0x6424);
    }
    iVar1 = FUN_00492032(*(int *)(param_1 + 0x6424) + param_1 + 0x6021,param_2 + iVar2,
                         uVar3 & 0xffff,param_1 + 0x642c);
    *(int *)(param_1 + 0x6424) = iVar1 + *(int *)(param_1 + 0x6424);
    param_3 = param_3 - uVar3;
    iVar2 = uVar3 + iVar2;
    if (*(int *)(param_1 + 0x6424) == 0x400) {
      FUN_004d9522(param_1,param_1 + 0x6021,*(undefined4 *)(param_1 + 0x6424));
      *(undefined4 *)(param_1 + 0x6424) = 0;
    }
  }
  return;
}

