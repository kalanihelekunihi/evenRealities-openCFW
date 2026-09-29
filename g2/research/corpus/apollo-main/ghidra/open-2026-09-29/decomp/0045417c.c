
undefined8 FUN_0045417c(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint local_18;
  uint local_14;
  undefined4 uStack_10;
  
  local_18 = param_2;
  local_14 = param_3;
  uStack_10 = param_4;
  iVar1 = FUN_00450f00(param_2,param_1 + 0x14);
  if (iVar1 == 0) {
    uVar2 = 1;
  }
  else {
    local_18 = local_18 & 0xffffff00;
    local_14 = param_2;
    FUN_00451670(param_1,0x1a,&local_18);
    if ((char)local_18 == '\0') {
      uVar2 = 0;
    }
    else {
      uVar2 = 1;
    }
  }
  return CONCAT44(local_18,uVar2);
}

