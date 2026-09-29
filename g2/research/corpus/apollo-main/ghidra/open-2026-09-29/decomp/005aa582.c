
undefined4 af_latin_hints_init(int param_1,int param_2)

{
  char cVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  iVar4 = *(int *)(param_2 + 4);
  af_glyph_hints_rescale(param_1,param_2);
  *(undefined4 *)(param_1 + 4) = *(undefined4 *)(param_2 + 0x2c);
  *(undefined4 *)(param_1 + 8) = *(undefined4 *)(param_2 + 0x30);
  *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)(param_2 + 0x245c);
  *(undefined4 *)(param_1 + 0x10) = *(undefined4 *)(param_2 + 0x2460);
  cVar1 = *(char *)(param_2 + 0x18);
  uVar2 = *(uint *)(param_1 + 0xab4);
  uVar3 = 0;
  if ((cVar1 == '\x02') || (cVar1 == '\x03')) {
    uVar3 = 1;
  }
  if ((cVar1 == '\x02') || (cVar1 == '\x04')) {
    uVar3 = uVar3 | 2;
  }
  if ((cVar1 != '\x01') && (cVar1 != '\x03')) {
    uVar3 = uVar3 | 4;
  }
  if (cVar1 == '\x02') {
    uVar3 = uVar3 | 8;
  }
  if (((cVar1 == '\x01') || (cVar1 == '\x03')) || ((int)((uint)*(byte *)(iVar4 + 0xc) << 0x1f) < 0))
  {
    uVar2 = uVar2 | 1;
  }
  if (*(char *)(*(int *)(*(int *)(param_2 + 0x24) + 0x178) + 0x14) == '\0') {
    uVar2 = uVar2 | 8;
  }
  *(uint *)(param_1 + 0xab4) = uVar2;
  *(uint *)(param_1 + 0xab8) = uVar3;
  return 0;
}

