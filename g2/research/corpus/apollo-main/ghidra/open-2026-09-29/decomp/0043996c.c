
void FUN_0043996c(uint *param_1,int param_2)

{
  undefined1 uVar1;
  uint uVar2;
  uint uVar3;
  undefined1 *puVar4;
  char *pcVar5;
  
  if ((*param_1 < 0xff0000) || (param_1[3] != 0)) {
    uVar3 = param_1[2];
    if (-1 < (int)uVar3) {
      uVar2 = param_1[3];
      pcVar5 = *(char **)(param_2 + 8);
      if (pcVar5 < *(char **)(param_2 + 4)) {
        *(char **)(param_2 + 8) = pcVar5 + 1;
        *pcVar5 = (char)uVar2 + (char)uVar3;
      }
    }
    uVar3 = param_1[4];
    while (0 < (int)uVar3) {
      if (param_1[3] == 0) {
        uVar1 = 0xff;
      }
      else {
        uVar1 = 0;
      }
      puVar4 = *(undefined1 **)(param_2 + 8);
      if (puVar4 < *(undefined1 **)(param_2 + 4)) {
        *(undefined1 **)(param_2 + 8) = puVar4 + 1;
        *puVar4 = uVar1;
      }
      uVar3 = param_1[4] - 1;
      param_1[4] = uVar3;
    }
    param_1[3] = 0;
    param_1[2] = *param_1 >> 0x10;
  }
  else {
    param_1[4] = param_1[4] + 1;
  }
  *param_1 = (*param_1 & 0xffff) << 8;
  return;
}

