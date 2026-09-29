
undefined8 FUN_005511bc(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = service_ancc_message_count_get();
  if (iVar1 < 1) {
    iVar1 = 0;
  }
  else {
    iVar1 = iVar1 + -1;
  }
  return CONCAT44(unaff_r7,iVar1);
}

