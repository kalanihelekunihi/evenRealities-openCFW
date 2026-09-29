
ulonglong FUN_005f9fa4(undefined4 param_1)

{
  int iVar1;
  undefined4 unaff_r7;
  undefined4 uVar2;
  
  if ((int)&DAT_005f9fdc + DAT_005f9fdc != (int)&DAT_005f9fe0 + DAT_005f9fe0) {
    return CONCAT44(unaff_r7,param_1);
  }
  uVar2 = CONCAT31((int3)((uint)unaff_r7 >> 8),(char)param_1);
  iVar1 = FUN_005f9fe8(1,&stack0xfffffff8,1);
  if (iVar1 == 1) {
    return CONCAT44(uVar2,param_1) & 0xffffffff000000ff;
  }
  return CONCAT44(uVar2,0xffffffff);
}

