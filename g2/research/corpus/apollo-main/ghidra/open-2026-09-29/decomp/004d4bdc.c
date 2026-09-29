
undefined8 FUN_004d4bdc(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  
  iVar1 = DAT_004d4cbc;
  if (*(int *)(DAT_004d4cbc + 0x138) == 0) {
    param_2 = DAT_004d4cc0[1];
    uVar3 = FUN_004d4cd4(DAT_004d4cc4,0x18,param_1,*DAT_004d4cc0,param_2,DAT_004d4cc0[2],param_4);
    *(undefined4 *)(iVar1 + 0x138) = uVar3;
    FUN_004d5114(*(undefined4 *)(iVar1 + 0x138),DAT_004d4cc8);
    uVar2 = (uint)(*(int *)(iVar1 + 0x138) != 0);
  }
  else {
    uVar2 = 1;
  }
  return CONCAT44(param_2,uVar2);
}

