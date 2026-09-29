
undefined4 FUN_0058f8e4(void)

{
  char cVar1;
  uint uVar2;
  undefined4 unaff_r7;
  uint in_fpscr;
  
  cVar1 = FUN_0045a570();
  if (cVar1 == '\x01') {
    uVar2 = FUN_00513748(0);
    VectorSignedToFloat((uVar2 & 0xfff) * (1 << ((uVar2 & 0xffff) >> 0xc)),
                        (byte)(in_fpscr >> 0x16) & 3);
  }
  return unaff_r7;
}

