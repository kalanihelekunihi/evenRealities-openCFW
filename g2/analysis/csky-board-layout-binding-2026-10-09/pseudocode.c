/* Partial reconstructed pseudocode; addresses bind original instructions.
 * Conditional board visibility; no production implementation or execution claim. */
board_view *board_get_10203004(void) { return (board_view *)0x200269A4; }
/* I2S branch within output setup 0x10207070; guarded by output bit 8.
 * 0x10207212 copies the last three words to the stack; 0x10207226 calls provider.
 */
void output_i2s_branch(board_view *b) {
 if (b->output_mask & 8) {
  gx_audio_in_set_output_i2s_10204228(b->i2s_out[0], b->i2s_out[1],
    b->i2s_out[2], b->i2s_out[3], b->i2s_out[4],
    b->i2s_out[5], b->i2s_out[6]);
  gx_audio_in_set_i2s_mode_10204340(0);
 }
}
