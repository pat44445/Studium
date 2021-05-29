-- cpu.vhd: Simple 8-bit CPU (BrainF*ck interpreter)
-- Copyright (C) 2019 Brno University of Technology,
--                    Faculty of Information Technology
-- Author(s): xdvora3d
--

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;

-- ----------------------------------------------------------------------------
--                        Entity declaration
-- ----------------------------------------------------------------------------
entity cpu is
 port (
   CLK   : in std_logic;  -- hodinovy signal
   RESET : in std_logic;  -- asynchronni reset procesoru
   EN    : in std_logic;  -- povoleni cinnosti procesoru
 
   -- synchronni pamet RAM
   DATA_ADDR  : out std_logic_vector(12 downto 0); -- adresa do pameti
   DATA_WDATA : out std_logic_vector(7 downto 0); -- mem[DATA_ADDR] <- DATA_WDATA pokud DATA_EN='1'
   DATA_RDATA : in std_logic_vector(7 downto 0);  -- DATA_RDATA <- ram[DATA_ADDR] pokud DATA_EN='1'
   DATA_RDWR  : out std_logic;                    -- cteni (0) / zapis (1)
   DATA_EN    : out std_logic;                    -- povoleni cinnosti
   
   -- vstupni port
   IN_DATA   : in std_logic_vector(7 downto 0);   -- IN_DATA <- stav klavesnice pokud IN_VLD='1' a IN_REQ='1'
   IN_VLD    : in std_logic;                      -- data platna
   IN_REQ    : out std_logic;                     -- pozadavek na vstup data
   
   -- vystupni port
   OUT_DATA : out  std_logic_vector(7 downto 0);  -- zapisovana data
   OUT_BUSY : in std_logic;                       -- LCD je zaneprazdnen (1), nelze zapisovat
   OUT_WE   : out std_logic                       -- LCD <- OUT_DATA pokud OUT_WE='1' a OUT_BUSY='0'
 );
end cpu;


-- ----------------------------------------------------------------------------
--                      Architecture declaration
-- ----------------------------------------------------------------------------
architecture behavioral of cpu is

	signal program_counter_reg : std_logic_vector(12 downto 0);
	signal program_counter_inc : std_logic;
	signal program_counter_dec : std_logic;

	signal program_tmp_reg : std_logic_vector(12 downto 0) := "1000000000000";

	signal pointer_reg : std_logic_vector(12 downto 0);
	signal pointer_inc : std_logic;
	signal pointer_dec : std_logic;
	
	signal whl_cnt_reg : std_logic_vector(7 downto 0);
	signal whl_cnt_inc : std_logic;
	signal whl_cnt_dec : std_logic;
	
	signal select_reg : std_logic_vector(1 downto 0) := "00";
	signal mx_wdata_sel : std_logic_vector(1 downto 0) := "00";
	
	
	
type fsm_state is
(
	s_idle,
	s_inc_load,
	s_inc_decode,
	s_inc_ptr,
	s_dec_ptr,
	s_inc_cell, s_inc_cell_2, s_inc_cell_final,
	s_dec_cell, s_dec_cell_2, s_dec_cell_final,
	s_while_0_start, s_while_1_start, s_while_2_start, s_while_3_start,
	s_while_0_end, s_while_1_end, s_while_2_end, s_while_3_end, s_while_4_end,
	s_print, s_print_final,
	s_ldnstr_to_act_cell, s_ldnstr_to_act_cell_final,
	s_str_to_tmp, s_str_to_tmp_2, s_str_to_tmp_final,
	s_tmp_to_act_cell, s_tmp_to_act_cell_2, s_tmp_to_act_cell_final,
	s_halt,
	s_nop


);
signal p_state : fsm_state;
signal n_state : fsm_state;
	
	
begin

