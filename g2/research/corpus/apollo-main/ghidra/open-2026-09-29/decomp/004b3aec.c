
void FUN_004b3aec(undefined2 *param_1,int param_2)

{
  undefined2 uVar1;
  int iVar2;
  short *psVar3;
  uint uVar4;
  byte bVar5;
  
  if ((*(char *)(param_2 + 6) != '\0') && (*(char *)(param_1 + 2) != '\0')) {
    *(undefined1 *)(param_2 + 5) = 1;
    *(undefined1 *)(param_2 + 6) = 0;
  }
  if (*DAT_004b43f8 != '\0') {
    uVar1 = *param_1;
    iVar2 = FUN_004bb07c((char)uVar1,0);
    psVar3 = (short *)(iVar2 + 0x6c);
    if (psVar3 != (short *)0x0) {
      bVar5 = 0;
      while( true ) {
        uVar4 = AttsGetCccTableLen();
        if (uVar4 <= bVar5) break;
        if (*psVar3 != 0) {
          AttsCccSet((char)uVar1,bVar5,*psVar3);
        }
        bVar5 = bVar5 + 1;
        psVar3 = psVar3 + 1;
      }
    }
  }
  return;
}

