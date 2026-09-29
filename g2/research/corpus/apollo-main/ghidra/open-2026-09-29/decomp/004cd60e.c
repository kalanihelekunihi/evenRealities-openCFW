
undefined8 FUN_004cd60e(undefined4 param_1,int param_2,undefined1 *param_3,undefined4 param_4)

{
  int iVar1;
  
  FUN_0043c0e4(param_3,0x108,0);
  if (*(int *)(param_2 + 0x28) == 0) {
    *param_3 = 2;
    FUN_0048d540(param_3 + 8,&DAT_004cd6d8);
    *(int *)(param_2 + 0x28) = *(int *)(param_2 + 0x28) + 1;
    iVar1 = 1;
  }
  else if (*(int *)(param_2 + 0x28) == 1) {
    *param_3 = 2;
    FUN_0048d540(param_3 + 8,&DAT_004cd6dc);
    *(int *)(param_2 + 0x28) = *(int *)(param_2 + 0x28) + 1;
    iVar1 = 1;
  }
  else {
    do {
      if (*(short *)(param_2 + 4) == *(short *)(param_2 + 0x1c)) {
        if (*(char *)(param_2 + 0x1f) == '\0') {
          iVar1 = 0;
          goto LAB_004cd6b8;
        }
        iVar1 = FUN_004cbedc(param_1,param_2 + 8,param_2 + 0x20);
        if (iVar1 != 0) goto LAB_004cd6b8;
        *(undefined2 *)(param_2 + 4) = 0;
      }
      iVar1 = FUN_004cbf38(param_1,param_2 + 8,*(undefined2 *)(param_2 + 4),param_3);
      if ((iVar1 != 0) && (iVar1 != -2)) goto LAB_004cd6b8;
      *(short *)(param_2 + 4) = *(short *)(param_2 + 4) + 1;
    } while (iVar1 == -2);
    *(int *)(param_2 + 0x28) = *(int *)(param_2 + 0x28) + 1;
    iVar1 = 1;
  }
LAB_004cd6b8:
  return CONCAT44(param_4,iVar1);
}

