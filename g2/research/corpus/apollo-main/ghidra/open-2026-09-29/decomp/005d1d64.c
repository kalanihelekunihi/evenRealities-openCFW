
undefined8 FUN_005d1d64(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  char *pcVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  
  uVar4 = 0;
  if (param_2 < 0x100) {
    pcVar1 = (char *)(**(code **)(param_1 + 0x14))
                               (*(undefined2 *)(*(int *)(param_1 + 0x10) + param_2 * 2));
    uVar5 = 0;
    while ((uVar4 = 0, uVar5 < *(uint *)(param_1 + 0x18) &&
           (((pcVar2 = *(char **)(*(int *)(param_1 + 0x1c) + uVar5 * 4), pcVar2 == (char *)0x0 ||
             (*pcVar2 != *pcVar1)) ||
            (iVar3 = FUN_0046cacc(pcVar2,pcVar1), uVar4 = uVar5, iVar3 != 0))))) {
      uVar5 = uVar5 + 1;
    }
  }
  return CONCAT44(param_4,uVar4);
}

