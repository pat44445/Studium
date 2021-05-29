-- fsm.vhd: Finite State Machine
-- Author(s): 
--
library ieee;
use ieee.std_logic_1164.all;
-- ----------------------------------------------------------------------------
--                        Entity declaration
-- ----------------------------------------------------------------------------
entity fsm is
port(
   CLK         : in  std_logic;
   RESET       : in  std_logic;

   -- Input signals 
   KEY         : in  std_logic_vector(15 downto 0); 
   CNT_OF      : in  std_logic;

   -- Output signals
   FSM_CNT_CE  : out std_logic;
   FSM_MX_MEM  : out std_logic;
   FSM_MX_LCD  : out std_logic;
   FSM_LCD_WR  : out std_logic;
   FSM_LCD_CLR : out std_logic
);
end entity fsm;

-- ----------------------------------------------------------------------------
--                      Architecture declaration
-- ----------------------------------------------------------------------------
architecture behavioral of fsm is
   type t_state is (TEST1,TEST2,TEST3,TEST_4_0,TEST_4_1,TEST_5_0,TEST_5_1,TEST_6_0,TEST_6_1,TEST_7_0,TEST_7_1,
	TEST_8_0,TEST_8_1,TEST_9_0,TEST_9_1,TEST_10_0,TEST_10_1,TEST_11_0,PRINT_MESSAGE_SPATNY,PRINT_MESSAGE_SPRAVNY,
	FINISH_SPATNE,FINISH_SPRAVNE, FINISH);
   signal present_state, next_state : t_state;

begin

