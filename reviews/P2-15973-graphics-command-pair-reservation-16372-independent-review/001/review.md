# Independent review 15973

Partial, accepted:false. Fresh replay passed for 138 bytes. Loads the global object, clears only bit 3 of byte +24, and selects ring mode from byte +8 bit 5. The ring branch keeps wrapped signed subtraction/division/multiply-add behavior and calls the flush child without using its result; the linear branch uses signed capacity arithmetic and the grow child. Both paths reload the object/buffer before advancing index by request*2 and publishing the updated word. The null/global and child boundaries remain opaque.

External child and hardware behavior remain unresolved; no admission or gate change.
