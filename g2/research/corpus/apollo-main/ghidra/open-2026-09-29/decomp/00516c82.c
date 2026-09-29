
void FUN_00516c82(undefined4 *param_1)

{
  int *piVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  
  piVar1 = DAT_00517850;
  *(undefined1 *)(*DAT_00517850 + 0x1bd) = *(undefined1 *)(*DAT_00517850 + 0x1bc);
  if (*(char *)(*piVar1 + 0x1bc) != '\0') {
    puVar2 = (undefined4 *)FUN_00514aec(7);
    if (puVar2 != (undefined4 *)0x0) {
      *puVar2 = 0x374;
      uVar3 = param_1[5];
      puVar2[2] = 0x368;
      puVar2[1] = uVar3;
      uVar3 = param_1[2];
      puVar2[4] = 0x360;
      puVar2[3] = uVar3;
      uVar3 = *param_1;
      puVar2[6] = 0x364;
      puVar2[5] = uVar3;
      uVar3 = param_1[1];
      puVar2[8] = 0x36c;
      puVar2[7] = uVar3;
      uVar3 = param_1[3];
      puVar2[10] = 0x370;
      puVar2[9] = uVar3;
      puVar2[0xb] = param_1[4];
      puVar2[0xc] = 0x388;
      puVar2[0xd] = 0;
    }
    *(undefined1 *)(*piVar1 + 0x1bc) = 0;
  }
  return;
}

