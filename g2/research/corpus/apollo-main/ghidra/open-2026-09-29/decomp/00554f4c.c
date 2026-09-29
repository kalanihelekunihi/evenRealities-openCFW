
void FUN_00554f4c(int param_1)

{
  int iVar1;
  
  iVar1 = FUN_00555710(0);
  if (param_1 == 10) {
    if (iVar1 != 0) {
      FUN_00589b68(4,0);
    }
  }
  else if (param_1 == 0x44) {
    if ((iVar1 != 0) && (iVar1 = FUN_00554ea8(), iVar1 != 0)) {
      FUN_00589b68(0xc,iVar1);
    }
  }
  else if (param_1 == 0x45) {
    if ((iVar1 != 0) && (iVar1 = FUN_00554ee8(), iVar1 != 0)) {
      FUN_00589b68(0xd,iVar1);
    }
  }
  else if (param_1 == 0x48) {
    system_close_page_factory_0046ae9c(1,6);
  }
  return;
}

