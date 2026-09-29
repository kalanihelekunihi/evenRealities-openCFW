
int FUN_0800ccc0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5)

{
  int iVar1;
  
  iVar1 = pvPortMalloc(0x2c);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 0x28) = 0;
    FUN_0800af30(param_1,param_2,param_3,param_4,param_5,iVar1);
  }
  return iVar1;
}

