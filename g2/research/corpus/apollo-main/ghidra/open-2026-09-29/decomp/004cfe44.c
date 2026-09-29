
undefined8 FUN_004cfe44(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_004cfd70(param_1);
  uVar2 = FUN_004cfe10(param_1);
  uVar2 = FUN_004cfe1a(uVar2,iVar1 - *DAT_004d06b0);
  iVar1 = FUN_004cfda0(param_1);
  if (iVar1 != 0) {
    FUN_004d09b4(DAT_004d06e4,DAT_004d06ac,0x1ba);
  }
  return CONCAT44(param_4,uVar2);
}

