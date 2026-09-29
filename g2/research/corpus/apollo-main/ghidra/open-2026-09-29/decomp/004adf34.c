
undefined8 als_function_24(void)

{
  byte bVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined4 unaff_r7;
  
  if (*DAT_004ae6c8 < 2) {
    uVar3 = als_function_15(1);
    uVar2 = als_function_17(uVar3,*DAT_004ae810);
    if ((uVar2 < *DAT_004ae954) || (uVar2 < *DAT_004ae8dc)) {
      bVar1 = 0;
    }
    else {
      bVar1 = 1;
    }
    uVar2 = (uint)bVar1;
  }
  else {
    uVar2 = 0;
  }
  return CONCAT44(unaff_r7,uVar2);
}

