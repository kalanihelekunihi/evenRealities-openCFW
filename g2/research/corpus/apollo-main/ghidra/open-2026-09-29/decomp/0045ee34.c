
undefined4 FUN_0045ee34(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  
  iVar6 = *param_1;
  iVar2 = *(int *)(iVar6 + 0x10);
  if (*(char *)(iVar2 + 10) == '\0') {
    cVar1 = *(char *)(iVar2 + 8);
  }
  else {
    cVar1 = *(char *)(iVar2 + 9);
  }
  iVar3 = FUN_0044dca2(iVar6);
  if (cVar1 == '\0') {
    iVar4 = FUN_0043fd9e(iVar6);
    FUN_0043f0e0(iVar6,-iVar4);
  }
  else if (cVar1 == '\x01') {
    uVar5 = FUN_0043fdda(iVar3);
    FUN_0043f142(iVar6,uVar5);
  }
  else {
    iVar4 = FUN_0043fdda(iVar6);
    FUN_0043f142(iVar6,-iVar4);
  }
  *(undefined1 *)(iVar2 + 0x1c) = 0;
  FUN_0045bbd2();
  for (; (iVar3 != 0 && (*(int *)(iVar3 + 0x10) == 0)); iVar3 = FUN_0044dca2(iVar3)) {
  }
  iVar6 = *(int *)(iVar3 + 0x10);
  if (iVar6 != 0) {
    if (*(int *)(iVar6 + 0x10) == 0) {
      *(undefined1 *)(iVar6 + 0x14) = 0;
      for (iVar3 = *(int *)(iVar6 + 0xc); iVar3 != 0; iVar3 = *(int *)(iVar3 + 0x20)) {
        if (*(char *)(iVar3 + 0x1c) == '\x01') {
          if (*(int *)(iVar3 + 0x18) != 0) {
            (**(code **)(iVar3 + 0x18))(iVar3,iVar6,0x43,0);
          }
          *(int *)(iVar6 + 4) = iVar3;
          if (*(int *)(iVar2 + 0x18) != 0) {
            (**(code **)(iVar2 + 0x18))(iVar2,iVar6,0x4e,0);
          }
          break;
        }
      }
    }
    else {
      uVar5 = **(undefined4 **)(iVar6 + 0x10);
      *(undefined4 *)(iVar6 + 0x10) = 0;
      *(undefined1 *)(iVar6 + 0x14) = 0;
      FUN_0045f58c(iVar6,uVar5);
    }
    *(undefined1 *)(iVar6 + 0xe8) = 0;
    FUN_0045fd06(iVar6);
  }
  return param_4;
}

