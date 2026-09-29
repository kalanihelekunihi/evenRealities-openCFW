
void FUN_004b1298(int param_1,uint param_2,uint param_3,int param_4,uint param_5,uint param_6,
                 int param_7)

{
  int *piVar1;
  undefined1 uVar2;
  uint uVar3;
  int *piVar4;
  uint uVar5;
  int iVar6;
  
  piVar1 = DAT_004b178c;
  if (param_1 < 0) {
    return;
  }
  uVar5 = param_2;
  if (param_6 != 0xffffffff) goto LAB_004b13d0;
  uVar5 = param_5 & 0x7f;
  param_6 = param_3;
  if (param_7 << 0x1b < 0) {
    param_6 = param_3 + 3 + ((uint)((int)(param_3 + 3) >> 1) >> 0x1e) & 0xfffffffc;
  }
  if ((uVar5 == 0x12 || uVar5 == 0x16) || (uVar5 == 0x17 || uVar5 == 0x4e)) {
    param_6 = param_6 + 3 + ((uint)((int)(param_6 + 3) >> 1) >> 0x1e) & 0xfffffffc;
  }
  if (uVar5 == 0x4c || uVar5 == 0x4d) {
    param_6 = (param_6 + 1) - ((int)(param_6 + 1) >> 0x1f) & 0xfffffffe;
  }
  switch(uVar5) {
  case 0xb:
  case 0xc:
  case 0x27:
  case 0x2a:
    goto switchD_004b1308_caseD_b;
  default:
    iVar6 = 4;
    switch(uVar5) {
    case 4:
    case 5:
    case 6:
    case 0xd:
    case 0x13:
    case 0x1d:
    case 0x3d:
    case 0x3e:
    case 0x3f:
    case 0x44:
    case 0x46:
    case 0x47:
    case 0x48:
    case 0x49:
    case 0x4a:
    case 0x4b:
    case 0x4c:
    case 0x4d:
      iVar6 = 2;
      break;
    case 7:
    case 8:
    case 9:
    case 0xc:
    case 0x12:
    case 0x16:
    case 0x17:
    case 0x18:
    case 0x19:
    case 0x1a:
    case 0x27:
    case 0x28:
    case 0x30:
    case 0x31:
    case 0x34:
    case 0x35:
    case 0x38:
    case 0x40:
    case 0x41:
    case 0x42:
    case 0x43:
    case 0x45:
    case 0x4e:
      iVar6 = 1;
      break;
    case 0x39:
    case 0x3c:
      iVar6 = 3;
    }
    param_6 = iVar6 * param_6;
    uVar5 = uVar5 - 4;
    break;
  case 0x12:
    param_6 = param_6 << 1;
    break;
  case 0x16:
  case 0x17:
  case 0x4c:
  case 0x4d:
  case 0x4e:
    param_6 = param_6 * 3;
    break;
  case 0x28:
  case 0x2b:
  case 0x30:
  case 0x31:
    param_6 = param_6 << 1;
    goto switchD_004b1308_caseD_b;
  case 0x29:
  case 0x2c:
  case 0x34:
  case 0x35:
    param_6 = param_6 << 2;
switchD_004b1308_caseD_b:
    uVar5 = (int)(param_6 + 7) >> 2;
    param_6 = (int)(param_6 + 7 + (uVar5 >> 0x1d)) >> 3;
  }
LAB_004b13d0:
  if (param_1 == 0) {
    uVar3 = param_5 & 0x7f;
    if (uVar3 != 0x12) {
      uVar5 = param_5 & 0x7f;
    }
    if ((uVar3 != 0x12 && uVar5 != 0x16) && uVar3 != 0x17) {
      if (uVar5 == 0x4c || uVar3 == 0x4d) {
        *(undefined1 *)(*DAT_004b178c + 8) = 1;
        FUN_0052264e(1);
        goto LAB_004b1410;
      }
      uVar2 = *(undefined1 *)(*DAT_004b178c + 9);
    }
    else {
      uVar2 = 1;
      *(undefined1 *)(*DAT_004b178c + 8) = 1;
    }
    FUN_0052262e(uVar2);
  }
LAB_004b1410:
  iVar6 = param_1 * 0x18 + *piVar1;
  *(uint *)(iVar6 + 0x38) = param_2;
  *(uint *)(iVar6 + 0x3c) = param_3;
  *(int *)(iVar6 + 0x40) = param_4;
  *(uint *)(iVar6 + 0x44) = param_7 << 0x10 | param_5 << 0x18 | param_6 & 0xffff;
  *(undefined4 *)(iVar6 + 0x48) = 1;
  *(uint *)(iVar6 + 0x4c) = param_5;
  iVar6 = param_1 * 0x10;
  piVar4 = (int *)FUN_00514aec(3);
  if (piVar4 != (int *)0x0) {
    *piVar4 = iVar6;
    piVar4[1] = param_2;
    piVar4[2] = iVar6 + 4;
    piVar4[3] = *(int *)(param_1 * 0x18 + *piVar1 + 0x44);
    piVar4[4] = iVar6 + 8;
    piVar4[5] = param_3 | param_4 << 0x10;
  }
  return;
}

