
void WStrReverseCpy(int param_1,int param_2,ushort param_3)

{
  short sVar1;
  
  for (sVar1 = 0; (int)sVar1 < (int)(uint)param_3; sVar1 = sVar1 + 1) {
    *(undefined1 *)(param_1 + ((param_3 - 1) - (int)sVar1)) = *(undefined1 *)(param_2 + sVar1);
  }
  return;
}

