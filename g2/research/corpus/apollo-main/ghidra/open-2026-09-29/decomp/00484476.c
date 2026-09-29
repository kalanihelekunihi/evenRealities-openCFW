
undefined8 FUN_00484476(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 *puVar2;
  int *piVar3;
  undefined4 local_18;
  
  piVar3 = *(int **)(param_2 + 0x54);
  piVar3[4] = param_1;
  puVar2 = DAT_004849c8;
  local_18 = param_3;
  if (*(char *)(DAT_004849c8 + 8) == '\0') {
    if ((*piVar3 != 0) && (iVar1 = FUN_0043e0e0(*piVar3,0x80000), iVar1 != 0)) {
      *(undefined1 *)(puVar2 + 8) = 1;
      FUN_00451670(*piVar3,0x22,param_2);
      *(undefined1 *)(puVar2 + 8) = 0;
    }
    *(undefined1 *)(param_2 + 0x59) = 100;
    *(undefined1 *)(param_2 + 0x58) = 0;
    for (puVar2 = (undefined4 *)*puVar2; puVar2 != (undefined4 *)0x0; puVar2 = (undefined4 *)*puVar2
        ) {
      if (puVar2[4] != 0) {
        (*(code *)puVar2[4])(puVar2,param_2);
      }
    }
    if (*(char *)(param_2 + 0x58) == '\0') {
      local_18 = DAT_004849cc;
      FUN_0044d25c(2,DAT_004849bc,0x9f,DAT_004849d0);
      *(undefined4 *)(param_2 + 0x50) = 3;
    }
    else {
      FUN_00484548();
    }
  }
  else {
    *(undefined1 *)(param_2 + 0x59) = 100;
    *(undefined1 *)(param_2 + 0x58) = 0;
    for (puVar2 = (undefined4 *)*puVar2; puVar2 != (undefined4 *)0x0; puVar2 = (undefined4 *)*puVar2
        ) {
      if (puVar2[4] != 0) {
        (*(code *)puVar2[4])(puVar2,param_2);
      }
    }
  }
  return CONCAT44(param_4,local_18);
}

