
undefined8 FUN_005c8808(int param_1,int param_2,undefined4 param_3,int param_4)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  int local_10;
  
  local_10 = param_4;
  if (*(int *)(param_1 + 0x40) != 0) {
    FUN_005c811c();
    uVar1 = (*(code *)*DAT_005c8d34)();
    if (*(uint *)(param_1 + 0x40) <= uVar1) {
      uVar2 = 0;
      goto LAB_005c8860;
    }
  }
  if ((*(int *)(param_1 + 0x3c) == 0) || (**(char **)(param_1 + 0x3c) == '\0')) {
    uVar2 = 1;
  }
  else {
    local_10 = 0;
    do {
      if (*(char *)(*(int *)(param_1 + 0x3c) + local_10) == '\0') {
        uVar2 = 0;
        goto LAB_005c8860;
      }
      iVar3 = (*(code *)*DAT_005c8fc8)(*(undefined4 *)(param_1 + 0x3c),&local_10);
    } while (iVar3 != param_2);
    uVar2 = 1;
  }
LAB_005c8860:
  return CONCAT44(local_10,uVar2);
}

