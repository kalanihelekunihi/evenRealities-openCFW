
undefined4 FUN_00490aea(int param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  if ((*(int *)(*param_2 + 0xc) == 0) ||
     (iVar1 = (**(code **)(*param_2 + 0xc))(0,param_1), iVar1 != 0)) {
    uVar2 = 1;
  }
  else {
    uVar2 = DAT_004910c4;
    if (*(int *)(param_1 + 0x10) != 0) {
      uVar2 = *(undefined4 *)(param_1 + 0x10);
    }
    *(undefined4 *)(param_1 + 0x10) = uVar2;
    uVar2 = 0;
  }
  return uVar2;
}

