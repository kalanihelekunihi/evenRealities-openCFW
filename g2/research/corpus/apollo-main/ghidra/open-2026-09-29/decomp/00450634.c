
undefined8 FUN_00450634(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0x400;
  iVar1 = FUN_004888b4(*(undefined4 *)(param_1 + 0x34),0,*(undefined4 *)(param_1 + 0x30),0,0x400,
                       param_4);
  return CONCAT44(uVar2,*(int *)(param_1 + 0x24) +
                        ((*(int *)(param_1 + 0x2c) - *(int *)(param_1 + 0x24)) * iVar1 >> 10));
}

