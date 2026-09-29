
void ui2a(uint param_1,int param_2)

{
  char *pcVar1;
  uint uVar2;
  char cVar3;
  uint uVar4;
  int iVar5;
  
  for (uVar2 = 1; (uint)*(byte *)(param_2 + 7) <= param_1 / uVar2;
      uVar2 = *(byte *)(param_2 + 7) * uVar2) {
  }
  iVar5 = 0;
  pcVar1 = *(char **)(param_2 + 0xc);
  while (uVar2 != 0) {
    uVar4 = param_1 / uVar2;
    param_1 = param_1 - uVar4 * uVar2;
    uVar2 = uVar2 / *(byte *)(param_2 + 7);
    if (((iVar5 != 0) || (0 < (int)uVar4)) || (uVar2 == 0)) {
      if ((int)uVar4 < 10) {
        cVar3 = '0';
      }
      else {
        cVar3 = 'W';
        if (*(char *)(param_2 + 8) != '\0') {
          cVar3 = '7';
        }
      }
      *pcVar1 = cVar3 + (char)uVar4;
      iVar5 = iVar5 + 1;
      pcVar1 = pcVar1 + 1;
    }
  }
  *pcVar1 = '\0';
  return;
}

