
undefined4 TT_Load_Glyph_Header(int param_1)

{
  undefined4 uVar1;
  undefined1 *puVar2;
  
  puVar2 = *(undefined1 **)(param_1 + 0xc4);
  if (*(undefined1 **)(param_1 + 200) < puVar2 + 10) {
    uVar1 = 0x14;
  }
  else {
    *(ushort *)(param_1 + 0x20) = CONCAT11(*puVar2,puVar2[1]);
    *(int *)(param_1 + 0x24) = (int)CONCAT11(puVar2[2],puVar2[3]);
    *(int *)(param_1 + 0x28) = (int)CONCAT11(puVar2[4],puVar2[5]);
    *(int *)(param_1 + 0x2c) = (int)CONCAT11(puVar2[6],puVar2[7]);
    *(int *)(param_1 + 0x30) = (int)CONCAT11(puVar2[8],puVar2[9]);
    *(undefined1 **)(param_1 + 0xc4) = puVar2 + 10;
    uVar1 = 0;
  }
  return uVar1;
}

