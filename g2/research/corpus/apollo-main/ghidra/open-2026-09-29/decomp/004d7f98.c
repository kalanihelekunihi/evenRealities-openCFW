
undefined8 parse_value(int param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  if ((param_2 == (int *)0x0) || (*param_2 == 0)) {
    uVar1 = 0;
  }
  else if ((param_2 == (int *)0x0) ||
          (((uint)param_2[1] < param_2[2] + 4U ||
           (iVar2 = FUN_0044b610(*param_2 + param_2[2],DAT_004d80d0,4), iVar2 != 0)))) {
    if ((param_2 == (int *)0x0) ||
       (((uint)param_2[1] < param_2[2] + 5U ||
        (iVar2 = FUN_0044b610(*param_2 + param_2[2],DAT_004d83b4,5), iVar2 != 0)))) {
      if ((param_2 == (int *)0x0) ||
         (((uint)param_2[1] < param_2[2] + 4U ||
          (iVar2 = FUN_0044b610(*param_2 + param_2[2],DAT_004d83b8,4), iVar2 != 0)))) {
        if ((param_2 == (int *)0x0) ||
           (((uint)param_2[1] <= (uint)param_2[2] || (*(char *)(*param_2 + param_2[2]) != '\"')))) {
          if (((param_2 == (int *)0x0) || ((uint)param_2[1] <= (uint)param_2[2])) ||
             ((*(char *)(*param_2 + param_2[2]) != '-' &&
              (9 < *(byte *)(*param_2 + param_2[2]) - 0x30)))) {
            if ((param_2 == (int *)0x0) ||
               (((uint)param_2[1] <= (uint)param_2[2] || (*(char *)(*param_2 + param_2[2]) != '[')))
               ) {
              if ((param_2 == (int *)0x0) ||
                 (((uint)param_2[1] <= (uint)param_2[2] || (*(char *)(*param_2 + param_2[2]) != '{')
                  ))) {
                uVar1 = 0;
              }
              else {
                uVar1 = parse_object(param_1,param_2);
              }
            }
            else {
              uVar1 = parse_array(param_1,param_2);
            }
          }
          else {
            uVar1 = parse_number(param_1,param_2);
          }
        }
        else {
          uVar1 = parse_string(param_1,param_2);
        }
      }
      else {
        *(undefined4 *)(param_1 + 0xc) = 2;
        *(undefined4 *)(param_1 + 0x14) = 1;
        param_2[2] = param_2[2] + 4;
        uVar1 = 1;
      }
    }
    else {
      *(undefined4 *)(param_1 + 0xc) = 1;
      param_2[2] = param_2[2] + 5;
      uVar1 = 1;
    }
  }
  else {
    *(undefined4 *)(param_1 + 0xc) = 4;
    param_2[2] = param_2[2] + 4;
    uVar1 = 1;
  }
  return CONCAT44(param_4,uVar1);
}

