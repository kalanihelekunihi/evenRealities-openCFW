
undefined4 FUN_1000b6f0(void)

{
  int iVar1;
  
  iVar1 = DAT_1000b740;
  FUN_10004708(*(undefined4 *)(DAT_1000b740 + 8));
  FUN_10004724(*(undefined4 *)(iVar1 + 8));
  *(undefined4 *)(iVar1 + 0xc) = 0;
  FUN_10004708(*(undefined4 *)(iVar1 + 0x184));
  FUN_10004724(*(undefined4 *)(iVar1 + 0x184));
  *(undefined4 *)(iVar1 + 0x188) = 0;
  FUN_100113c4(iVar1 + 0x310,0,0x1c0);
  FUN_100113c4(DAT_1000b744,0,0x14);
  FUN_100113c4(iVar1,0,0x2f8);
  return 0;
}

