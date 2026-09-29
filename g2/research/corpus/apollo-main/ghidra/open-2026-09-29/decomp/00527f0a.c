
undefined4 ps_property_set(int param_1,undefined4 param_2,int *param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  
  uVar5 = 0;
  iVar1 = FUN_0046cacc(param_2,DAT_00528700);
  if (iVar1 == 0) {
    iVar1 = *param_3;
    iVar2 = param_3[1];
    iVar3 = param_3[2];
    iVar4 = param_3[3];
    iVar7 = param_3[4];
    iVar8 = param_3[5];
    iVar9 = param_3[6];
    iVar6 = param_3[7];
    if (((((iVar1 < 0) || (iVar3 < 0)) || (iVar7 < 0)) ||
        (((iVar9 < 0 || (iVar2 < 0)) || ((iVar4 < 0 || ((iVar8 < 0 || (iVar6 < 0)))))))) ||
       ((iVar3 < iVar1 ||
        (((((iVar7 < iVar3 || (iVar9 < iVar7)) || (500 < iVar2)) || ((500 < iVar4 || (500 < iVar8)))
          ) || (500 < iVar6)))))) {
      uVar5 = 6;
    }
    else {
      *(int *)(param_1 + 0x24) = iVar1;
      *(int *)(param_1 + 0x28) = iVar2;
      *(int *)(param_1 + 0x2c) = iVar3;
      *(int *)(param_1 + 0x30) = iVar4;
      *(int *)(param_1 + 0x34) = iVar7;
      *(int *)(param_1 + 0x38) = iVar8;
      *(int *)(param_1 + 0x3c) = iVar9;
      *(int *)(param_1 + 0x40) = iVar6;
      uVar5 = 0;
    }
  }
  else {
    iVar1 = FUN_0046cacc(param_2,DAT_00528704);
    if (iVar1 == 0) {
      if (*param_3 == 1) {
        *(int *)(param_1 + 0x1c) = *param_3;
      }
      else {
        uVar5 = 7;
      }
    }
    else {
      iVar1 = FUN_0046cacc(param_2,DAT_00528708);
      if (iVar1 == 0) {
        *(char *)(param_1 + 0x20) = (char)*param_3;
        uVar5 = 0;
      }
      else {
        iVar1 = FUN_0046cacc(param_2,DAT_0052870c);
        if (iVar1 == 0) {
          iVar1 = *param_3;
          if (iVar1 < 0) {
            iVar1 = 0;
          }
          *(int *)(param_1 + 0x44) = iVar1;
          uVar5 = 0;
        }
        else {
          uVar5 = 0xc;
        }
      }
    }
  }
  return uVar5;
}

