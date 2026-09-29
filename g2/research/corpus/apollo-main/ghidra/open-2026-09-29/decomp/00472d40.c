
int FUN_00472d40(int param_1,int param_2)

{
  int iVar1;
  longlong lVar2;
  
  lVar2 = CONCAT44(param_2,param_1);
  if ((param_2 == 0) && (param_1 == 0)) {
    iVar1 = 1;
  }
  else {
    iVar1 = 0;
    lVar2 = CONCAT44(param_2,param_1);
  }
  while (lVar2 != 0) {
    lVar2 = FUN_00472c84();
    iVar1 = iVar1 + 1;
  }
  return iVar1;
}

