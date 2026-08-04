; Block decoder sketch

        ORG $C000
START
        LDX #$00
        LDA #$01
        STA $E000,X
        INX
        LDA #$03
        STA $E000,X
        INX
        LDA #$03
        STA $E000,X
        INX
        LDA #$00
        STA $E000,X
        INX
        LDA #$02
        STA $E000,X
        INX
        LDA #$04
        STA $E000,X
        INX
        LDA #$FF
        STA $E000,X
        INX
        LDA #$00
        STA $E000,X
        INX
        LDA #$00
        STA $E000,X
        INX
        LDA #$00
        STA $E000,X
        INX
        LDA #$00
        STA $E000,X
        INX
        RTS
