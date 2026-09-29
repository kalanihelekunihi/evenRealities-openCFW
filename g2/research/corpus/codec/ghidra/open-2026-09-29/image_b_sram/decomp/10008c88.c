
void FUN_10008c88(void)

{
  char cVar1;
  uint uVar2;
  char *pcVar3;
  int iVar4;
  char cVar5;
  uint in_stack_00000000;
  uint in_stack_00000008;
  uint in_stack_00000014;
  char local_30 [32];
  
  uVar2 = in_stack_00000014;
  if ((in_stack_00000000 != 0) ||
     (uVar2 = in_stack_00000014 & 0xffffffef, (in_stack_00000014 & 0x400) == 0)) {
    cVar5 = 'A';
    if ((uVar2 & 0x20) == 0) {
      cVar5 = 'a';
    }
    pcVar3 = local_30;
    iVar4 = 0x20;
    do {
      uVar2 = in_stack_00000000 / in_stack_00000008;
      in_stack_00000000 = in_stack_00000000 - uVar2 * in_stack_00000008;
      cVar1 = (char)in_stack_00000000;
      if ((in_stack_00000000 & 0xff) < 10) {
        cVar1 = cVar1 + '0';
      }
      else {
        cVar1 = cVar1 + cVar5 + -10;
      }
      *pcVar3 = cVar1;
      if (uVar2 == 0) break;
      pcVar3 = pcVar3 + 1;
      iVar4 = iVar4 + -1;
      in_stack_00000000 = uVar2;
    } while (iVar4 != 0);
  }
  FUN_10008aa0();
  return;
}

