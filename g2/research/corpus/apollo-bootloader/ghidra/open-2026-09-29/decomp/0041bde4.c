
undefined8 FUN_0041bde4(void)

{
  undefined4 uVar1;
  uint uVar2;
  int unaff_r7;
  
  if (*DAT_0041c49c == '\x01') {
    *DAT_0041c4a8 = *DAT_0041c4a8 & 0xffffffdf;
    uVar2 = 0;
    while ((uVar2 < 10000 && (*DAT_0041c4a0 << 0x18 < 0))) {
      uVar2 = uVar2 + 1;
    }
    if (uVar2 == 10000) {
      uVar1 = 4;
      goto LAB_0041be34;
    }
    unaff_r7 = *DAT_0041c4a0;
    FUN_0041cd1a(5,0,&stack0xfffffff8);
  }
  uVar1 = 0;
LAB_0041be34:
  return CONCAT44(unaff_r7,uVar1);
}

