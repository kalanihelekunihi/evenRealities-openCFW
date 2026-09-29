
void FUN_08003bc8(void)

{
  undefined4 in_r3;
  undefined4 uStack_8;
  
  uStack_8 = in_r3;
  if (((*(uint *)(DAT_08003c14 + 0xc) & 1) == 0) && ((*(uint *)(DAT_08003c14 + 0x10) & 1) == 0)) {
    if (*DAT_08003c18 == '\0') {
      g2_log_printf(s_2217_int_08003c1c);
      g2_log_printf(&DAT_08003c28);
    }
    FUN_08003a84();
  }
  else {
    peripheral_transaction_guard(0x10,&uStack_8,1);
    peripheral_transaction_guard(0x11,&uStack_8,1);
  }
  case_dispatch_pending(1);
  case_dispatch_pending(2);
  return;
}

