
undefined8 SmpDmLescEnabled(undefined1 param_1)

{
  int iVar1;
  uint uVar2;
  undefined4 unaff_r7;
  
  iVar1 = smpCcbByConnId(param_1);
  if ((iVar1 == 0) || (*(int *)(iVar1 + 0x48) == 0)) {
    uVar2 = 0;
  }
  else {
    uVar2 = (uint)**(byte **)(iVar1 + 0x48);
  }
  return CONCAT44(unaff_r7,uVar2);
}

