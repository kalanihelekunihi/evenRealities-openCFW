
uint FUN_005d1ed0(int param_1,uint param_2)

{
  char *pcVar1;
  char *pcVar2;
  int iVar3;
  uint uVar4;
  
  if (param_2 < 0x100) {
    pcVar1 = (char *)(**(code **)(*(int *)(param_1 + 600) + 0x14))
                               (*(undefined2 *)
                                 (*(int *)(*(int *)(param_1 + 600) + 0x18) + param_2 * 2));
    for (uVar4 = 0; uVar4 < *(uint *)(param_1 + 0x248); uVar4 = uVar4 + 1) {
      pcVar2 = *(char **)(*(int *)(param_1 + 0x244) + uVar4 * 4);
      if (((pcVar2 != (char *)0x0) && (*pcVar2 == *pcVar1)) &&
         (iVar3 = FUN_0046cacc(pcVar2,pcVar1), iVar3 == 0)) {
        return uVar4;
      }
    }
  }
  return 0xffffffff;
}

