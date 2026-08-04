; Block-format decoder sketch for tests.
; Generated in MADS-compatible syntax.

        ORG $C000
START
        LDX #$00
        LDA #$01
        STA $E000,X
        INX
        LDA #$40
        STA $E000,X
        INX
        LDA #$00
        STA $E000,X
        INX
        RTS
