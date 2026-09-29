
undefined8 uart_sync_write(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  iVar1 = FUN_00584c98();
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    uVar2 = 0xffffffff;
  }
  return CONCAT44(unaff_r7,uVar2);
}

