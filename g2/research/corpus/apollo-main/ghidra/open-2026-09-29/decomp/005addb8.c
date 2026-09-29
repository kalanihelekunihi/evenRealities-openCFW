
char cff_fd_select_get(char *param_1,uint param_2)

{
  char cVar1;
  char cVar2;
  undefined1 *puVar3;
  char *pcVar4;
  char *pcVar5;
  uint uVar6;
  uint uVar7;
  
  cVar2 = '\0';
  if (*(int *)(param_1 + 8) != 0) {
    if (*param_1 == '\0') {
      cVar2 = *(char *)(*(int *)(param_1 + 8) + param_2);
    }
    else if (*param_1 == '\x03') {
      if (param_2 - *(int *)(param_1 + 0x10) < *(uint *)(param_1 + 0x14)) {
        cVar2 = param_1[0x18];
      }
      else {
        puVar3 = *(undefined1 **)(param_1 + 8);
        pcVar4 = puVar3 + 2;
        uVar6 = (uint)CONCAT11(*puVar3,puVar3[1]);
        do {
          if (param_2 < uVar6) {
            return '\0';
          }
          cVar1 = *pcVar4;
          pcVar5 = pcVar4 + 3;
          uVar7 = (uint)CONCAT11(pcVar4[1],pcVar4[2]);
          if (param_2 < uVar7) {
            *(uint *)(param_1 + 0x10) = uVar6;
            *(uint *)(param_1 + 0x14) = uVar7 - uVar6;
            param_1[0x18] = cVar1;
            return cVar1;
          }
          pcVar4 = pcVar5;
          uVar6 = uVar7;
        } while (pcVar5 < puVar3 + *(int *)(param_1 + 0xc));
      }
    }
  }
  return cVar2;
}

