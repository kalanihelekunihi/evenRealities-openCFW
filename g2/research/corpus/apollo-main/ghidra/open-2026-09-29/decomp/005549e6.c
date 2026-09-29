
bool FUN_005549e6(undefined4 param_1,uint param_2,uint param_3,int param_4)

{
  bool bVar1;
  int iVar2;
  
  if ((param_3 < param_2) || (param_2 + 4 <= param_3)) {
    bVar1 = false;
  }
  else {
    iVar2 = FUN_00554968();
    bVar1 = (int)(((param_3 - param_2) * 10 + param_4) * 0x1c) <= iVar2;
  }
  return bVar1;
}

