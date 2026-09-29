
void touch_record_1b36_copy_gate
               (int param_1,undefined2 *param_2,undefined2 *param_3,undefined1 *param_4)

{
  *param_3 = *param_2;
  if ((param_4 != (undefined1 *)0x0) && ((*(ushort *)(param_1 + 0x74) & 0x300) == 0x200)) {
    *param_4 = 0;
  }
  return;
}

