
char FUN_0044fdbe(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int local_30;
  int local_2c;
  undefined4 local_28;
  undefined4 local_20;
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  FUN_0044f7b4(&local_30,0x1c);
  local_30 = param_1;
  local_2c = param_1;
  local_28 = param_2;
  local_20 = param_3;
  cVar1 = FUN_0044ffe6(param_1 + 0x2e4,&local_30,1);
  if (cVar1 == '\x01') {
    cVar1 = FUN_0044ffe6(param_1 + 0x2e4,&local_30,0);
  }
  return cVar1;
}

