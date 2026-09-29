
undefined8 FUN_0047f418(void)

{
  undefined4 uVar1;
  uint uVar2;
  int unaff_r7;
  
  if (*DAT_0047fad0 == '\x01') {
    *DAT_0047fadc = *DAT_0047fadc & 0xffffffdf;
    uVar2 = 0;
    while ((uVar2 < 10000 && (*DAT_0047fad4 << 0x18 < 0))) {
      uVar2 = uVar2 + 1;
    }
    if (uVar2 == 10000) {
      uVar1 = 4;
      goto LAB_0047f468;
    }
    unaff_r7 = *DAT_0047fad4;
    FUN_00480312(5,0,&stack0xfffffff8);
  }
  uVar1 = 0;
LAB_0047f468:
  return CONCAT44(unaff_r7,uVar1);
}

