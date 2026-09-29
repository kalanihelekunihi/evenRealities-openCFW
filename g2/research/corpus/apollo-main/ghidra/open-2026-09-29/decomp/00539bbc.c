
longlong FUN_00539bbc(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  undefined1 uVar4;
  uint uVar5;
  uint local_20;
  
  local_20 = CONCAT31((int3)((uint)param_4 >> 8),2);
  bVar1 = FUN_00539348(param_1);
  uVar5 = FUN_00539352(param_1);
  FUN_00539c9a(bVar1,&local_20);
  bVar2 = FUN_00539372(local_20 & 0xff);
  bVar3 = FUN_00539372(param_1);
  uVar4 = FUN_0053935c(bVar1);
  FUN_0044b0d6(uVar4,bVar2 | bVar3);
  if (bVar1 == 0) {
    *DAT_00539dc4 = *DAT_00539dc4 & 0xfffffffc | uVar5 & 3;
  }
  else if (bVar1 == 2) {
    *DAT_00539dc4 = *DAT_00539dc4 & 0xffffffef | (uVar5 & 1) << 4;
  }
  else if (bVar1 < 2) {
    *DAT_00539dc4 = *DAT_00539dc4 & 0xfffffff3 | (uVar5 & 3) << 2;
  }
  else if (bVar1 == 4) {
    *DAT_00539dc4 = *DAT_00539dc4 & 0xfffffe7f | (uVar5 & 3) << 7;
  }
  else if (bVar1 < 4) {
    *DAT_00539dc4 = *DAT_00539dc4 & 0xffffff9f | (uVar5 & 3) << 5;
  }
  FUN_004807a0(param_2);
  FUN_0044b0d6(uVar4,bVar3);
  return (ulonglong)local_20 << 0x20;
}

