
undefined2 FT_Stream_GetUShort(int param_1)

{
  undefined2 uVar1;
  undefined1 *puVar2;
  undefined1 *puVar3;
  
  uVar1 = 0;
  puVar2 = *(undefined1 **)(param_1 + 0x20);
  puVar3 = puVar2;
  if (puVar2 + 1 < *(undefined1 **)(param_1 + 0x24)) {
    puVar3 = puVar2 + 2;
    uVar1 = CONCAT11(*puVar2,puVar2[1]);
  }
  *(undefined1 **)(param_1 + 0x20) = puVar3;
  return uVar1;
}

