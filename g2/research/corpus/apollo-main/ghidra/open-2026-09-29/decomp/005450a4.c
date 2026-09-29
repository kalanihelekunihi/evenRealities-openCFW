
char FUN_005450a4(int param_1)

{
  char cVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined1 auStack_2c [20];
  undefined4 local_18;
  
  cVar1 = '\0';
  if (*(int *)(param_1 + 0x1c) != 0) {
    (**(code **)(param_1 + 0x1c))(param_1);
  }
  for (uVar2 = 0; uVar2 < 0x40; uVar2 = uVar2 + 1) {
    *(undefined4 *)(param_1 + uVar2 * 8 + 0xac) = 0xffffffff;
  }
  for (uVar2 = 0; uVar2 < *(uint *)(param_1 + 0x10); uVar2 = *(int *)(param_1 + 0xc) + uVar2) {
    cVar1 = FUN_005445f2(param_1,uVar2,0xffffffff);
    if (cVar1 != '\0') goto LAB_00545154;
  }
  for (uVar2 = 0; uVar2 < *(uint *)(param_1 + 0x2c); uVar2 = uVar2 + 1) {
    if (*(int *)(*(int *)(param_1 + 0x28) + uVar2 * 0xc + 8) == 0) {
      uVar3 = FUN_0044a43c(*(undefined4 *)(*(int *)(param_1 + 0x28) + uVar2 * 0xc + 4));
    }
    else {
      uVar3 = *(undefined4 *)(*(int *)(param_1 + 0x28) + uVar2 * 0xc + 8);
    }
    local_18 = 0xffffffff;
    FUN_00544d60(param_1,auStack_2c,*(undefined4 *)(*(int *)(param_1 + 0x28) + uVar2 * 0xc),
                 *(undefined4 *)(*(int *)(param_1 + 0x28) + uVar2 * 0xc + 4),uVar3);
    if (cVar1 != '\0') break;
  }
LAB_00545154:
  *(undefined4 *)(param_1 + 0x14) = 0;
  if (*(int *)(param_1 + 0x20) != 0) {
    (**(code **)(param_1 + 0x20))(param_1);
  }
  return cVar1;
}

