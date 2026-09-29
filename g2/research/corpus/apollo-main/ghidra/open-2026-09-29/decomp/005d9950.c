
undefined4 FUN_005d9950(void)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined4 in_r3;
  
  iVar1 = DAT_005d9b58;
  FUN_0043c0e4(DAT_005d9b58,0xa8,0);
  *(undefined4 *)(iVar1 + 0x10) = 3;
  *(undefined4 *)(iVar1 + 0x14) = 3;
  uVar2 = DAT_005d9b5c;
  *(undefined4 *)(iVar1 + 0x18) = DAT_005d9b5c;
  *(undefined4 *)(iVar1 + 0x1c) = DAT_005d9b60;
  *(undefined4 *)(iVar1 + 0x20) = 0x400;
  *(undefined4 *)(iVar1 + 0x28) = 0;
  *(undefined4 *)(iVar1 + 0x24) = 0;
  *(undefined4 *)(iVar1 + 0x2c) = 0;
  *(undefined4 *)(iVar1 + 0x60) = uVar2;
  *(undefined4 *)(iVar1 + 100) = DAT_005d9b64;
  *(undefined4 *)(iVar1 + 0x68) = 0x10;
  *(undefined4 *)(iVar1 + 0x70) = 0;
  *(undefined4 *)(iVar1 + 0x6c) = 0;
  *(undefined4 *)(iVar1 + 0x74) = 0;
  DataMemoryBarrier(0x1f);
  for (uVar3 = 0; uVar3 < 0x10; uVar3 = uVar3 + 1) {
    *(undefined1 *)(iVar1 + uVar3) = *(undefined1 *)((DAT_005d9b68 - uVar3) + 0xf);
  }
  DataMemoryBarrier(0x1f);
  return in_r3;
}

