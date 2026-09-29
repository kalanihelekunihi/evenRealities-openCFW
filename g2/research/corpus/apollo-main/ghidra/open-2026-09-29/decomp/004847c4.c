
void FUN_004847c4(int param_1,undefined4 param_2,undefined1 param_3,undefined4 param_4)

{
  int iVar1;
  
  FUN_004846de(param_1);
  iVar1 = FUN_00453604();
  *(undefined4 *)(param_1 + 0x48) = param_2;
  FUN_00439c04(param_1 + 0x18,param_4,0x10);
  FUN_00439c04(param_1 + 4,param_4,0x10);
  FUN_00439c04(param_1 + 0x28,param_4,0x10);
  *(undefined1 *)(param_1 + 0x14) = param_3;
  if (*(int *)(iVar1 + 0x2b0) != 0) {
    (**(code **)(iVar1 + 0x2b0))(iVar1,param_1);
  }
  if (*(int *)(iVar1 + 0x2ac) == 0) {
    *(int *)(iVar1 + 0x2ac) = param_1;
  }
  else {
    for (iVar1 = *(int *)(iVar1 + 0x2ac); *(int *)(iVar1 + 0x4c) != 0;
        iVar1 = *(int *)(iVar1 + 0x4c)) {
    }
    *(int *)(iVar1 + 0x4c) = param_1;
  }
  return;
}

