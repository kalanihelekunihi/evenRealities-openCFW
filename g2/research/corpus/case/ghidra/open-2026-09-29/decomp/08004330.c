
void FUN_08004330(int *param_1)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = *(int *)*param_1;
  iVar3 = ((int *)*param_1)[1];
  if ((iVar4 << 0x1e < 0) && (iVar3 << 0x1e < 0)) {
    if (-1 < param_1[0x16] << 0x1b) {
      param_1[0x16] = param_1[0x16] | 0x800;
    }
    case_hook_080040fa(param_1);
    *(undefined4 *)*param_1 = 2;
  }
  uVar1 = DAT_0800447c;
  if (((iVar4 << 0x1d < 0) && (iVar3 << 0x1d < 0)) || ((iVar4 << 0x1c < 0 && (iVar3 << 0x1c < 0))))
  {
    if (-1 < param_1[0x16] << 0x1b) {
      param_1[0x16] = param_1[0x16] | 0x200;
    }
    iVar2 = case_status_word3_field10_clear(*param_1);
    if ((iVar2 != 0) && (*(char *)((int)param_1 + 0x1a) == '\0')) {
      if (*(int *)*param_1 << 0x1c < 0) {
        iVar2 = case_status_word2_bit2();
        if (iVar2 == 0) {
          *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xfffffff3;
          param_1[0x16] = param_1[0x16] & ~uVar1 | 1;
        }
        else {
          param_1[0x16] = param_1[0x16] | 0x20;
          param_1[0x17] = param_1[0x17] | 1;
        }
      }
    }
    case_hook_08004324(param_1);
    *(undefined4 *)*param_1 = 0xc;
  }
  if ((iVar4 << 0x18 < 0) && (iVar3 << 0x18 < 0)) {
    param_1[0x16] = param_1[0x16] | 0x10000;
    case_hook_080046a0(param_1);
    *(undefined4 *)*param_1 = 0x80;
  }
  if ((iVar4 << 0x17 < 0) && (iVar3 << 0x17 < 0)) {
    param_1[0x16] = param_1[0x16] | 0x20000;
    case_hook_080040fc(param_1);
    *(uint *)*param_1 = uVar1;
  }
  if ((iVar4 << 0x16 < 0) && (iVar3 << 0x16 < 0)) {
    param_1[0x16] = param_1[0x16] | 0x40000;
    case_hook_080040fe(param_1);
    *(undefined4 *)*param_1 = 0x200;
  }
  if ((iVar4 << 0x1b < 0) && (iVar3 << 0x1b < 0)) {
    if ((param_1[0xc] == 0) || ((*(uint *)(*param_1 + 0xc) & 3) != 0)) {
      param_1[0x16] = param_1[0x16] | 0x400;
      param_1[0x17] = param_1[0x17] | 2;
      case_hook_08004326(param_1);
    }
    *(undefined4 *)*param_1 = 0x10;
  }
  if ((iVar4 << 0x12 < 0) && (iVar3 << 0x12 < 0)) {
    case_hook_080040f8(param_1);
    *(undefined4 *)*param_1 = 0x2000;
  }
  return;
}

