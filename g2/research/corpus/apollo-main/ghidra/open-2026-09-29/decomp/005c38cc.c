
undefined4 FUN_005c38cc(int *param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int *piVar2;
  int *piVar3;
  int *piVar4;
  
  while ((piVar2 = (int *)*param_2, piVar2 != (int *)0x0 && (*(char *)(piVar2 + 3) == '\0'))) {
    piVar4 = (int *)*piVar2;
    if (piVar2 == (int *)piVar4[1]) {
      iVar1 = piVar4[2];
      if ((iVar1 == 0) || (*(char *)(iVar1 + 0xc) != '\0')) {
        piVar3 = piVar2;
        if ((int *)piVar2[2] == param_2) {
          FUN_005c3896(param_1,piVar2);
          piVar3 = param_2;
          param_2 = piVar2;
        }
        *(undefined1 *)(piVar3 + 3) = 1;
        *(undefined1 *)(piVar4 + 3) = 0;
        FUN_005c3860(param_1,piVar4);
      }
      else {
        *(undefined1 *)(iVar1 + 0xc) = 1;
        *(undefined1 *)(piVar2 + 3) = 1;
        *(undefined1 *)(piVar4 + 3) = 0;
        param_2 = piVar4;
      }
    }
    else {
      iVar1 = piVar4[1];
      if ((iVar1 == 0) || (*(char *)(iVar1 + 0xc) != '\0')) {
        piVar3 = piVar2;
        if ((int *)piVar2[1] == param_2) {
          FUN_005c3860(param_1,piVar2);
          piVar3 = param_2;
          param_2 = piVar2;
        }
        *(undefined1 *)(piVar3 + 3) = 1;
        *(undefined1 *)(piVar4 + 3) = 0;
        FUN_005c3896(param_1,piVar4);
      }
      else {
        *(undefined1 *)(iVar1 + 0xc) = 1;
        *(undefined1 *)(piVar2 + 3) = 1;
        *(undefined1 *)(piVar4 + 3) = 0;
        param_2 = piVar4;
      }
    }
  }
  *(undefined1 *)(*param_1 + 0xc) = 1;
  return param_4;
}

