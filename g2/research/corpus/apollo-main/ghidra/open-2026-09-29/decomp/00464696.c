
undefined4 FUN_00464696(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = DAT_004646b8;
  *(undefined4 *)(DAT_004646b8 + 0x84) = 0;
  if (*(int *)(iVar1 + 0x9c) != 0) {
    (**(code **)(iVar1 + 0x9c))(*(undefined4 *)(iVar1 + 0xa0));
  }
  return unaff_r7;
}

