
bool FUN_0050b168(int param_1)

{
  bool bVar1;
  
  if (param_1 == 0) {
    bVar1 = true;
  }
  else {
    bVar1 = *(short *)(param_1 + 4) == 0;
  }
  return bVar1;
}

