
int FUN_0046cacc(byte *param_1,byte *param_2)

{
  byte bVar1;
  uint uVar2;
  
  do {
    uVar2 = (uint)*param_1;
    bVar1 = *param_2;
    if (uVar2 == 0) break;
    param_1 = param_1 + 1;
    param_2 = param_2 + 1;
  } while (uVar2 == bVar1);
  return uVar2 - bVar1;
}

