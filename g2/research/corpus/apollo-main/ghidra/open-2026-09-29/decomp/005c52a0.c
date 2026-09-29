
void FUN_005c52a0(int *param_1)

{
  char cVar1;
  int iVar2;
  int iVar3;
  undefined1 auStack_30 [16];
  undefined1 auStack_20 [16];
  
  iVar3 = *(int *)(*param_1 + 0x2c);
  iVar2 = FUN_00451960(param_1);
  cVar1 = FUN_00450bcc(auStack_20,iVar2 + 0x18,*(int *)(iVar3 + 0x2c) + 0x14);
  if (cVar1 != '\0') {
    FUN_00439c04(auStack_30,iVar2 + 0x18,0x10);
    FUN_00439c04(iVar2 + 0x18,auStack_20,0x10);
    if ((*(byte *)(iVar3 + 0x4c) & 0x3f) >> 5 == 0) {
      FUN_005c5370(iVar3,iVar2,*(undefined4 *)(iVar3 + 0x48),0x20);
      FUN_005c5440(iVar3,iVar2,*(undefined4 *)(iVar3 + 0x48),0x20);
    }
    else if (*(int *)(iVar3 + 0x48) == *(int *)(iVar3 + 0x40)) {
      FUN_005c5370(iVar3,iVar2,*(undefined4 *)(iVar3 + 0x48),0x21);
      FUN_005c5440(iVar3,iVar2,*(undefined4 *)(iVar3 + 0x48),0x21);
    }
    else {
      FUN_005c5370(iVar3,iVar2,*(undefined4 *)(iVar3 + 0x48),0x20);
      FUN_005c5440(iVar3,iVar2,*(undefined4 *)(iVar3 + 0x48),0x20);
      FUN_005c5370(iVar3,iVar2,*(undefined4 *)(iVar3 + 0x40),1);
      FUN_005c5440(iVar3,iVar2,*(undefined4 *)(iVar3 + 0x40),1);
    }
    FUN_00439c04(iVar2 + 0x18,auStack_30,0x10);
  }
  return;
}

