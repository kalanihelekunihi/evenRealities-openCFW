
int case_initialize_interrupt_path
              (uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  undefined4 *puVar2;
  int iVar3;
  uint uVar4;
  undefined1 auStack_24 [12];
  int local_18;
  undefined1 auStack_14 [8];
  
  puVar1 = DAT_08004f98;
  uVar4 = *DAT_08004f98;
  *DAT_08004f98 = uVar4 | 0x40000;
  case_clock_descriptor(auStack_24,auStack_14,uVar4 | 0x40000,param_4,*puVar1 & 0x40000);
  if (local_18 == 0) {
    iVar3 = case_shift_selected();
  }
  else {
    iVar3 = case_shift_selected();
    iVar3 = iVar3 << 1;
  }
  iVar3 = __aeabi_uidiv(iVar3,DAT_08004f9c);
  puVar2 = DAT_08004fa4;
  *DAT_08004fa4 = DAT_08004fa0;
  puVar2[3] = DAT_08004fa8;
  puVar2[1] = iVar3 + -1;
  puVar2[4] = 0;
  puVar2[2] = 0;
  puVar2[6] = 0;
  iVar3 = case_initialize_peripheral_context();
  if ((iVar3 == 0) && (iVar3 = case_enable_peripheral_context(DAT_08004fa4), iVar3 == 0)) {
    case_interrupt_enable(0x16);
    if (param_1 < 4) {
      case_forward_action(0x16,param_1,0);
      *DAT_08004fac = param_1;
    }
    else {
      iVar3 = 1;
    }
  }
  return iVar3;
}

