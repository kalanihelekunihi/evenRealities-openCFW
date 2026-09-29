
short * hciCoreCisByHandle(short param_1)

{
  short *psVar1;
  char cVar2;
  
  cVar2 = '\x06';
  psVar1 = DAT_0052ae20;
  while( true ) {
    if (cVar2 == '\0') {
      return (short *)0x0;
    }
    if (*psVar1 == param_1) break;
    cVar2 = cVar2 + -1;
    psVar1 = psVar1 + 1;
  }
  return psVar1;
}

