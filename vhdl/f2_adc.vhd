-- This is f2_adc VHDL model
-- Generated by initentity script
LIBRARY ieee;
USE ieee.std_logic_1164.all;
USE ieee.numeric_std.all;
USE std.textio.all;


ENTITY f2_adc IS
    PORT( A : IN  STD_LOGIC;
          Z : OUT STD_LOGIC
        );
END f2_adc;

ARCHITECTURE rtl OF f2_adc IS
BEGIN
    buf:PROCESS(A)
    BEGIN
        Z<=A;
    END PROCESS;
END ARCHITECTURE;