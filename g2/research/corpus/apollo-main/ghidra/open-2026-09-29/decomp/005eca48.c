
undefined8 FUN_005eca48(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  iVar1 = td_active_session();
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else if (*(uint *)(iVar1 + 8) < 0xb) {
    uVar2 = *(undefined4 *)(iVar1 + 8);
  }
  else {
    uVar2 = 10;
  }
  return CONCAT44(unaff_r7,uVar2);
}

