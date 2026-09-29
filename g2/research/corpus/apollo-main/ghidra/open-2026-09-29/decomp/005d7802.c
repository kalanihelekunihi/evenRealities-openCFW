
void FUN_005d7802(uint *param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  byte bVar5;
  
  uVar1 = param_1[2];
  iVar2 = *(int *)(param_1[5] + 4);
  iVar4 = *(int *)(param_1[5] + 8);
  for (uVar3 = 0; uVar3 < *param_1; uVar3 = uVar3 + 1) {
    if (param_2 == 0) {
      *(undefined4 *)(iVar2 + uVar3 * 8) = *(undefined4 *)(uVar1 + 0x24);
    }
    else {
      *(undefined4 *)(iVar2 + uVar3 * 8 + 4) = *(undefined4 *)(uVar1 + 0x24);
    }
    if ((int)((uint)*(byte *)(uVar1 + 0x10) << 0x1b) < 0) {
      if (param_2 == 0) {
        bVar5 = 0x20;
      }
      else {
        bVar5 = 0x40;
      }
      *(byte *)(iVar4 + uVar3) = bVar5 | *(byte *)(iVar4 + uVar3);
    }
    uVar1 = uVar1 + 0x28;
  }
  return;
}

