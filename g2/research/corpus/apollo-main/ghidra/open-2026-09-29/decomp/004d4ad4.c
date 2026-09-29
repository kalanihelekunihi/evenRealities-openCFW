
undefined8 FUN_004d4ad4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  
  iVar1 = DAT_004d4bcc;
  if (*(int *)(DAT_004d4bcc + 0x134) == 0) {
    param_2 = DAT_004d4bd0[1];
    uVar3 = FUN_004d4cd4(DAT_004d4bd4,0x18,param_1,*DAT_004d4bd0,param_2,DAT_004d4bd0[2],param_4);
    *(undefined4 *)(iVar1 + 0x134) = uVar3;
    FUN_004d5114(*(undefined4 *)(iVar1 + 0x134),DAT_004d4bd8);
    uVar2 = (uint)(*(int *)(iVar1 + 0x134) != 0);
  }
  else {
    uVar2 = 1;
  }
  return CONCAT44(param_2,uVar2);
}