program_counter_proc: process(CLK, RESET, program_counter_inc, program_counter_dec)
begin
	if(RESET = '1') then
		program_counter_reg <= (others => '0');
	elsif(CLK' event) and (CLK = '1')then
		if(program_counter_inc = '1')then
			program_counter_reg <= program_counter_reg + 1;
		elsif(program_counter_dec = '1')then
			program_counter_reg <= program_counter_reg - 1;
		end if;
	end if;
end process;


pointer_reg_proc: process(CLK, RESET, pointer_inc, pointer_dec, pointer_reg)
begin
	if(RESET = '1') then
		pointer_reg <= "1000000000000";
	elsif(CLK' event) and (CLK = '1')then
		if(pointer_inc = '1')then
			if(pointer_reg = "1111111111111")then
				pointer_reg <= "1000000000000";
			else
				pointer_reg <= pointer_reg + 1;
			end if;
		elsif(pointer_dec = '1')then
			if(pointer_reg = "1000000000000")then
				pointer_reg <= "1111111111111";
			else
				pointer_reg <= pointer_reg - 1;
			end if;
		end if;
	end if;
end process;

whl_cnt_proc: process(CLK, RESET, whl_cnt_inc, whl_cnt_dec)
begin
	if(RESET = '1') then
		whl_cnt_reg <= (others => '0');
	elsif(CLK' event) and (CLK = '1')then
		if(whl_cnt_inc = '1')then
			whl_cnt_reg <= whl_cnt_reg + 1;
		elsif(whl_cnt_dec = '1')then
			whl_cnt_reg <= whl_cnt_reg -1 ;
		end if;
	end if;
end process;

				
				
				
				
				
				
mx_select_ptr_or_pc: process(CLK, select_reg, program_counter_reg, pointer_reg)
begin
	if(select_reg = "00")then
		DATA_ADDR <= pointer_reg;
	elsif(select_reg = "01")then
		DATA_ADDR <= program_counter_reg;
	elsif(select_reg = "10")then
		DATA_ADDR <= program_tmp_reg;
	end if;
end process;
mx_write_selected_data: process(CLK, RESET, mx_wdata_sel)
begin
	if(CLK' event) and (CLK = '1')then
		if(mx_wdata_sel = "00")then
			DATA_WDATA <= IN_DATA;
		elsif(mx_wdata_sel = "01")then
			DATA_WDATA <= DATA_RDATA + 1;
		elsif(mx_wdata_sel = "10")then
			DATA_WDATA <= DATA_RDATA - 1;
		elsif(mx_wdata_sel = "11")then
			DATA_WDATA <= DATA_RDATA;
		end if;
	end if;
end process;







fsm_state_proc: process(CLK, RESET, EN)
begin
	if(RESET = '1')then
		p_state <= s_idle;
	elsif(CLK' event) and (CLK = '1')then
		if (EN = '1')then
			p_state <= n_state;
		end if;
	end if;
end process;
	


fsm_state_change_proc: process(IN_VLD, DATA_RDATA, IN_DATA, OUT_BUSY, p_state, whl_cnt_reg, program_tmp_reg )
begin

	IN_REQ <= '0';
	OUT_WE <= '0';
	DATA_RDWR <= '0';
	DATA_EN <= '0';
	
	
	program_counter_inc <= '0';
	program_counter_dec <= '0';
	pointer_inc <= '0';
	pointer_dec <= '0';
	whl_cnt_inc <= '0';
	whl_cnt_dec <= '0';




	case p_state is
	
		when s_idle =>
			n_state <= s_inc_load;
			
		when s_inc_load =>
			n_state <= s_inc_decode;
			DATA_EN <= '1';
			select_reg <= "01";
			
		when s_inc_decode =>
			if(DATA_RDATA = X"3E")then
				n_state <= s_inc_ptr;
			elsif(DATA_RDATA = X"3C")then
				n_state <= s_dec_ptr;
			elsif(DATA_RDATA = X"2B")then
				n_state <= s_inc_cell;
			elsif(DATA_RDATA = X"2D")then
				n_state <= s_dec_cell;
			elsif(DATA_RDATA = X"5B")then
				n_state <= s_while_0_start;
			elsif(DATA_RDATA = X"5D")then
				n_state <= s_while_0_end;
			elsif(DATA_RDATA = X"2E")then
				n_state <= s_print;
			elsif(DATA_RDATA = X"2C")then
				n_state <= s_ldnstr_to_act_cell;
			elsif(DATA_RDATA = X"24")then
				n_state <= s_str_to_tmp;
			elsif(DATA_RDATA = X"21")then
				n_state<= s_tmp_to_act_cell;
			elsif(DATA_RDATA = X"00")then
				n_state <= s_halt;
			else
				n_state <= s_nop;
			end if;
			
		when s_inc_ptr =>
			program_counter_inc <= '1';
			pointer_inc <= '1';
			n_state <= s_inc_load;
			
		when s_dec_ptr =>
			program_counter_inc <= '1';
			pointer_dec <= '1';
			n_state <= s_inc_load;
			
		when s_inc_cell =>
			DATA_RDWR <= '0';
			DATA_EN <= '1';
			select_reg <= "00";
			n_state <= s_inc_cell_2;
			
		when s_inc_cell_2 =>
			mx_wdata_sel <= "01";
			n_state <= s_inc_cell_final;
			
		when s_inc_cell_final =>
			program_counter_inc <= '1';
			DATA_RDWR <= '1';
			DATA_EN <= '1';
			select_reg <= "00";
			n_state <= s_inc_load;
			
		when s_dec_cell =>
			DATA_RDWR <= '0';
			DATA_EN <= '1';
			select_reg <= "00";
			n_state <= s_dec_cell_2;
			
		when s_dec_cell_2 =>
			mx_wdata_sel <= "10";
			n_state <= s_dec_cell_final;
			
			
		when s_dec_cell_final =>
			program_counter_inc <= '1';
			DATA_RDWR <= '1';
			DATA_EN <= '1';
			select_reg <= "00";
			n_state <= s_inc_load;
			
		when s_ldnstr_to_act_cell =>
			IN_REQ <= '1';
			mx_wdata_sel <= "00";
			select_reg <= "00";
			n_state <= s_ldnstr_to_act_cell_final;
			
		when s_ldnstr_to_act_cell_final =>
			if(IN_VLD = '1')then
				select_reg <= "00";
				mx_wdata_sel <= "00";
				DATA_RDWR <= '1';
				DATA_EN <= '1';
				program_counter_inc <= '1';
				n_state <= s_inc_load;
			else
				IN_REQ <= '1';
				select_reg <= "00";
				mx_wdata_sel <= "00";
				n_state <= s_ldnstr_to_act_cell_final;
			end if;
			
		when s_print =>
			DATA_RDWR <= '0';
			DATA_EN <= '1';
			select_reg <= "00";
			n_state <= s_print_final;
			
		when s_print_final =>
			if(OUT_BUSY = '0')then
				OUT_DATA <= DATA_RDATA;
				OUT_WE <= '1';
				program_counter_inc <= '1';
				n_state <= s_inc_load;
			else
				n_state <= s_print_final;
			end if;
			
		when s_str_to_tmp =>
			DATA_EN <= '1';
			DATA_RDWR <= '0';
			select_reg <= "00";
			n_state <= s_str_to_tmp_2;
			
		when s_str_to_tmp_2 =>
			mx_wdata_sel <= "11";
			n_state <= s_str_to_tmp_final;
			
		when s_str_to_tmp_final =>
			DATA_EN <= '1';
			DATA_RDWR <= '1';
			program_counter_inc <= '1';
			select_reg <= "10";
			n_state <= s_inc_load;
			
		when s_tmp_to_act_cell =>
			DATA_EN <= '1';
			DATA_RDWR <= '0';
			select_reg <= "10";
			n_state <= s_tmp_to_act_cell_2;
		
		when s_tmp_to_act_cell_2 =>
			mx_wdata_sel <= "11";
			n_state <= s_tmp_to_act_cell_final;
			
		when s_tmp_to_act_cell_final =>
			DATA_EN <= '1';
			DATA_RDWR <= '1';
			program_counter_inc <= '1';
			select_reg <= "00";
			n_state <= s_inc_load;
			
			
		when s_halt =>
			n_state <= s_halt;
			
		when s_nop =>
			program_counter_inc <= '1';
			n_state <= s_inc_load;
			
		when s_while_0_start =>
			DATA_EN <= '1';
			DATA_RDWR <= '0';
			select_reg <= "00";
			program_counter_inc <= '1';
			n_state <= s_while_1_start;
			
		when s_while_1_start =>
			if(DATA_RDATA = X"00")then
				whl_cnt_inc <= '1';
				n_state <= s_while_2_start;
			else
				n_state <= s_inc_load;
			end if;
			
		when s_while_2_start =>
			DATA_RDWR <= '0';
			DATA_EN <= '1';
			select_reg <= "01";
			n_state <= s_while_3_start;
			
		when s_while_3_start =>
			if(whl_cnt_reg = X"00")then
				n_state <= s_inc_load;
			else
				n_state <= s_while_2_start;
				if(DATA_RDATA = X"5B")then
					whl_cnt_inc <= '1';
				elsif(DATA_RDATA = X"5D")then
					whl_cnt_dec <= '1';
				end if;
				
				program_counter_inc <= '1';
			end if;

			
		when s_while_0_end =>
			DATA_RDWR <= '0';
			DATA_EN <= '1';
			select_reg <= "00";
			n_state <= s_while_1_end;
			
		when s_while_1_end =>
			if(DATA_RDATA = X"00")then
				program_counter_inc <= '1';
				n_state <= s_inc_load;
			else
				program_counter_dec <= '1';
				whl_cnt_inc <= '1';
				n_state <= s_while_2_end;
			end if;
			
		when s_while_2_end =>
			DATA_RDWR <= '0';
			DATA_EN <= '1';
			select_reg <= "01";
			n_state <= s_while_3_end;
			
		when s_while_3_end =>
				n_state <= s_while_4_end;
			if(whl_cnt_reg = X"00")then
				n_state <= s_inc_load;
			else
				if(DATA_RDATA = X"5B")then
					whl_cnt_dec <= '1';
				elsif(DATA_RDATA = X"5D")then
					whl_cnt_inc <= '1';
				end if;
			end if;
			
		when s_while_4_end =>
			n_state <= s_while_2_end;
			if(whl_cnt_reg = X"00")then
				program_counter_inc <= '1';
				
			else
				program_counter_dec <= '1';
			end if;
			
			
	end case;
			
end process;		
			


 -- zde dopiste vlastni VHDL kod


 -- pri tvorbe kodu reflektujte rady ze cviceni INP, zejmena mejte na pameti, ze 
 --   - nelze z vice procesu ovladat stejny signal,
 --   - je vhodne mit jeden proces pro popis jedne hardwarove komponenty, protoze pak
 --   - u synchronnich komponent obsahuje sensitivity list pouze CLK a RESET a 
 --   - u kombinacnich komponent obsahuje sensitivity list vsechny ctene signaly.
 
end behavioral;
 
