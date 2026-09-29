
void WStrReverse(int param_1,byte param_2)

{
  undefined1 uVar1;
  byte bVar2;
  
  for (bVar2 = 0; bVar2 < param_2 >> 1; bVar2 = bVar2 + 1) {
    uVar1 = *(undefined1 *)(param_1 + ((uint)param_2 - (uint)bVar2) + -1);
    *(undefined1 *)(param_1 + ((uint)param_2 - (uint)bVar2) + -1) =
         *(undefined1 *)(param_1 + (uint)bVar2);
    *(undefined1 *)(param_1 + (uint)bVar2) = uVar1;
  }
  return;
}

