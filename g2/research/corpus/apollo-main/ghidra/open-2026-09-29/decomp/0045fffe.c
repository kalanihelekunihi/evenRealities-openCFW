
int FUN_0045fffe(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  
  iVar1 = param_1;
  if ((((*DAT_0046011c != 0) && (param_2 != 0xffff)) &&
      ((iVar2 = *DAT_0046011c, *(int *)(iVar2 + 4) == 0 ||
       (iVar1 = *(int *)(*(int *)(iVar2 + 4) + param_2 * 4), iVar1 == 0)))) &&
     (((iVar1 = param_1, iVar2 != *(int *)*DAT_00460120 &&
       (*(int *)(*(int *)*DAT_00460120 + 4) != 0)) &&
      (iVar2 = *(int *)(*(int *)(*(int *)*DAT_00460120 + 4) + param_2 * 4), iVar2 != 0)))) {
    iVar1 = iVar2;
  }
  return iVar1;
}

