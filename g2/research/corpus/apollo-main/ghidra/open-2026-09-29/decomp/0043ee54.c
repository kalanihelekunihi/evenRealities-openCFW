
undefined8 FUN_0043ee54(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar4 = 0;
  if (*(int *)(param_1 + 8) != 0) {
    uVar4 = (uint)*(ushort *)(*(int *)(param_1 + 8) + 0x30);
  }
  uVar5 = 0;
  do {
    if (uVar4 <= uVar5) {
      uVar3 = 0;
LAB_0043ee92:
      return CONCAT44(param_4,uVar3);
    }
    iVar2 = *(int *)(**(int **)(param_1 + 8) + uVar5 * 4);
    if (iVar2 == param_2) {
      uVar3 = 1;
      goto LAB_0043ee92;
    }
    cVar1 = FUN_0043ee54(iVar2,param_2);
    if (cVar1 != '\0') {
      uVar3 = 1;
      goto LAB_0043ee92;
    }
    uVar5 = uVar5 + 1;
  } while( true );
}

