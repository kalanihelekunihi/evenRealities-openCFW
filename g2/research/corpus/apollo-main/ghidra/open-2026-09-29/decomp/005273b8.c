
undefined8 FT_Get_Module(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  
  uVar2 = 0;
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar2 = 0;
  }
  else {
    puVar3 = (undefined4 *)(param_1 + 0x14);
    puVar4 = puVar3 + *(int *)(param_1 + 0x10);
    for (; puVar3 < puVar4; puVar3 = puVar3 + 1) {
      iVar1 = FUN_0046cacc(*(undefined4 *)(*(int *)*puVar3 + 8),param_2);
      if (iVar1 == 0) {
        uVar2 = *puVar3;
        break;
      }
    }
  }
  return CONCAT44(param_4,uVar2);
}

