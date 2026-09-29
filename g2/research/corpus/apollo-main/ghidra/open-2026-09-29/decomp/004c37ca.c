
char FUN_004c37ca(byte param_1)

{
  char cVar1;
  byte bVar2;
  char cVar3;
  
  cVar3 = '\0';
  for (bVar2 = 0; bVar2 < 2; bVar2 = bVar2 + 1) {
    cVar1 = FUN_004c3750(*(undefined4 *)(DAT_004c43dc + (uint)param_1 * 8 + (uint)bVar2 * 4));
    cVar3 = cVar1 + cVar3;
  }
  return cVar3;
}

