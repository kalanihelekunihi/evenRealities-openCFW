
undefined * text_stream_pending_text(int param_1)

{
  undefined *puVar1;
  
  if (param_1 == 0) {
    puVar1 = &DAT_00552cf4;
  }
  else {
    puVar1 = *(undefined **)(param_1 + 4);
  }
  return puVar1;
}

