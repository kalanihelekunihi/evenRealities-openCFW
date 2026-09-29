
void Ins_IF(int param_1,int *param_2)

{
  char cVar1;
  int iVar2;
  int iVar3;
  bool bVar4;
  
  if (*param_2 == 0) {
    iVar3 = 1;
    bVar4 = false;
    do {
      iVar2 = SkipCode(param_1);
      if (iVar2 == 1) {
        return;
      }
      cVar1 = *(char *)(param_1 + 0x174);
      if (cVar1 == '\x1b') {
        bVar4 = iVar3 == 1;
      }
      else if (cVar1 == 'X') {
        iVar3 = iVar3 + 1;
      }
      else if (cVar1 == 'Y') {
        iVar3 = iVar3 + -1;
        if (iVar3 == 0) {
          bVar4 = true;
        }
        else {
          bVar4 = false;
        }
      }
    } while (!bVar4);
  }
  return;
}

