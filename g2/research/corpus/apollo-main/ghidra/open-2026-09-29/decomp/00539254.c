
undefined8 FUN_00539254(void)

{
  uint *puVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  FUN_0053928c(0);
  puVar1 = DAT_005392d0;
  *DAT_005392d0 = *DAT_005392d0 & 0xffffffef;
  *puVar1 = *puVar1 & 0xfffffffe;
  iVar2 = FUN_004807fc(1000,DAT_005392d0,0,0);
  if ((iVar2 == 0) && (iVar2 = FUN_004d3f78(), iVar2 == 3)) {
    iVar2 = 0;
  }
  return CONCAT44(unaff_r7,iVar2);
}

