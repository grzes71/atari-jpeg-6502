; RLE-based block decoder sketch for tests.
; Generated in MADS-compatible syntax.

        .ORG $C000
START
        LDX #$00
        LDY #$00
; read block tag
        LDA #$01
        STA $E000,X
        INX
; read block length
        LDA #$03
        STA $E000,X
        INX
; payload loop sketch: read bytes from the payload buffer
PAYLOAD_LOOP
        LDA $C000,Y
        STA $E000,X
        INX
        INY
        CPY #$03
        BNE PAYLOAD_LOOP
        CPX #$40
; RLE loop sketch: repeat count/value pairs until EOB
; count/value pair handling
; read count from payload
        LDA $C000,Y
        INY
; read value from payload
        LDA $C000,Y
        INY
; load value for image store
        LDA #$01
        STA $D000,X
        INX
        STA $D000,X
        INX
        STA $D000,X
        INX
; use count to drive the repeat loop
        LDY #$03
        DEY
        BNE LOOP
PAIR_LOOP
        LDA $C000,Y
        CMP #$FF
        BEQ DONE
        ; count/value pair iteration
        ; count-based repeat loop for image writes
        LDY #$03
LOOP
        LDA #$01
        STA $D000,X
        INX
        DEY
        BNE LOOP
        INY
        JMP PAIR_LOOP
DONE
        LDA #$03
        STA $E000,X
        INX
        LDA #$00
        STA $E000,X
        INX
        LDA #$02
        STA $E000,X
        INX
; second RLE pair
        LDA #$03
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
; count/value pair iteration
; count-based repeat loop for value writes
; repeat the value store for the RLE count
        LDY #$03
VALUE_LOOP
        LDA #$01
        STA $D000,X
        INX
        DEY
        BNE VALUE_LOOP
; store decoded values into image memory
        LDA #$00
        STA $D000,X
        INX
        STA $D000,X
        INX
        STA $D000,X
        INX
        RTS
