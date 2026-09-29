
uint touch_application_1904_process_three(int param_1)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  uVar5 = 0;
  iVar3 = 3;
  while (iVar4 = iVar3 + -1, iVar3 != 0) {
    iVar1 = touch_sub_4ade(iVar4,param_1);
    iVar3 = iVar4;
    if ((iVar1 != 0) && (*(char *)(*(int *)(param_1 + 0xc) + iVar4 * 0x90 + 0x7b) != '\a')) {
      uVar2 = touch_application_18a8_process(iVar4,param_1);
      uVar5 = uVar5 | uVar2;
    }
  }
  return uVar5;
}

