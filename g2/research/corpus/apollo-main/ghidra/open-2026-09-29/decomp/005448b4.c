
char FUN_005448b4(int param_1,int param_2,undefined1 *param_3,char param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined1 auStack_70 [4];
  undefined1 auStack_6c [88];
  
  FUN_0048949c(auStack_6c,0x58);
  if (param_3 == (undefined1 *)0x0) {
    iVar2 = FUN_0054449a(param_1,param_2,auStack_6c);
    if (iVar2 == 0) {
      return '\x05';
    }
    param_3 = auStack_6c;
  }
  if (param_4 == '\0') {
    cVar1 = FUN_005858d8(param_1,*(undefined4 *)(param_3 + 0x50),auStack_70,6,3,0);
    *(undefined1 *)(param_1 + 0xa4) = 1;
  }
  else {
    cVar1 = FUN_005858d8(param_1,*(undefined4 *)(param_3 + 0x50),auStack_70,6,4,1);
    if ((*(char *)(param_1 + 0xa4) == '\0') && (cVar1 == '\0')) {
      if (param_2 == 0) {
        if (param_3 != (undefined1 *)0x0) {
          FUN_00543d1c(param_1,param_3 + 0x10,param_3[2],0xffffffff);
        }
      }
      else {
        uVar3 = FUN_0044a43c(param_2);
        FUN_00543d1c(param_1,param_2,uVar3,0xffffffff);
      }
    }
    *(undefined1 *)(param_1 + 0xa4) = 0;
  }
  iVar2 = *(int *)(param_1 + 0xc) * (*(uint *)(param_3 + 0x50) / *(uint *)(param_1 + 0xc)) + 1;
  if ((cVar1 == '\0') && (iVar4 = FUN_00585948(param_1,iVar2,auStack_70,4), iVar4 == 1)) {
    cVar1 = FUN_005858d8(param_1,iVar2,auStack_70,4,2,1);
    iVar2 = FUN_00543cc0(param_1,*(int *)(param_1 + 0xc) *
                                 (*(uint *)(param_3 + 0x50) / *(uint *)(param_1 + 0xc)));
    if (iVar2 != 0) {
      *(undefined1 *)(iVar2 + 2) = 2;
    }
  }
  return cVar1;
}

