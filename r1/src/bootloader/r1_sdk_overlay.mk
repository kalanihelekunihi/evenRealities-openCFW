# Append the R1 configuration without replacing the Nordic example's CFLAGS.
# Invoke after the vendor Makefile, for example:
#   make -f Makefile -f /absolute/path/r1_sdk_overlay.mk \
#        R1_OVERLAY_DIR=/absolute/path/to/sdk-overlay

ifndef R1_OVERLAY_DIR
$(error R1_OVERLAY_DIR must name the absolute sdk-overlay directory)
endif

override CFLAGS += -include $(R1_OVERLAY_DIR)/r1_sdk_overrides.h
