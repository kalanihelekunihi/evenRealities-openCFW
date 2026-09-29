
undefined4 FUN_00543cec(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = FUN_00543cc0(param_1);
  if (iVar1 != 0) {
    *(undefined4 *)(iVar1 + 0x14) = param_3;
    *(int *)(iVar1 + 0x10) =
         *(int *)(iVar1 + 4) + (*(int *)(param_1 + 0xc) - *(int *)(iVar1 + 0x14));
  }
  return param_4;
}

