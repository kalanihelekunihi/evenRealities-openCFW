
int FUN_004397fa(char *param_1)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  if (*param_1 == '\0') {
    iVar4 = 4;
  }
  else {
    iVar4 = 0;
  }
  uVar5 = iVar4 + *(int *)(param_1 + 0x34);
  if (*param_1 == '\0') {
    iVar4 = 3;
  }
  else {
    iVar4 = 0;
  }
  uVar1 = *(int *)(param_1 + 0x30) - iVar4;
  if (uVar1 < uVar5) {
    iVar4 = uVar5 - uVar1;
  }
  else {
    iVar4 = -(uVar1 - uVar5);
  }
  iVar2 = 0;
  for (uVar5 = *(uint *)(param_1 + 8);
      (((iVar3 = iVar2, uVar5 != 0 && (iVar3 = iVar2 + 1, uVar5 >> 1 != 0)) &&
       (iVar3 = iVar2 + 2, uVar5 >> 2 != 0)) && (iVar3 = iVar2 + 3, uVar5 >> 3 != 0));
      uVar5 = uVar5 >> 4) {
    iVar2 = iVar2 + 4;
  }
  return iVar3 + ((iVar4 * 8 - *(int *)(param_1 + 0x20)) - *(int *)(param_1 + 0x24)) + -0x1a +
         (*(int *)(param_1 + 0x14) - ((int)~*(uint *)(param_1 + 0xc) >> 0x1f)) * -8;
}

