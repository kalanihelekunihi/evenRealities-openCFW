
void hciCoreCisFree(short param_1)

{
  char cVar1;
  short *psVar2;
  
  cVar1 = '\x06';
  psVar2 = DAT_0052ae20;
  while( true ) {
    if (cVar1 == '\0') {
      return;
    }
    if (*psVar2 == param_1) break;
    cVar1 = cVar1 + -1;
    psVar2 = psVar2 + 1;
  }
  *psVar2 = -1;
  return;
}

