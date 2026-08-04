; Block decoder sketch

; MADS-compatible decoder skeleton

        ORG $C000

; --- program entry point ---
START
        JSR INIT_DECODER
        JSR DECOMPRESS_BLOCK
        RTS

; --- decoder state ---
INIT_DECODER
        LDX #$00
        LDY #$00
        LDA #$00
        STA BLOCK_INDEX
        LDA #<PAYLOAD
        STA PAYLOAD_PTR
        LDA #>PAYLOAD
        STA PAYLOAD_PTR+1
        LDA #$00
        STA PAIR_COUNT
        LDA #<IMAGE_BUFFER
        STA IMAGE_PTR
        LDA #>IMAGE_BUFFER
        STA IMAGE_PTR+1
        RTS

; --- main decode loop ---
DECOMPRESS_BLOCK
        LDY #$00
        LDA (PAYLOAD_PTR),Y
        CMP #$01
        BNE DECODE_DONE
        INY
        LDA (PAYLOAD_PTR),Y
        STA PAYLOAD_LEN
        INY
        LDA #$00
        STA PAIR_COUNT
        JMP DECODE_NEXT_BLOCK

DECODE_NEXT_BLOCK
        LDA (PAYLOAD_PTR),Y
        CMP #$FF
        BEQ END_BLOCK
        JMP READ_TOKEN_PAIR

READ_TOKEN_PAIR
        STA TOKEN
        INY
        LDA (PAYLOAD_PTR),Y
        STA VALUE
        INY
        INC PAIR_COUNT
        JSR PAIR_DECODE
        JMP DECODE_NEXT_BLOCK

PAIR_DECODE
        LDA TOKEN
        CMP #$02
        BNE STORE_VALUE
        JMP WRITE_TO_IMAGE

WRITE_TO_IMAGE
        LDA VALUE
        LDY #$00
        STA (IMAGE_PTR),Y
        INC IMAGE_PTR
        BNE IMAGE_DONE
        INC IMAGE_PTR+1
IMAGE_DONE
        RTS

STORE_VALUE
        LDA VALUE
        LDY #$00
        STA (IMAGE_PTR),Y
        INC IMAGE_PTR
        BNE IMAGE_DONE
        INC IMAGE_PTR+1
        JMP IMAGE_DONE

END_BLOCK
        INC BLOCK_INDEX
        CLC
        LDA PAYLOAD_PTR
        ADC PAYLOAD_LEN
        STA PAYLOAD_PTR
        BCC NO_WRAP
        INC PAYLOAD_PTR+1
NO_WRAP
        JMP DECOMPRESS_BLOCK

DECODE_DONE
        RTS

ZERO_FILL
        LDX #$00
        LDY #$00
ZERO_FILL_LOOP
        LDA #$00
        STA (IMAGE_PTR),Y
        INY
        CPY #$40
        BNE ZERO_FILL_LOOP
        RTS

DEQUANTIZE
        LDX #$00
DEQUANTIZE_LOOP
        LDA (IMAGE_PTR),Y
        CMP #$00
        BEQ DEQUANTIZE_NEXT
        CLC
        ADC #$01
        STA (IMAGE_PTR),Y
DEQUANTIZE_NEXT
        INY
        CPY #$40
        BNE DEQUANTIZE_LOOP
        RTS

; --- state variables ---
BLOCK_INDEX
        .BYTE $00
TOKEN
        .BYTE $00
VALUE
        .BYTE $00
PAYLOAD_LEN
        .BYTE $00
PAIR_COUNT
        .BYTE $00
PAYLOAD_PTR
        .WORD $0000
IMAGE_PTR
        .WORD $0000

; --- helper routines ---
IMAGE_BUFFER
        .BYTE $00

; --- payload data ---
PAYLOAD
        .BYTE $01
        .BYTE $03
        .BYTE $02
        .BYTE $00
        .BYTE $00
        .BYTE $FF
        .BYTE $00
        .BYTE $00
        .BYTE $00
        .BYTE $00
        .BYTE $01
        .BYTE $03
        .BYTE $02
        .BYTE $00
        .BYTE $00
        .BYTE $FF
        .BYTE $00
        .BYTE $00
        .BYTE $00
        .BYTE $00
        .BYTE $01
        .BYTE $03
        .BYTE $02
        .BYTE $00
        .BYTE $00
        .BYTE $FF
        .BYTE $00
        .BYTE $00
        .BYTE $00
        .BYTE $00

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
