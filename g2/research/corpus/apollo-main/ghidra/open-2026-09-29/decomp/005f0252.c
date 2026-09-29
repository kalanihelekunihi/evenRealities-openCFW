
void tt_loader_set_pp(int *param_1)

{
  bool bVar1;
  char cVar2;
  int iVar3;
  char cVar4;
  
  cVar4 = '\0';
  cVar2 = '\0';
  if (*(int *)(*(int *)(*param_1 + 0x60) + 0x40) == 0x28) {
    if (param_1[0x27] == 0) {
      cVar4 = '\0';
    }
    else {
      cVar4 = *(char *)(param_1[0x27] + 0x265);
    }
    if (param_1[0x27] == 0) {
      cVar2 = '\0';
    }
    else {
      cVar2 = *(char *)(param_1[0x27] + 0x26a);
    }
  }
  if ((cVar4 == '\0') || (cVar2 == '\0')) {
    bVar1 = false;
  }
  else {
    bVar1 = true;
  }
  param_1[0x11] = param_1[9] - param_1[0xd];
  param_1[0x12] = 0;
  param_1[0x13] = param_1[0xe] + param_1[0x11];
  param_1[0x14] = 0;
  if (bVar1) {
    iVar3 = param_1[0xe] / 2;
  }
  else {
    iVar3 = 0;
  }
  param_1[0x2d] = iVar3;
  param_1[0x2e] = param_1[0x2b] + param_1[0xc];
  if (bVar1) {
    iVar3 = param_1[0xe] / 2;
  }
  else {
    iVar3 = 0;
  }
  param_1[0x2f] = iVar3;
  param_1[0x30] = param_1[0x2e] - param_1[0x2c];
  return;
}

