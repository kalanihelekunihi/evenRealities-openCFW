
undefined8 FUN_0048ea66(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  uint local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 uStack_1c;
  
  local_28 = param_1 & 0xffffff00;
  local_24 = param_2;
  local_20 = param_3;
  uStack_1c = param_4;
  uVar1 = FUN_0047dcb4(&local_28);
  uVar2 = FUN_0047dc74();
  if (((char)local_28 != '\0') && (*DAT_0048ed80 == '\0')) {
    *DAT_0048ed80 = '\x01';
    local_24 = uVar2;
    local_20 = uVar1;
    FUN_0048e9be(DAT_0048ed84,2,&local_24,uVar1);
  }
  if ((char)local_28 == '\0') {
    uVar1 = uVar2;
  }
  FUN_0048e9be(param_1,param_2,param_3,uVar1);
  return CONCAT44(local_24,local_28);
}

