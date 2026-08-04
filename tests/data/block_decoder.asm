; DC-only decoder sketch for tests.
; Generated in MADS-compatible syntax.

        ORG $C000
START
        LDY #$00
        LDA #$00
LOOP
        STA $E000,Y
        INY
        CPY #$40
        BNE LOOP
        RTS
