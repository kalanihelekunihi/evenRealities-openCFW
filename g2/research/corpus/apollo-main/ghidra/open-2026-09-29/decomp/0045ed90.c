
undefined4 FUN_0045ed90(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = *param_1;
  iVar1 = *(int *)(iVar3 + 0x10);
  *(undefined1 *)(iVar1 + 0x1c) = 0;
  FUN_0045bbd2();
  for (iVar3 = FUN_0044dca2(iVar3); (iVar3 != 0 && (*(int *)(iVar3 + 0x10) == 0));
      iVar3 = FUN_0044dca2(iVar3)) {
  }
  iVar3 = *(int *)(iVar3 + 0x10);
  if (iVar3 != 0) {
    if (*(int *)(iVar3 + 0x10) == 0) {
      *(undefined1 *)(iVar3 + 0x14) = 0;
      for (iVar4 = *(int *)(iVar3 + 0xc); iVar4 != 0; iVar4 = *(int *)(iVar4 + 0x20)) {
        if (*(char *)(iVar4 + 0x1c) == '\x01') {
          if (*(int *)(iVar4 + 0x18) != 0) {
            (**(code **)(iVar4 + 0x18))(iVar4,iVar3,0x43,0);
          }
          *(int *)(iVar3 + 4) = iVar4;
          if (*(int *)(iVar1 + 0x18) != 0) {
            (**(code **)(iVar1 + 0x18))(iVar1,iVar3,0x4e,0);
          }
          break;
        }
      }
    }
    else {
      uVar2 = **(undefined4 **)(iVar3 + 0x10);
      *(undefined4 *)(iVar3 + 0x10) = 0;
      *(undefined1 *)(iVar3 + 0x14) = 0;
      FUN_0045f58c(iVar3,uVar2);
    }
    *(undefined1 *)(iVar3 + 0xe8) = 0;
    FUN_0045fd06(iVar3);
  }
  return param_4;
}

