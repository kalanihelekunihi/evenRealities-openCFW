
void FUN_0055bb68(byte param_1,int param_2,int param_3)

{
  byte bVar1;
  byte bVar2;
  
  bVar1 = 0;
  bVar2 = 0;
  while ((bVar1 < 8 && (bVar2 < 2))) {
    if (((uint)param_1 & 1 << (uint)bVar1) != 0) {
      FUN_0055bb3a(1 << (uint)bVar1 & 0xff,*(undefined2 *)(param_2 + (uint)bVar2 * 2),
                   *(undefined2 *)(param_3 + (uint)bVar2 * 2));
      bVar2 = bVar2 + 1;
    }
    bVar1 = bVar1 + 1;
  }
  return;
}

