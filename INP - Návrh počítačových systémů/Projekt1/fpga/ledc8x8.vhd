-- Autor reseni: SEM DOPLNTE VASE, JMENO, PRIJMENI A LOGIN

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.std_logic_arith.all;
use IEEE.std_logic_unsigned.all;

entity ledc8x8 is
port ( -- Sem doplnte popis rozhrani obvodu.

		RESET : in std_logic;
		SMCLK : in std_logic;
		ROW : out std_logic_vector(0 to 7);
		LED : out std_logic_vector(0 to 7)
		);
end ledc8x8;

architecture main of ledc8x8 is
	signal ce : std_logic;
	signal ce_interval : std_logic;
	signal prepnuti_stavu: std_logic_vector (1 downto 0) := (others => '0');
	signal interval: std_logic_vector (21 downto 0) := (others => '0');
	signal pocitadlo: std_logic_vector (7 downto 0) := (others => '0');
	signal radky: std_logic_vector (7 downto 0);
	

begin

	--zpomaleni na SMCLK/256 (2 na 8)
	zpomaleni_taktu: process(RESET, SMCLK, pocitadlo)
	begin
		if(RESET = '1') then
			pocitadlo <= (others => '0');
		elsif (SMCLK'event) and (SMCLK = '1') then
			pocitadlo <= pocitadlo + 1;
		end if;
	
	end process zpomaleni_taktu;
	
	ce <= '1' when pocitadlo = X"FF" else '0';
	
	
	pul_sec_interval: process(RESET, SMCLK, interval)
	begin
		if(RESET = '1') then
			interval <= (others => '0');	
		elsif (SMCLK'event) and (SMCLK = '1') then 
			interval <= interval + 1;
		end if;
	end process pul_sec_interval;	
	
	ce_interval <= '1' when interval = "1111111111111111111111" else '0';
	
	
	
	prepnuti: process(SMCLK, RESET, prepnuti_stavu, ce_interval, interval)
	begin
		if(RESET = '1') then
		prepnuti_stavu <= (others => '0');
		elsif(prepnuti_stavu /= "10") then
			if(SMCLK'event and SMCLK= '1' and ce_interval = '1') then
				prepnuti_stavu <= prepnuti_stavu + 1;
			end if;
		end if;
	
	end process prepnuti;
			
	
	
	
	vyber_radku: process( RESET, SMCLK, ce)
	begin
		if(RESET = '1') then
			radky <= "00000001";
		elsif(SMCLK'event and SMCLK = '1') then
			if(ce = '1') then
				radky <= radky(6 downto 0) & radky(7);
			end if;
		end if;
			
	end process vyber_radku;
	

	sviceni: process(radky, prepnuti_stavu)
	begin
		if(prepnuti_stavu /= "01") then 
			case radky is
				when "10000000" => LED <= "00000001";
				when "01000000" => LED <= "11101111";
				when "00100000" => LED <= "11101011";
				when "00010000" => LED <= "11101001";
				when "00001000" => LED <= "11101010";
				when "00000100" => LED <= "11101010";
				when "00000010" => LED <= "11111001";
				when "00000001" => LED <= "11111011";
				when others => LED <= "11111111";
			end case;
		
		else  
			case radky is
				when others => LED <= "11111111";
			end case;
			
		end if;
		
	end process sviceni;

	
	ROW <= radky;
	

end main;




-- ISID: 75579
