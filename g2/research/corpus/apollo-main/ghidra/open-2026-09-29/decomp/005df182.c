
undefined8
FUN_005df182(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_005df158();
  if (iVar1 == 0) {
    uVar2 = 0x8e;
  }
  else {
    if (param_4 != (undefined4 *)0x0) {
      *param_4 = *(undefined4 *)(iVar1 + 0xc);
    }
    uVar2 = FT_Stream_Seek(param_3,*(undefined4 *)(iVar1 + 8));
  }
  return CONCAT44(param_4,uVar2);
}

