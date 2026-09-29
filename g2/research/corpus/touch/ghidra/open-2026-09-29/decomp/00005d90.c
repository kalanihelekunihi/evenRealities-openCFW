
uint touch_sub_2a90(undefined4 param_1,int *param_2)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  
  if (param_2 == (int *)0x0) {
    uVar2 = 1;
  }
  else {
    *(undefined4 *)(param_2[2] + 0x1c) = param_1;
    iVar3 = param_2[2];
    uVar1 = touch_sub_2a70();
    *(undefined4 *)(iVar3 + 0x20) = uVar1;
    uVar2 = *(uint *)(param_2[1] + 8) & 0x10;
    if ((*(uint *)(param_2[1] + 8) & 0x10) != 0) {
      *(uint *)(**(int **)(*param_2 + 8) + 0x70) =
           *(uint *)(**(int **)(*param_2 + 8) + 0x70) & 0xffff0000;
      *(uint *)(**(int **)(*param_2 + 8) + 0x70) =
           *(uint *)(**(int **)(*param_2 + 8) + 0x70) | *(uint *)(param_2[2] + 0x20);
      uVar2 = 0;
    }
  }
  return uVar2;
}