-- -------------------------------------------------------
sync_logic : process(RESET, CLK)
begin
   if (RESET = '1') then
      present_state <= TEST1;
   elsif (CLK'event AND CLK = '1') then
      present_state <= next_state;
   end if;
end process sync_logic;

-- xdvora3d : kod1 = 27808853056 	 kod2 = 2734808842
-- -------------------------------------------------------
next_state_logic : process(present_state, KEY, CNT_OF)
begin
   case (present_state) is
   -- - - - - - - - - - - - - - - - - - - - - - -
   when TEST1 =>
      next_state <= TEST1;
		if (KEY(2) = '1') then
			next_state <= TEST2;
		elsif (KEY(14 downto 0) /= "000000000000000") then
         next_state <= FINISH_SPATNE;
      elsif (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
		
	-- - - - - - - - - - - - - - - - - - - - - - -
   when TEST2 =>
      next_state <= TEST2;
		if (KEY(7) = '1') then
			next_state <= TEST3;
		elsif (KEY(14 downto 0) /= "000000000000000") then
         next_state <= FINISH_SPATNE;
      elsif (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
   when TEST3 =>
      next_state <= TEST3;
		if (KEY(8) = '1') then
			next_state <= TEST_4_0;
		elsif (KEY(3) = '1') then
			next_state <= TEST_4_1;
		elsif (KEY(14 downto 0) /= "000000000000000") then
         next_state <= FINISH_SPATNE;
      elsif (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
   -- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_4_0 =>
      next_state <= TEST_4_0;
		if (KEY(0) = '1') then
			next_state <= TEST_5_0;
		elsif (KEY(14 downto 0) /= "000000000000000") then
         next_state <= FINISH_SPATNE;
      elsif (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_4_1 =>
      next_state <= TEST_4_1;
		if (KEY(4) = '1') then
			next_state <= TEST_5_1;
		elsif (KEY(14 downto 0) /= "000000000000000") then
         next_state <= FINISH_SPATNE;
      elsif (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_5_0 =>
      next_state <= TEST_5_0;
		if (KEY(8) = '1') then
			next_state <= TEST_6_0;
		elsif (KEY(14 downto 0) /= "000000000000000") then
         next_state <= FINISH_SPATNE;
      elsif (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_5_1 =>
      next_state <= TEST_5_1;
		if (KEY(8) = '1') then
			next_state <= TEST_6_1;
		elsif (KEY(14 downto 0) /= "000000000000000") then
         next_state <= FINISH_SPATNE;
      elsif (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_6_0 =>
      next_state <= TEST_6_0;
		if (KEY(8) = '1') then
			next_state <= TEST_7_0;
		elsif (KEY(14 downto 0) /= "000000000000000") then
         next_state <= FINISH_SPATNE;
      elsif (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_6_1 =>
      next_state <= TEST_6_1;
		if (KEY(0) = '1') then
			next_state <= TEST_7_1;
		elsif (KEY(14 downto 0) /= "000000000000000") then
         next_state <= FINISH_SPATNE;
      elsif (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_7_0 =>
      next_state <= TEST_7_0;
		if (KEY(5) = '1') then
			next_state <= TEST_8_0;
		elsif (KEY(14 downto 0) /= "000000000000000") then
         next_state <= FINISH_SPATNE;
      elsif (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_7_1 =>
      next_state <= TEST_7_1;
		if (KEY(8) = '1') then
			next_state <= TEST_8_1;
		elsif (KEY(14 downto 0) /= "000000000000000") then
         next_state <= FINISH_SPATNE;
      elsif (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_8_0 =>
      next_state <= TEST_8_0;
		if (KEY(3) = '1') then
			next_state <= TEST_9_0;
		elsif (KEY(14 downto 0) /= "000000000000000") then
         next_state <= FINISH_SPATNE;
      elsif (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_8_1 =>
      next_state <= TEST_8_1;
		if (KEY(8) = '1') then
			next_state <= TEST_9_1;
		elsif (KEY(14 downto 0) /= "000000000000000") then
         next_state <= FINISH_SPATNE;
      elsif (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_9_0 =>
      next_state <= TEST_9_0;
		if (KEY(0) = '1') then
			next_state <= TEST_10_0;
		elsif (KEY(14 downto 0) /= "000000000000000") then
         next_state <= FINISH_SPATNE;
      elsif (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_9_1 =>
      next_state <= TEST_9_1;
		if (KEY(4) = '1') then
			next_state <= TEST_10_1;
		elsif (KEY(14 downto 0) /= "000000000000000") then
         next_state <= FINISH_SPATNE;
      elsif (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_10_0 =>
      next_state <= TEST_10_0;
		if (KEY(5) = '1') then
			next_state <= TEST_11_0;
		elsif (KEY(14 downto 0) /= "000000000000000") then
         next_state <= FINISH_SPATNE;
      elsif (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_10_1 =>
      next_state <= TEST_10_1;
		if (KEY(2) = '1') then
			next_state <= FINISH_SPRAVNE;
		elsif (KEY(14 downto 0) /= "000000000000000") then
         next_state <= FINISH_SPATNE;
		elsif (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_11_0 =>
      next_state <= TEST_11_0;
		if (KEY(6) = '1') then
			next_state <= FINISH_SPRAVNE;
		elsif (KEY(14 downto 0) /= "000000000000000") then
         next_state <= FINISH_SPATNE;
      elsif (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when FINISH_SPATNE =>
		next_state <= FINISH_SPATNE;
		if (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPATNY; 
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when FINISH_SPRAVNE =>
		next_state <= FINISH_SPRAVNE;
		if (KEY(15) = '1') then
         next_state <= PRINT_MESSAGE_SPRAVNY;
		elsif (KEY(14 downto 0) /= "000000000000000") then
			next_state <= FINISH_SPATNE;
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when PRINT_MESSAGE_SPATNY =>
      next_state <= PRINT_MESSAGE_SPATNY;
      if (CNT_OF = '1') then
         next_state <= FINISH;
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when PRINT_MESSAGE_SPRAVNY =>
      next_state <= PRINT_MESSAGE_SPRAVNY;
      if (CNT_OF = '1') then
         next_state <= FINISH;
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
   when FINISH =>
      next_state <= FINISH;
      if (KEY(15) = '1') then
         next_state <= TEST1; 
      end if;
   -- - - - - - - - - - - - - - - - - - - - - - -
   when others =>
      next_state <= TEST1;
   end case;
end process next_state_logic;

-- xdvora3d : kod1 = 27808853056 	 kod2 = 2734808842
-- -------------------------------------------------------
output_logic : process(present_state, KEY)
begin
   FSM_CNT_CE     <= '0';
   FSM_MX_MEM     <= '0';
   FSM_MX_LCD     <= '0';
   FSM_LCD_WR     <= '0';
   FSM_LCD_CLR    <= '0';

   case (present_state) is
   -- - - - - - - - - - - - - - - - - - - - - - -
   when TEST1 =>
      if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
   when TEST2 =>
      if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if; 
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
   when TEST3 =>
      if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
   when TEST_4_0 =>
      if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
   when TEST_4_1=>
      if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
   -- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_5_0=>
      if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_5_1=>
      if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_6_0=>
      if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_6_1=>
      if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_7_0=>
      if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_7_1=>
      if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_8_0=>
      if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_8_1=>
      if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_9_0=>
      if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_9_1=>
      if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_10_0=>
      if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_10_1=>
      if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
	when TEST_11_0=>
      if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
	-- - - - - - - - - - - - - - - - - - - - - - -
   when PRINT_MESSAGE_SPATNY =>
      FSM_CNT_CE     <= '1';
      FSM_MX_LCD     <= '1';
      FSM_LCD_WR     <= '1';
   -- - - - - - - - - - - - - - - - - - - - - - -
	when PRINT_MESSAGE_SPRAVNY => 
      FSM_CNT_CE     <= '1';
      FSM_MX_LCD     <= '1';
      FSM_LCD_WR     <= '1';
		FSM_MX_MEM 		<= '1';
	-- - - - - - - - - - - - - - - - - - - - - - -
	when FINISH_SPRAVNE =>
		if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
		if (KEY(15) = '1') then
			FSM_LCD_CLR    <= '1';
		end if;
	---------------------
	when FINISH_SPATNE =>
		if (KEY(14 downto 0) /= "000000000000000") then
         FSM_LCD_WR     <= '1';
      end if;
		if (KEY(15) = '1') then
			FSM_LCD_CLR    <= '1';
		end if;
   -- - - - - - - - - - - - - - - - - - - - - - -
   when FINISH =>
      if (KEY(15) = '1') then
         FSM_LCD_CLR    <= '1';
      end if;
   -- - - - - - - - - - - - - - - - - - - - - - -
   when others =>
   end case;
end process output_logic;

end architecture behavioral;

