
int putchw(undefined4 param_1,int *param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  char *pcVar4;
  int iVar5;
  int iVar6;
  
  pcVar4 = (char *)param_2[3];
  for (iVar5 = *param_2; (*pcVar4 != '\0' && (pcVar4 = pcVar4 + 1, 0 < iVar5)); iVar5 = iVar5 + -1)
  {
  }
  if (*(char *)((int)param_2 + 5) != '\0') {
    iVar5 = iVar5 + -1;
  }
  if (*(char *)((int)param_2 + 6) != '\0') {
    if (*(char *)((int)param_2 + 7) == '\x10') {
      iVar5 = iVar5 + -2;
    }
    else if (*(char *)((int)param_2 + 7) == '\b') {
      iVar5 = iVar5 + -1;
    }
  }
  if ((char)param_2[1] == '\0') {
    iVar6 = 0;
    for (iVar1 = iVar5; 0 < iVar1; iVar1 = iVar1 + -1) {
      iVar2 = putf(param_1,0x20);
      iVar6 = iVar6 + iVar2;
    }
    iVar5 = (iVar5 + -1) - (uint)(-1 < iVar5) * iVar5;
  }
  else {
    iVar6 = 0;
  }
  if (*(char *)((int)param_2 + 5) != '\0') {
    iVar1 = putf(param_1);
    iVar6 = iVar6 + iVar1;
  }
  if (*(char *)((int)param_2 + 6) != '\0') {
    if (*(char *)((int)param_2 + 7) == '\x10') {
      iVar1 = putf(param_1,0x30);
      uVar3 = 0x58;
      iVar6 = iVar6 + iVar1;
      if ((char)param_2[2] == '\0') {
        uVar3 = 0x78;
      }
    }
    else {
      if (*(char *)((int)param_2 + 7) != '\b') goto LAB_10206a24;
      uVar3 = 0x30;
    }
    iVar1 = putf(param_1,uVar3);
    iVar6 = iVar6 + iVar1;
  }
LAB_10206a24:
  if ((char)param_2[1] != '\0') {
    for (; 0 < iVar5; iVar5 = iVar5 + -1) {
      iVar1 = putf(param_1,0x30);
      iVar6 = iVar6 + iVar1;
    }
  }
  pcVar4 = (char *)param_2[3];
  while (*pcVar4 != '\0') {
    iVar5 = putf(param_1);
    iVar6 = iVar6 + iVar5;
    pcVar4 = pcVar4 + 1;
  }
  return iVar6;
}

