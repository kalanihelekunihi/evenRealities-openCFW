
int FUN_0048d3c8(int param_1,char param_2,char param_3,int param_4,uint param_5,int param_6,
                int *param_7,char param_8)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = 0;
  if (param_2 == '\0') {
    if ((((param_3 == '\x05') || (param_3 == '\x06')) || (param_3 == '\x04')) &&
       (param_4 = 0, param_5 == 1)) {
      param_3 = '\x01';
    }
    for (uVar1 = 0; uVar1 < param_5; uVar1 = uVar1 + 1) {
      iVar4 = param_4 + *(int *)(param_6 + uVar1 * 4) + iVar4;
    }
    iVar4 = iVar4 - param_4;
    if (param_3 == '\0') {
      *param_7 = 0;
    }
    else if (param_3 == '\x01') {
      *param_7 = (param_1 - iVar4) / 2;
    }
    else if (param_3 == '\x02') {
      *param_7 = param_1 - iVar4;
    }
    else if (param_3 == '\x04') {
      param_4 = (param_1 - iVar4) / (int)(param_5 + 1);
      *param_7 = param_4;
    }
    else if (param_3 == '\x05') {
      param_4 = (param_1 - iVar4) / (int)param_5;
      *param_7 = param_4 / 2;
    }
    else if (param_3 == '\x06') {
      *param_7 = 0;
      param_4 = (param_1 - iVar4) / (int)(param_5 - 1);
    }
  }
  else {
    *param_7 = 0;
  }
  for (uVar1 = 0; uVar1 < param_5 - 1; uVar1 = uVar1 + 1) {
    param_7[uVar1 + 1] = param_4 + *(int *)(param_6 + uVar1 * 4) + param_7[uVar1];
  }
  iVar2 = param_7[param_5 - 1];
  iVar4 = *(int *)(param_6 + param_5 * 4 + -4);
  iVar3 = *param_7;
  if (param_8 != '\0') {
    for (uVar1 = 0; uVar1 < param_5; uVar1 = uVar1 + 1) {
      param_7[uVar1] = (param_1 - param_7[uVar1]) - *(int *)(param_6 + uVar1 * 4);
    }
  }
  return (iVar4 + iVar2) - iVar3;
}

