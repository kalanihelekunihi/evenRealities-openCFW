
byte FUN_0044d5a4(int param_1)

{
  byte bVar1;
  
  if (param_1 == 0) {
    bVar1 = 0;
  }
  else {
    bVar1 = *(byte *)(param_1 + 0x1c) >> 1 & 1;
  }
  return bVar1;
}

