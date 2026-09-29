
undefined4 parse_number(int param_1,int *param_2)

{
  undefined1 uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  double dVar5;
  undefined1 *local_50;
  undefined1 local_4c [64];
  undefined4 extraout_s1;
  
  local_50 = (undefined1 *)0x0;
  uVar1 = get_decimal_point((int)DAT_004d7b38);
  if ((param_2 == (int *)0x0) || (*param_2 == 0)) {
    uVar2 = 0;
  }
  else {
    for (uVar3 = 0;
        ((uVar3 < 0x3f && (param_2 != (int *)0x0)) && (uVar3 + param_2[2] < (uint)param_2[1]));
        uVar3 = uVar3 + 1) {
      uVar4 = (uint)*(byte *)(*param_2 + param_2[2] + uVar3);
      if ((uVar4 == 0x2b) || (uVar4 == 0x2d)) {
LAB_004d7a86:
        local_4c[uVar3] = *(undefined1 *)(*param_2 + param_2[2] + uVar3);
      }
      else {
        if (uVar4 != 0x2e) {
          if (((uVar4 - 0x30 < 10) || (uVar4 == 0x45)) || (uVar4 - 0x30 == 0x35)) goto LAB_004d7a86;
          break;
        }
        local_4c[uVar3] = uVar1;
      }
    }
    local_4c[uVar3] = 0;
    uVar2 = FUN_00542d48(local_4c,&local_50);
    dVar5 = (double)CONCAT44(extraout_s1,uVar2);
    if (local_4c == local_50) {
      uVar2 = 0;
    }
    else {
      *(double *)(param_1 + 0x18) = dVar5;
      if (dVar5 < DAT_004d7b40) {
        if ((int)((uint)(dVar5 < DAT_004d7b48) << 0x1f) < 0) {
          *(undefined4 *)(param_1 + 0x14) = 0x80000000;
        }
        else {
          *(int *)(param_1 + 0x14) = (int)(longlong)dVar5;
        }
      }
      else {
        *(undefined4 *)(param_1 + 0x14) = 0x7fffffff;
      }
      *(undefined4 *)(param_1 + 0xc) = 8;
      param_2[2] = (int)(local_50 + (param_2[2] - (int)local_4c));
      uVar2 = 1;
    }
  }
  return uVar2;
}

