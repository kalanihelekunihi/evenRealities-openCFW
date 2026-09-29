
undefined8 FUN_00585a52(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  byte bVar3;
  
  bVar3 = 0;
  if (*(char *)(param_1 + 0x19) == '\0') {
    iVar2 = FUN_00597d72(*(undefined4 *)(param_1 + 8));
    if (iVar2 < 0) {
      bVar3 = 3;
    }
    uVar1 = (uint)bVar3;
  }
  else {
    uVar1 = 3;
  }
  return CONCAT44(param_4,uVar1);
}

