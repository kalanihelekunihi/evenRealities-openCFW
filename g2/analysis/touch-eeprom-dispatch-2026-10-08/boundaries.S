/* Linkable guarded test boundaries, not provider implementations. */
.syntax unified
.thumb
.global eeprom_simple_boundary
.thumb_func
eeprom_simple_boundary:
 bkpt #0
 bx lr
.global eeprom_extended_boundary
.thumb_func
eeprom_extended_boundary:
 bkpt #0
 bx lr
