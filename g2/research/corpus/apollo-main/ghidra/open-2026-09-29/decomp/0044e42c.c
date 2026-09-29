
byte FUN_0044e42c(int param_1)

{
  byte bVar1;
  
  if (*(int *)(param_1 + 8) == 0) {
    bVar1 = 3;
  }
  else {
    bVar1 = *(byte *)(*(int *)(param_1 + 8) + 0x32) & 3;
  }
  return bVar1;
}

