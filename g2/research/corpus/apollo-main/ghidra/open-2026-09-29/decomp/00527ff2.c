
undefined8 ps_property_get(int param_1,undefined4 param_2,undefined4 *param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_0046cacc(param_2,DAT_00528700);
  if (iVar1 == 0) {
    *param_3 = *(undefined4 *)(param_1 + 0x24);
    param_3[1] = *(undefined4 *)(param_1 + 0x28);
    param_3[2] = *(undefined4 *)(param_1 + 0x2c);
    param_3[3] = *(undefined4 *)(param_1 + 0x30);
    param_3[4] = *(undefined4 *)(param_1 + 0x34);
    param_3[5] = *(undefined4 *)(param_1 + 0x38);
    param_3[6] = *(undefined4 *)(param_1 + 0x3c);
    param_3[7] = *(undefined4 *)(param_1 + 0x40);
    uVar2 = 0;
  }
  else {
    iVar1 = FUN_0046cacc(param_2,DAT_00528704);
    if (iVar1 == 0) {
      *param_3 = *(undefined4 *)(param_1 + 0x1c);
      uVar2 = 0;
    }
    else {
      iVar1 = FUN_0046cacc(param_2,DAT_00528708);
      if (iVar1 == 0) {
        *(undefined1 *)param_3 = *(undefined1 *)(param_1 + 0x20);
        uVar2 = 0;
      }
      else {
        uVar2 = 0xc;
      }
    }
  }
  return CONCAT44(param_4,uVar2);
}

