
undefined4 FUN_0048fc88(int param_1,undefined4 param_2,undefined1 param_3,undefined4 *param_4)

{
  char cVar1;
  int iVar2;
  
  iVar2 = *(int *)(param_1 + 8);
  while( true ) {
    if ((param_4 == (undefined4 *)0x0) || (iVar2 != *(int *)(param_1 + 8))) {
      return 1;
    }
    if (*(int *)*param_4 == 0) {
      cVar1 = FUN_0048fc26(param_1,param_4,param_2,param_3);
    }
    else {
      cVar1 = (**(code **)*param_4)(param_1,param_4,param_2,param_3);
    }
    if (cVar1 == '\0') break;
    param_4 = (undefined4 *)param_4[2];
  }
  return 0;
}

