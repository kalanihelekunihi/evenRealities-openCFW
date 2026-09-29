
undefined8 attUuidCmp16to128(undefined1 *param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = DAT_004b51e8;
  *(undefined1 *)(DAT_004b51e8 + 0xc) = *param_1;
  *(undefined1 *)(iVar1 + 0xd) = param_1[1];
  iVar1 = FUN_004751c8(iVar1,param_2,0x10);
  return CONCAT44(unaff_r7,(uint)(iVar1 == 0));
}

