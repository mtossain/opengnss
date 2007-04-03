doppler_filter_coeffs = \
    gr.firdes.low_pass ( 
        1.0, # Gain
        input_rate,
        2e6, # Cutoff frequency
        1e6, # Width of transition band
        gr.firdes.WIN_HAMMING)

doppler_removal_filter = \
    gr.freq_xlating_fir_filter_ccf( 
        1, # FIR decimation
        doppler_filter_coeffs,
        doppler_frequency,
        input_rate)
    
