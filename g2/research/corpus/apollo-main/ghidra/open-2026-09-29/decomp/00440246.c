
void FUN_00440246(int param_1,int param_2,int param_3)

{
  char cVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  undefined1 auStack_38 [16];
  undefined1 auStack_28 [16];
  
  iVar4 = *(int *)(param_1 + 4);
  if (iVar4 != 0) {
    iVar3 = FUN_0043e0e0(param_1,0x40000);
    if (iVar3 == 0) {
      iVar3 = FUN_0044e486(iVar4);
      param_2 = (*(int *)(iVar4 + 0x14) + param_2) - iVar3;
      iVar3 = FUN_0044e498(iVar4);
      param_3 = (*(int *)(iVar4 + 0x18) + param_3) - iVar3;
    }
    else {
      param_2 = *(int *)(iVar4 + 0x14) + param_2;
      param_3 = *(int *)(iVar4 + 0x18) + param_3;
    }
    iVar3 = FUN_0043efc6(iVar4,0);
    param_2 = iVar3 + param_2;
    iVar3 = FUN_0043f022(iVar4,0);
    param_3 = iVar3 + param_3;
  }
  param_2 = param_2 - *(int *)(param_1 + 0x14);
  param_3 = param_3 - *(int *)(param_1 + 0x18);
  if ((param_2 != 0) || (param_3 != 0)) {
    FUN_00440656(param_1);
    FUN_0043fc2a(param_1,auStack_28);
    cVar1 = '\0';
    if (iVar4 != 0) {
      FUN_0043feca(iVar4,auStack_38);
      cVar1 = FUN_00450f28(auStack_28,auStack_38,0);
      if (cVar1 == '\0') {
        FUN_0044f2ca(iVar4);
      }
    }
    *(int *)(param_1 + 0x14) = param_2 + *(int *)(param_1 + 0x14);
    *(int *)(param_1 + 0x18) = param_3 + *(int *)(param_1 + 0x18);
    *(int *)(param_1 + 0x1c) = param_2 + *(int *)(param_1 + 0x1c);
    *(int *)(param_1 + 0x20) = param_3 + *(int *)(param_1 + 0x20);
    FUN_0044035e(param_1,param_2,param_3,0);
    if (iVar4 != 0) {
      FUN_00451670(iVar4,0x2a,param_1);
    }
    FUN_00440656(param_1);
    if ((iVar4 != 0) &&
       ((cVar2 = FUN_00450f28(param_1 + 0x14,auStack_38,0), cVar1 != '\0' || (cVar2 != '\0')))) {
      FUN_0044f2ca(iVar4);
    }
  }
  return;
}

