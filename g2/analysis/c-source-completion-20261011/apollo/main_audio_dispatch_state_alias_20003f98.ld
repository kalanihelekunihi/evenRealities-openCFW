/* One source-owned 16-byte record serves both native 0x53c638 facades.
 * The final RAM address and startup lifecycle remain separate gates. */
SECTIONS {}
PROVIDE(g2_audio_dispatch_state = g2_audio_control_context_20003f98);
ASSERT(g2_audio_dispatch_state == g2_audio_control_context_20003f98,
       "audio dispatch and control must share one record")
