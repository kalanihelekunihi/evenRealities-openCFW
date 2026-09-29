
undefined8 FUN_005ea4f0(short param_1,int param_2)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  undefined4 unaff_r7;
  
  if (((param_2 == 0) || (*(char *)(param_2 + 1) != '\0')) || (param_1 == 0)) {
    uVar2 = 0;
  }
  else {
    iVar3 = td_session_record_at(param_1 + -1);
    if ((iVar3 == 0) || (*(char *)(iVar3 + 1) != '\x01')) {
      bVar1 = 0;
    }
    else {
      bVar1 = 1;
    }
    uVar2 = (uint)bVar1;
  }
  return CONCAT44(unaff_r7,uVar2);
}

