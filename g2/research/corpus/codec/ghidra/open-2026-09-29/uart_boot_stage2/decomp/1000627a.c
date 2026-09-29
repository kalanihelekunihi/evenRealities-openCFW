
undefined4 FUN_1000627a(byte *param_1,byte *param_2)

{
  byte bVar1;
  undefined4 uVar2;
  
  do {
    bVar1 = *param_1;
    if (bVar1 != *param_2) {
      uVar2 = 0xffffffff;
      if (*param_2 <= bVar1) {
        uVar2 = 1;
      }
      return uVar2;
    }
    param_1 = param_1 + 1;
    param_2 = param_2 + 1;
  } while (bVar1 != 0);
  return 0;
}

