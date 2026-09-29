
undefined8
FUN_00450a04(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5
            )

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = FUN_004888b4(*(undefined4 *)(param_1 + 0x34),0,*(undefined4 *)(param_1 + 0x30),0,0x400);
  iVar2 = FUN_0048869a(uVar1,param_2,param_3,param_4);
  return CONCAT44(param_5,*(int *)(param_1 + 0x24) +
                          ((*(int *)(param_1 + 0x2c) - *(int *)(param_1 + 0x24)) * iVar2 >> 10));
}

