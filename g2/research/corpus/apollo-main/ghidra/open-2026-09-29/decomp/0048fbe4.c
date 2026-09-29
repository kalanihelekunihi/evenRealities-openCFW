
undefined8 FUN_0048fbe4(int param_1,undefined1 param_2,int param_3)

{
  undefined4 uVar1;
  byte bVar2;
  undefined4 unaff_r7;
  
  bVar2 = *(byte *)(param_3 + 0x16) & 0xc0;
  if ((*(byte *)(param_3 + 0x16) & 0xc0) == 0) {
    uVar1 = FUN_0048f968(param_1,param_2);
  }
  else if (bVar2 == 0x40) {
    uVar1 = FUN_0048fb30(param_1,param_2);
  }
  else if (bVar2 == 0x80) {
    uVar1 = FUN_0048fb1c(param_1,param_2);
  }
  else {
    uVar1 = DAT_00490488;
    if (*(int *)(param_1 + 0xc) != 0) {
      uVar1 = *(undefined4 *)(param_1 + 0xc);
    }
    *(undefined4 *)(param_1 + 0xc) = uVar1;
    uVar1 = 0;
  }
  return CONCAT44(unaff_r7,uVar1);
}

