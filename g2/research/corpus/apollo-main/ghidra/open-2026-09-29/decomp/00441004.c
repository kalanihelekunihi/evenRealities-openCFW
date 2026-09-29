
ulonglong FUN_00441004(undefined1 param_1)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = FUN_00440f44(param_1);
  return CONCAT44(unaff_r7,(iVar1 + 7U & 0xffff) >> 3) & 0xffffffff000000ff;
}

