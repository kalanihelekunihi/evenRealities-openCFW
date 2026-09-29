
undefined8 FUN_005beac2(int param_1,uint param_2,char *param_3,int param_4)

{
  undefined4 uVar1;
  int iVar2;
  undefined1 *puVar3;
  
  if (((param_3 == (char *)0x0) || (*param_3 != *DAT_005bf094)) || (param_4 != 0x38)) {
    uVar1 = 0xfffffffa;
  }
  else if (param_1 == 0) {
    uVar1 = 0xfffffffe;
  }
  else {
    *(undefined4 *)(param_1 + 0x18) = 0;
    if (*(int *)(param_1 + 0x20) == 0) {
      *(undefined4 *)(param_1 + 0x20) = 0x5befe5;
      *(undefined4 *)(param_1 + 0x28) = 0;
    }
    if (*(int *)(param_1 + 0x24) == 0) {
      *(undefined1 **)(param_1 + 0x24) = &LAB_005befec_1;
    }
    uVar1 = (**(code **)(param_1 + 0x20))(*(undefined4 *)(param_1 + 0x28),1,0x18);
    *(undefined4 *)(param_1 + 0x1c) = uVar1;
    if (*(int *)(param_1 + 0x1c) == 0) {
      uVar1 = 0xfffffffc;
    }
    else {
      *(undefined4 *)(*(int *)(param_1 + 0x1c) + 0x14) = 0;
      *(undefined4 *)(*(int *)(param_1 + 0x1c) + 0xc) = 0;
      if ((int)param_2 < 0) {
        param_2 = -param_2;
        *(undefined4 *)(*(int *)(param_1 + 0x1c) + 0xc) = 1;
      }
      if (param_2 - 8 < 8) {
        *(uint *)(*(int *)(param_1 + 0x1c) + 0x10) = param_2;
        if (*(int *)(*(int *)(param_1 + 0x1c) + 0xc) == 0) {
          puVar3 = &LAB_005beefc_1;
        }
        else {
          puVar3 = (undefined1 *)0x0;
        }
        iVar2 = FUN_005be024(param_1,puVar3,1 << (param_2 & 0xff));
        *(int *)(*(int *)(param_1 + 0x1c) + 0x14) = iVar2;
        if (iVar2 == 0) {
          FUN_005bea86(param_1);
          uVar1 = 0xfffffffc;
        }
        else {
          FUN_005bea46(param_1);
          uVar1 = 0;
        }
      }
      else {
        FUN_005bea86(param_1);
        uVar1 = 0xfffffffe;
      }
    }
  }
  return CONCAT44(param_4,uVar1);
}

