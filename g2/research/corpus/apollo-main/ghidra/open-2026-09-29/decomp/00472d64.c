
void FUN_00472d64(int param_1,int param_2)

{
  bool bVar1;
  
  if (param_2 < 0) {
    bVar1 = param_1 != 0;
    param_1 = -param_1;
    param_2 = -param_2 - (uint)bVar1;
  }
  FUN_00472d40(param_1,param_2);
  return;
}

