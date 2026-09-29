
int FUN_005849a8(char *param_1)

{
  bool bVar1;
  char cVar2;
  
  cVar2 = '\0';
  bVar1 = false;
  for (; *param_1 != '\0'; param_1 = param_1 + 1) {
    if (*param_1 == ' ') {
      if (!bVar1) {
        cVar2 = cVar2 + '\x01';
        bVar1 = true;
      }
    }
    else {
      bVar1 = false;
    }
  }
  if (bVar1) {
    cVar2 = cVar2 + -1;
  }
  return (int)cVar2;
}

