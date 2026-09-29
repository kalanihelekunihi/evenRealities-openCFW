
undefined8 parse_string(int param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  char *pcVar2;
  byte bVar3;
  undefined4 uVar4;
  int iVar5;
  char *pcVar6;
  char *pcVar7;
  char *pcVar8;
  char *local_20;
  undefined4 uStack_1c;
  
  pcVar7 = (char *)(*param_2 + param_2[2] + 1);
  local_20 = (char *)0x0;
  pcVar6 = (char *)0x0;
  uStack_1c = param_4;
  if (*(char *)(*param_2 + param_2[2]) == '\"') {
    iVar5 = 0;
    pcVar8 = (char *)(*param_2 + param_2[2]);
    while ((pcVar2 = pcVar8, pcVar8 = pcVar2 + 1, (uint)((int)pcVar8 - *param_2) < (uint)param_2[1]
           && (*pcVar8 != '\"'))) {
      if (*pcVar8 == '\\') {
        if ((char *)param_2[1] <= pcVar2 + (2 - *param_2)) goto LAB_004d7cba;
        iVar5 = iVar5 + 1;
        pcVar8 = pcVar2 + 2;
      }
    }
    if ((((uint)((int)pcVar8 - *param_2) < (uint)param_2[1]) && (*pcVar8 == '\"')) &&
       (pcVar6 = (char *)(*(code *)param_2[4])(pcVar8 + (-iVar5 - (*param_2 + param_2[2])) + 1),
       pcVar2 = pcVar6, pcVar6 != (char *)0x0)) {
      while (local_20 = pcVar2, pcVar7 < pcVar8) {
        if (*pcVar7 == '\\') {
          bVar3 = 2;
          if ((int)pcVar8 - (int)pcVar7 < 1) goto LAB_004d7cba;
          cVar1 = pcVar7[1];
          if (((cVar1 == '\"') || (cVar1 == '/')) || (cVar1 == '\\')) {
            *local_20 = pcVar7[1];
            local_20 = local_20 + 1;
          }
          else if (cVar1 == 'b') {
            *local_20 = '\b';
            local_20 = local_20 + 1;
          }
          else if (cVar1 == 'f') {
            *local_20 = '\f';
            local_20 = local_20 + 1;
          }
          else if (cVar1 == 'n') {
            *local_20 = '\n';
            local_20 = local_20 + 1;
          }
          else if (cVar1 == 'r') {
            *local_20 = '\r';
            local_20 = local_20 + 1;
          }
          else if (cVar1 == 't') {
            *local_20 = '\t';
            local_20 = local_20 + 1;
          }
          else if ((cVar1 != 'u') ||
                  (bVar3 = utf16_literal_to_utf8(pcVar7,pcVar8,&local_20), bVar3 == 0))
          goto LAB_004d7cba;
          pcVar7 = pcVar7 + bVar3;
          pcVar2 = local_20;
        }
        else {
          *local_20 = *pcVar7;
          pcVar7 = pcVar7 + 1;
          pcVar2 = local_20 + 1;
        }
      }
      *local_20 = '\0';
      *(undefined4 *)(param_1 + 0xc) = 0x10;
      *(char **)(param_1 + 0x10) = pcVar6;
      param_2[2] = (int)pcVar8 - *param_2;
      param_2[2] = param_2[2] + 1;
      uVar4 = 1;
      goto LAB_004d7cd0;
    }
  }
LAB_004d7cba:
  if (pcVar6 != (char *)0x0) {
    (*(code *)param_2[5])(pcVar6);
  }
  if (pcVar7 != (char *)0x0) {
    param_2[2] = (int)pcVar7 - *param_2;
  }
  uVar4 = 0;
LAB_004d7cd0:
  return CONCAT44(local_20,uVar4);
}

