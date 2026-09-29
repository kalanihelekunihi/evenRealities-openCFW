
void cff_sid_to_glyph_name(int param_1,int param_2)

{
  cff_index_get_sid_string
            (*(int *)(param_1 + 0x2a4),
             *(undefined2 *)(*(int *)(*(int *)(param_1 + 0x2a4) + 0x4a4) + param_2 * 2));
  return;
}

