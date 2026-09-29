
undefined8 stage_one_entry(void)

{
  uint *puVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  stage_one_status(0);
  puVar1 = DAT_00423d9c;
  *DAT_00423d9c = *DAT_00423d9c & 0xffffffef;
  *puVar1 = *puVar1 & 0xfffffffe;
  iVar2 = delay_status_change(1000,DAT_00423d9c,0,0);
  if ((iVar2 == 0) && (iVar2 = debug_disable(), iVar2 == 3)) {
    iVar2 = 0;
  }
  return CONCAT44(unaff_r7,iVar2);
}

