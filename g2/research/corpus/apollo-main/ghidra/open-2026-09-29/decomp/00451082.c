
int FUN_00451082(int *param_1,int *param_2,byte param_3,int param_4,int param_5)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  if (param_3 == 1) {
    iVar5 = 0;
    iVar6 = 0;
    goto LAB_0045136a;
  }
  if (param_3 != 0) {
    if (param_3 == 3) {
      iVar5 = FUN_00451598(param_1);
      iVar6 = FUN_00451598(param_2);
      iVar5 = iVar5 - iVar6;
      iVar6 = 0;
      goto LAB_0045136a;
    }
    if (param_3 < 3) {
      iVar6 = FUN_00451598(param_1);
      iVar5 = FUN_00451598(param_2);
      iVar5 = iVar6 / 2 - iVar5 / 2;
      iVar6 = 0;
      goto LAB_0045136a;
    }
    if (param_3 == 5) {
      iVar6 = FUN_00451598(param_1);
      iVar5 = FUN_00451598(param_2);
      iVar5 = iVar6 / 2 - iVar5 / 2;
      iVar6 = FUN_004515a4(param_1);
      iVar1 = FUN_004515a4(param_2);
      iVar6 = iVar6 - iVar1;
      goto LAB_0045136a;
    }
    if (param_3 < 5) {
      iVar5 = 0;
      iVar6 = FUN_004515a4(param_1);
      iVar1 = FUN_004515a4(param_2);
      iVar6 = iVar6 - iVar1;
      goto LAB_0045136a;
    }
    if (param_3 == 7) {
      iVar5 = 0;
      iVar6 = FUN_004515a4(param_1);
      iVar1 = FUN_004515a4(param_2);
      iVar6 = iVar6 / 2 - iVar1 / 2;
      goto LAB_0045136a;
    }
    if (param_3 < 7) {
      iVar5 = FUN_00451598(param_1);
      iVar6 = FUN_00451598(param_2);
      iVar5 = iVar5 - iVar6;
      iVar6 = FUN_004515a4(param_1);
      iVar1 = FUN_004515a4(param_2);
      iVar6 = iVar6 - iVar1;
      goto LAB_0045136a;
    }
    if (param_3 == 9) {
      iVar6 = FUN_00451598(param_1);
      iVar5 = FUN_00451598(param_2);
      iVar5 = iVar6 / 2 - iVar5 / 2;
      iVar6 = FUN_004515a4(param_1);
      iVar1 = FUN_004515a4(param_2);
      iVar6 = iVar6 / 2 - iVar1 / 2;
      goto LAB_0045136a;
    }
    if (param_3 < 9) {
      iVar5 = FUN_00451598(param_1);
      iVar6 = FUN_00451598(param_2);
      iVar5 = iVar5 - iVar6;
      iVar6 = FUN_004515a4(param_1);
      iVar1 = FUN_004515a4(param_2);
      iVar6 = iVar6 / 2 - iVar1 / 2;
      goto LAB_0045136a;
    }
    if (param_3 == 0xb) {
      iVar6 = FUN_00451598(param_1);
      iVar5 = FUN_00451598(param_2);
      iVar5 = iVar6 / 2 - iVar5 / 2;
      iVar6 = FUN_004515a4(param_2);
      iVar6 = -iVar6;
      goto LAB_0045136a;
    }
    if (param_3 < 0xb) {
      iVar5 = 0;
      iVar6 = FUN_004515a4(param_2);
      iVar6 = -iVar6;
      goto LAB_0045136a;
    }
    if (param_3 == 0xd) {
      iVar5 = 0;
      iVar6 = FUN_004515a4(param_1);
      goto LAB_0045136a;
    }
    if (param_3 < 0xd) {
      iVar5 = FUN_00451598(param_1);
      iVar6 = FUN_00451598(param_2);
      iVar5 = iVar5 - iVar6;
      iVar6 = FUN_004515a4(param_2);
      iVar6 = -iVar6;
      goto LAB_0045136a;
    }
    if (param_3 == 0xf) {
      iVar5 = FUN_00451598(param_1);
      iVar6 = FUN_00451598(param_2);
      iVar5 = iVar5 - iVar6;
      iVar6 = FUN_004515a4(param_1);
      goto LAB_0045136a;
    }
    if (param_3 < 0xf) {
      iVar6 = FUN_00451598(param_1);
      iVar5 = FUN_00451598(param_2);
      iVar5 = iVar6 / 2 - iVar5 / 2;
      iVar6 = FUN_004515a4(param_1);
      goto LAB_0045136a;
    }
    if (param_3 == 0x11) {
      iVar5 = FUN_00451598(param_2);
      iVar5 = -iVar5;
      iVar6 = FUN_004515a4(param_1);
      iVar1 = FUN_004515a4(param_2);
      iVar6 = iVar6 / 2 - iVar1 / 2;
      goto LAB_0045136a;
    }
    if (param_3 < 0x11) {
      iVar5 = FUN_00451598(param_2);
      iVar5 = -iVar5;
      iVar6 = 0;
      goto LAB_0045136a;
    }
    if (param_3 == 0x13) {
      iVar5 = FUN_00451598(param_1);
      iVar6 = 0;
      goto LAB_0045136a;
    }
    if (param_3 < 0x13) {
      iVar5 = FUN_00451598(param_2);
      iVar5 = -iVar5;
      iVar6 = FUN_004515a4(param_1);
      iVar1 = FUN_004515a4(param_2);
      iVar6 = iVar6 - iVar1;
      goto LAB_0045136a;
    }
    if (param_3 == 0x15) {
      iVar5 = FUN_00451598(param_1);
      iVar6 = FUN_004515a4(param_1);
      iVar1 = FUN_004515a4(param_2);
      iVar6 = iVar6 - iVar1;
      goto LAB_0045136a;
    }
    if (param_3 < 0x15) {
      iVar5 = FUN_00451598(param_1);
      iVar6 = FUN_004515a4(param_1);
      iVar1 = FUN_004515a4(param_2);
      iVar6 = iVar6 / 2 - iVar1 / 2;
      goto LAB_0045136a;
    }
  }
  iVar5 = 0;
  iVar6 = 0;
LAB_0045136a:
  iVar1 = *param_1;
  iVar2 = param_1[1];
  iVar3 = FUN_00451598(param_2);
  iVar4 = FUN_004515a4(param_2);
  *param_2 = param_4 + iVar1 + iVar5;
  param_2[1] = param_5 + iVar2 + iVar6;
  param_2[2] = iVar3 + *param_2 + -1;
  param_2[3] = iVar4 + param_2[1] + -1;
  return param_4;
}

