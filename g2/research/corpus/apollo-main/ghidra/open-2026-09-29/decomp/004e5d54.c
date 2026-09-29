
undefined8 even_ai_scroll_needed(void)

{
  int *piVar1;
  ushort uVar2;
  ushort uVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 in_r3;
  
  piVar1 = DAT_004e5f90;
  if (*DAT_004e607c == '\x01') {
    uVar4 = 0;
  }
  else {
    if ((*DAT_004e5f90 != 0) && (iVar5 = text_stream_pending_text(*DAT_004e5f90), iVar5 != 0)) {
      uVar2 = text_stream_pending_length(*piVar1);
      uVar3 = text_stream_current_length(*piVar1);
      if (uVar3 < uVar2) {
        uVar4 = 0;
        goto LAB_004e5d92;
      }
    }
    uVar4 = 1;
  }
LAB_004e5d92:
  return CONCAT44(in_r3,uVar4);
}

