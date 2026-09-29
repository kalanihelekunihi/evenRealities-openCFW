
undefined8 parse_object(int param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int *piVar2;
  int iVar3;
  int *piVar4;
  int *piVar5;
  int *piVar6;
  
  piVar4 = (int *)0x0;
  if (999 < (uint)param_2[3]) {
    uVar1 = 0;
    goto LAB_004d820a;
  }
  param_2[3] = param_2[3] + 1;
  if (((param_2 != (int *)0x0) && ((uint)param_2[2] < (uint)param_2[1])) &&
     (*(char *)(*param_2 + param_2[2]) == '{')) {
    param_2[2] = param_2[2] + 1;
    buffer_skip_whitespace(param_2);
    if (((param_2 != (int *)0x0) && ((uint)param_2[2] < (uint)param_2[1])) &&
       (*(char *)(*param_2 + param_2[2]) == '}')) {
LAB_004d822e:
      param_2[3] = param_2[3] + -1;
      *(undefined4 *)(param_1 + 0xc) = 0x40;
      *(int **)(param_1 + 8) = piVar4;
      param_2[2] = param_2[2] + 1;
      uVar1 = 1;
      goto LAB_004d820a;
    }
    if ((param_2 == (int *)0x0) || ((uint)param_2[1] <= (uint)param_2[2])) {
      param_2[2] = param_2[2] + -1;
    }
    else {
      param_2[2] = param_2[2] + -1;
      piVar5 = piVar4;
      piVar6 = (int *)0x0;
      do {
        piVar2 = (int *)cJSON_New_Item(param_2 + 4);
        piVar4 = piVar5;
        if (piVar2 == (int *)0x0) goto LAB_004d81fe;
        piVar4 = piVar2;
        if (piVar5 != (int *)0x0) {
          *piVar6 = (int)piVar2;
          piVar2[1] = (int)piVar6;
          piVar4 = piVar5;
        }
        param_2[2] = param_2[2] + 1;
        buffer_skip_whitespace(param_2);
        iVar3 = parse_string(piVar2,param_2);
        if (iVar3 == 0) goto LAB_004d81fe;
        buffer_skip_whitespace(param_2);
        piVar2[8] = piVar2[4];
        piVar2[4] = 0;
        if (((param_2 == (int *)0x0) || ((uint)param_2[1] <= (uint)param_2[2])) ||
           (*(char *)(*param_2 + param_2[2]) != ':')) goto LAB_004d81fe;
        param_2[2] = param_2[2] + 1;
        buffer_skip_whitespace(param_2);
        iVar3 = parse_value(piVar2,param_2);
        if (iVar3 == 0) goto LAB_004d81fe;
        buffer_skip_whitespace(param_2);
      } while (((param_2 != (int *)0x0) && ((uint)param_2[2] < (uint)param_2[1])) &&
              (piVar5 = piVar4, piVar6 = piVar2, *(char *)(*param_2 + param_2[2]) == ','));
      if (((param_2 != (int *)0x0) && ((uint)param_2[2] < (uint)param_2[1])) &&
         (*(char *)(*param_2 + param_2[2]) == '}')) goto LAB_004d822e;
    }
  }
LAB_004d81fe:
  if (piVar4 != (int *)0x0) {
    cJSON_Delete(piVar4);
  }
  uVar1 = 0;
LAB_004d820a:
  return CONCAT44(param_4,uVar1);
}

