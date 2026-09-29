
undefined8 FUN_0048f6ea(int param_1,char param_2,byte *param_3,uint *param_4)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  
  uVar4 = *param_4;
  if (param_2 == '\0') {
    *param_4 = 0;
    do {
      *param_4 = *param_4 + 1;
      if (uVar4 < *param_4) {
        uVar3 = DAT_0048fc84;
        if (*(int *)(param_1 + 0xc) != 0) {
          uVar3 = *(undefined4 *)(param_1 + 0xc);
        }
        *(undefined4 *)(param_1 + 0xc) = uVar3;
        uVar3 = 0;
        goto LAB_0048f77c;
      }
      iVar2 = FUN_0048f3be(param_1,param_3,1);
      if (iVar2 == 0) {
        uVar3 = 0;
        goto LAB_0048f77c;
      }
      bVar1 = *param_3;
      param_3 = param_3 + 1;
    } while ((int)((uint)bVar1 << 0x18) < 0);
    uVar3 = 1;
  }
  else if (param_2 == '\x01') {
    *param_4 = 8;
    uVar3 = FUN_0048f3be(param_1,param_3,8);
  }
  else if (param_2 == '\x05') {
    *param_4 = 4;
    uVar3 = FUN_0048f3be(param_1,param_3,4);
  }
  else {
    uVar3 = DAT_00490118;
    if (*(int *)(param_1 + 0xc) != 0) {
      uVar3 = *(undefined4 *)(param_1 + 0xc);
    }
    *(undefined4 *)(param_1 + 0xc) = uVar3;
    uVar3 = 0;
  }
LAB_0048f77c:
  return CONCAT44(param_4,uVar3);
}

