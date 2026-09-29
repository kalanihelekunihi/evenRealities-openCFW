
undefined4 FUN_00590b6c(int param_1,char param_2)

{
  undefined4 uVar1;
  
  if (param_2 == '\0') {
    if (*(int *)(param_1 + 0x40) == -1) {
      uVar1 = *(undefined4 *)(param_1 + 0x3c);
    }
    else {
      uVar1 = *(undefined4 *)(param_1 + 0x4c);
    }
  }
  else if (*(int *)(param_1 + 0x48) == -1) {
    uVar1 = *(undefined4 *)(param_1 + 0x44);
  }
  else {
    uVar1 = *(undefined4 *)(param_1 + 0x50);
  }
  return uVar1;
}

