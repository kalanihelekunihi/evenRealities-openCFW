
void cff_make_private_dict(int param_1,int param_2)

{
  byte bVar1;
  uint uVar2;
  undefined1 *puVar3;
  
  puVar3 = (undefined1 *)(param_1 + 0xbc);
  FUN_0043c0e4(param_2,0xc4,0);
  *(undefined1 *)(param_2 + 8) = *puVar3;
  bVar1 = *(byte *)(param_2 + 8);
  for (uVar2 = 0; uVar2 < bVar1; uVar2 = uVar2 + 1) {
    *(short *)(param_2 + uVar2 * 2 + 0xc) = (short)*(undefined4 *)(puVar3 + uVar2 * 4 + 4);
  }
  *(undefined1 *)(param_2 + 9) = *(undefined1 *)(param_1 + 0xbd);
  bVar1 = *(byte *)(param_2 + 9);
  for (uVar2 = 0; uVar2 < bVar1; uVar2 = uVar2 + 1) {
    *(short *)(param_2 + uVar2 * 2 + 0x28) = (short)*(undefined4 *)(puVar3 + uVar2 * 4 + 0x3c);
  }
  *(undefined1 *)(param_2 + 10) = *(undefined1 *)(param_1 + 0xbe);
  bVar1 = *(byte *)(param_2 + 10);
  for (uVar2 = 0; uVar2 < bVar1; uVar2 = uVar2 + 1) {
    *(short *)(param_2 + uVar2 * 2 + 0x3c) = (short)*(undefined4 *)(puVar3 + uVar2 * 4 + 100);
  }
  *(undefined1 *)(param_2 + 0xb) = *(undefined1 *)(param_1 + 0xbf);
  bVar1 = *(byte *)(param_2 + 0xb);
  for (uVar2 = 0; uVar2 < bVar1; uVar2 = uVar2 + 1) {
    *(short *)(param_2 + uVar2 * 2 + 0x58) = (short)*(undefined4 *)(puVar3 + uVar2 * 4 + 0x9c);
  }
  *(undefined4 *)(param_2 + 0x6c) = *(undefined4 *)(param_1 + 0x180);
  *(undefined4 *)(param_2 + 0x70) = *(undefined4 *)(param_1 + 0x184);
  *(undefined4 *)(param_2 + 0x74) = *(undefined4 *)(param_1 + 0x188);
  *(short *)(param_2 + 0x78) = (short)*(undefined4 *)(param_1 + 0x18c);
  *(short *)(param_2 + 0x7a) = (short)*(undefined4 *)(param_1 + 400);
  *(undefined1 *)(param_2 + 0x7c) = *(undefined1 *)(param_1 + 0x194);
  bVar1 = *(byte *)(param_2 + 0x7c);
  for (uVar2 = 0; uVar2 < bVar1; uVar2 = uVar2 + 1) {
    *(short *)(param_2 + uVar2 * 2 + 0x80) = (short)*(undefined4 *)(puVar3 + uVar2 * 4 + 0xdc);
  }
  *(undefined1 *)(param_2 + 0x7d) = *(undefined1 *)(param_1 + 0x195);
  bVar1 = *(byte *)(param_2 + 0x7d);
  for (uVar2 = 0; uVar2 < bVar1; uVar2 = uVar2 + 1) {
    *(short *)(param_2 + uVar2 * 2 + 0x9a) = (short)*(undefined4 *)(puVar3 + uVar2 * 4 + 0x110);
  }
  *(undefined1 *)(param_2 + 0x7e) = *(undefined1 *)(param_1 + 0x200);
  *(undefined4 *)(param_2 + 0xb8) = *(undefined4 *)(param_1 + 0x20c);
  *(undefined4 *)(param_2 + 4) = *(undefined4 *)(param_1 + 0x208);
  return;
}

