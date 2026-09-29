
char FUN_004215fe(byte param_1)

{
  char cVar1;
  byte bVar2;
  char cVar3;
  
  cVar3 = '\0';
  for (bVar2 = 0; bVar2 < 2; bVar2 = bVar2 + 1) {
    cVar1 = FUN_00421584(*(undefined4 *)(DAT_00422210 + (uint)param_1 * 8 + (uint)bVar2 * 4));
    cVar3 = cVar1 + cVar3;
  }
  return cVar3;
}

