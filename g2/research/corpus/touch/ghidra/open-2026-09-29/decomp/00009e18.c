
undefined4 Cy_SysClk_IloCompensate(int param_1,int *param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  uVar2 = DAT_00009f30;
  if ((((param_1 - 100U <= DAT_00009ef4) && (uVar2 = DAT_00009f30, param_2 != (int *)0x0)) &&
      (uVar2 = DAT_00009f08, *DAT_00009ef8 == DAT_00009f04)) &&
     ((*(uint *)(DAT_00009efc + 0x34) & DAT_00009f00) == 0x100)) {
    if (*DAT_00009f0c == '\0') {
      *DAT_00009f10 = *DAT_00009f20 >> 10;
      *DAT_00009f0c = '\x01';
      uVar2 = DAT_00009f2c;
    }
    else {
      uVar2 = DAT_00009f2c;
      if (((int)*DAT_00009f10 < 0) && (uVar2 = DAT_00009f08, *DAT_00009f14 != 0)) {
        iVar3 = param_1 * 100 + DAT_00009f18;
        iVar1 = __aeabi_uidiv(iVar3,DAT_00009f1c);
        if ((uint)(iVar1 * *DAT_00009f14) < 0x400000) {
          iVar3 = __aeabi_uidiv(*DAT_00009f20 * *DAT_00009f14,*DAT_00009f20 >> 10);
          iVar1 = __aeabi_uidiv(iVar1 * iVar3,DAT_00009f28);
        }
        else {
          uVar2 = __aeabi_uidiv(*DAT_00009f20 * *DAT_00009f14,*DAT_00009f20 >> 10);
          iVar1 = __aeabi_uidiv(uVar2,0x28);
          iVar3 = __aeabi_uidiv(iVar3,DAT_00009f24);
          iVar1 = iVar1 * iVar3;
        }
        *param_2 = iVar1;
        *DAT_00009f0c = '\0';
        uVar2 = 0;
      }
    }
  }
  return uVar2;
}

