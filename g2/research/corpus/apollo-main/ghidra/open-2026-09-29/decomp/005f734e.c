
void Ins_UTP(int param_1,uint *param_2)

{
  uint uVar1;
  byte bVar2;
  
  uVar1 = *param_2;
  if ((uVar1 & 0xffff) < (uint)*(ushort *)(param_1 + 0x2c)) {
    bVar2 = 0xff;
    if (*(short *)(param_1 + 0x12e) != 0) {
      bVar2 = 0xf7;
    }
    if (*(short *)(param_1 + 0x130) != 0) {
      bVar2 = bVar2 & 0xef;
    }
    *(byte *)(*(int *)(param_1 + 0x3c) + (uVar1 & 0xffff)) =
         bVar2 & *(byte *)(*(int *)(param_1 + 0x3c) + (uVar1 & 0xffff));
  }
  else if (*(char *)(param_1 + 0x235) != '\0') {
    *(undefined4 *)(param_1 + 0xc) = 0x86;
  }
  return;
}

