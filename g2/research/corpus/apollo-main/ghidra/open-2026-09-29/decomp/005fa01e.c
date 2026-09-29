
void FUN_005fa01e(uint *param_1)

{
  uint *puVar1;
  uint uVar2;
  uint uVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  int unaff_r9;
  
  while( true ) {
    puVar1 = param_1 + 1;
    uVar3 = *param_1;
    if (uVar3 == 0) break;
    param_1 = param_1 + 2;
    puVar4 = (undefined4 *)*puVar1;
    if ((int)puVar4 << 0x1f < 0) {
      puVar4 = (undefined4 *)((int)puVar4 + unaff_r9 + -1);
    }
    do {
      puVar5 = puVar4;
      uVar2 = uVar3;
      puVar4 = puVar5 + 1;
      *puVar5 = 0;
      uVar3 = uVar2 - 4;
    } while (3 < uVar2 - 4);
    if ((int)(uVar2 * 0x40000000) < 0) {
      *(undefined2 *)puVar4 = 0;
      puVar4 = (undefined4 *)((int)puVar5 + 6);
    }
    if ((int)(uVar2 * -0x80000000) < 0) {
      *(undefined1 *)puVar4 = 0;
    }
  }
  return;
}

