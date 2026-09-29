
char FUN_0044ea98(int param_1,int param_2,int param_3)

{
  char cVar1;
  
  if (param_3 == 0 && param_2 == 0) {
    cVar1 = '\x01';
  }
  else {
    FUN_0043e1fa(param_1);
    *(int *)(*(int *)(param_1 + 8) + 0x20) = param_2 + *(int *)(*(int *)(param_1 + 8) + 0x20);
    *(int *)(*(int *)(param_1 + 8) + 0x24) = param_3 + *(int *)(*(int *)(param_1 + 8) + 0x24);
    FUN_0044035e(param_1,param_2,param_3,1);
    cVar1 = FUN_00451670(param_1,0xf,0);
    if (cVar1 == '\x01') {
      FUN_00440656(param_1);
      cVar1 = '\x01';
    }
  }
  return cVar1;
}

