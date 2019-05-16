"""
by Shinong Mao
This code is written in python code based on the technical datasheet from ADI
It is used as the register generator for the ADF4351 chip
"""
from decimal import *

#define parameters
f_start = 500000000         #start frequency 500MHz
f_end = 2700000000          #stop frequency 2700MHz
step_size = 1000000         #sweep step 1MHz
REF_in = 100000000          #reference Osc frequency 100MHz
R = 5                       #clock divider, 5
out_p = -4                  #output power, -4dBm,choose 1 of 4 opts(-4,-1,2,5)

f_span = f_end-f_start
p_number = int(f_span/step_size)+1
f_PFD = REF_in * (1/R)

#define the output power level, only 4 options
def power_select(x):
    return{
        -4:0,
        -1:1,
        2:2,
        5:3,
    }.get(x,0)

#frequency sweep
def div_c(RF_out):
        if 2200000000<RF_out<=4400000000:
            div = 1                              #define the RF divider = RFout/fPFD
            div_r = 0                            #define the divider value for rigester define
        elif 1100000000<RF_out<=2200000000:
            div = 2
            div_r = 1
        elif 550000000<RF_out<=1100000000:
            div = 4
            div_r = 2
        elif 275000000<RF_out<=550000000:
            div = 8
            div_r = 3
        elif 137500000<RF_out<=275000000:
            div = 16
            div_r = 4
        elif 68750000<RF_out<=137500000:
            div = 32
            div_r = 5
        elif 34375000<RF_out<=68750000:
            div = 64
            div_r = 6
        else:
            print('frequency out of range')
            exit()
        return [div,div_r]

#define 2201 points sweep
def sweep(f1,f2,s):
    R_0_buffer = []
    R_1_buffer = []
    R_4_buffer = []
    p_index = power_select(out_p)      #register for def power
    for i in range(f1,f2+s,s):
        div = div_c(i)[0]
        div_r = div_c(i)[1]
        INT = int(i/(f_PFD/div))
        if INT <23:
            print('INT value error')
        remain = str(round((i/(f_PFD/div)-INT),2))
        frac_buffer = Decimal(remain).as_integer_ratio()
        FRAC = frac_buffer[0]
        MOD = frac_buffer[1]
        if MOD < 2:
            MOD = 2
        #print(div,INT,FRAC,MOD)
        R_0 = hex(2**3*FRAC+2**15*INT)
        R_1 = hex(1*2**0+2**3*MOD+2**15*1+2**27*1)
        R_4 = hex(4*2**0+p_index*2**3+2**5+160*2**12+2**20*div_r+2**23)
        #print(i/1000000,R_0,R_1,R_4)
        R_0_buffer.append(R_0)
        R_1_buffer.append(R_1)
        R_4_buffer.append(R_4)
    return(R_0_buffer,R_1_buffer,R_4_buffer)

if __name__ == '__main__':
    import csv

    buffer = sweep(f_start, f_end, step_size)

    f = open('result.csv', 'w', newline='')
    writer = csv.writer(f)
    for i in range(p_number):
        Reg_buf = [buffer[0][i], buffer[1][i], buffer[2][i]]
        #print(buffer[0][i],buffer[1][i],buffer[2][i])
        writer.writerow(Reg_buf)
    f.close()

    R_0 = buffer[0]
    R_1 = buffer[1]
    R_4 = buffer[2]
    print(len(R_1))
    for i in range(len(R_4)):
        print(R_4[i],end='')
        print(',',end='')
