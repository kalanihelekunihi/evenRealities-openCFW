
char FUN_0049048c(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  char cVar2;
  int iVar3;
  int *piVar4;
  undefined4 uVar5;
  undefined1 auStack_28 [8];
  int local_20;
  undefined4 uStack_18;
  
  cVar2 = '\x01';
  bVar1 = false;
  uStack_18 = param_4;
  iVar3 = FUN_0048f77e(param_1,auStack_28);
  if (iVar3 == 0) {
    cVar2 = '\0';
  }
  else if (*(int *)(param_2 + 0x24) == 0) {
    uVar5 = DAT_004905d8;
    if (*(int *)(param_1 + 0xc) != 0) {
      uVar5 = *(undefined4 *)(param_1 + 0xc);
    }
    *(undefined4 *)(param_1 + 0xc) = uVar5;
    cVar2 = '\0';
  }
  else {
    if (((*(byte *)(param_2 + 0x16) & 0xf) == 9) && (*(int *)(param_2 + 0x20) != 0)) {
      piVar4 = (int *)(*(int *)(param_2 + 0x20) + -8);
      if ((*piVar4 != 0) &&
         (cVar2 = (*(code *)*piVar4)(auStack_28,param_2,*(int *)(param_2 + 0x20) + -4),
         local_20 == 0)) {
        bVar1 = true;
      }
    }
    if ((cVar2 != '\0') && (!bVar1)) {
      uVar5 = 0;
      if (((*(byte *)(param_2 + 0x16) & 0xc0) == 0) && ((*(byte *)(param_2 + 0x16) & 0x30) != 0x20))
      {
        uVar5 = 1;
      }
      cVar2 = FUN_0048fe98(auStack_28,*(undefined4 *)(param_2 + 0x24),
                           *(undefined4 *)(param_2 + 0x1c),uVar5);
    }
    iVar3 = FUN_0048f7ca(param_1,auStack_28);
    if (iVar3 == 0) {
      cVar2 = '\0';
    }
  }
  return cVar2;
}

