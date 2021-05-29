<?php

arguments();

$syn = new Syntax();

$syn->check_if_header();

$order = 0;
while(($row = fgets(STDIN)) != false)
{
    $order++;
    
    if(strpos($row, '#') !== false)
    {
        $row = explode("#",$row);
        $row = $row[0];
        
    }
    if(preg_match('/^[\s]*$/', $row))
    {
        $order--;
        continue;
    }
    $row = trim($row);
    
    $keywords_spaces = preg_split("/( |\t)/",$row);
    
    foreach($keywords_spaces as $k)
    {
        if($k == '' || $k === '\t')
        {
            continue;
        }
        else
        {
            $keywords[] = trim($k);
        }
        
    }
    
    $syn->check_syntax($order, $keywords);
    
    
    unset($keywords);
    unset($keywords_spaces);
}


$syn->print_output();


# funkce pro zpracovani argumentu z prikazove radky

function arguments() {
    global $argc;
    $argument = getopt("",["help"]);
    
    if($argc == 1)
    {
        return;
    }
    elseif($argc == 2 )
    {
        if(array_key_exists('help', $argument))
        {
            echo ("Program parser.php\nZadejte program v jazyce IPPcode20 na standardni vstup\n");
            exit(0);
        }
        else
        {
            exit(10);
        }
    }
    else 
        exit(10);
}


# trida Xml_Writer pro zapis instrukci do formatu XML

class Xml_Writer
{
    private $writer;
    
    function make_header()
    {
        $this->writer = new XMLWriter();
        $this->writer->openMemory();
        $this->writer->startDocument( '1.0", UTF-8' );
        $this->writer->startElement('program');
        $this->writer->writeAttribute('language', 'IPPcode20');
    }
    
    function write_instruction_opcode($opcode, $order)
    {
        $this->writer->startElement('instruction');
        $this->writer->writeAttribute('order', $order);
        $this->writer->writeAttribute('opcode', $opcode);
    }
    
    function write_instruction_operands($name, $type, $text)
    {
        $this->writer->startElement($name);
        $this->writer->writeAttribute('type', $type);
        $this->writer->text($text);
        $this->writer->endElement();
    }
    function write_instruction_opcode_end()
    { 
        $this->writer->endElement();
    }
    function print_output()
    {
        $this->writer->endDocument();
        echo $this->writer->outputMemory();
    }
}
    
    

# trida pro kontrolu zpravnosti syntaxe


class Syntax
{
    private $instance_to_writer;
    
    
    # funkce ktera kontroluje jestli je je pritomna hlavicka ippcode20
    function check_if_header()
    {
        $this->instance_to_writer = new Xml_Writer();
        
        while($row = fgets(STDIN))
        {
            if(strpos($row, '#') !== false)
            {
                $row = explode("#", $row);
                $row = $row[0];
            }
            $row = trim($row);
            if($row == '')
                continue;
                
                if(!preg_match('/^\.ippcode20$/', strtolower($row)))
                {
                    fprintf(STDERR, "Chybna / Chybi hlavicka .IPPcode20\n");
                    exit(21);
                }
                
                $this->instance_to_writer->make_header();
                return;
        }
        
        
        fprintf(STDERR, "Chybna | Chybi hlavicka .IPPcode20\n");
        exit(21);
        
    }
    
    
    # funkce ktera kontroluje jeden instrukcni radek
    # @vstup - $order = cislo radku
    # @vstup - $keywords = pole klicovych elementu rozdelenych podle mezer
    function check_syntax($order, $keywords)
    {

        switch (($keywords[0] = strtoupper($keywords[0])))
        {
            case "ADD":
            case "SUBB":
            case "MUL":
            case "IDIV":
            case "LT":
            case "GT":
            case "EQ":
            case "AND":
            case "OR":
            case "STR2INT":
            case "CONCAT":
            case "GETCHAR":
            case "SETCHAR":
                {
                    if(count($keywords) == 4)
                    {
                        $this->instance_to_writer->write_instruction_opcode($keywords[0], $order);
                        if($this->check_var($keywords[1], "arg1") && ($this->check_symb($keywords[2], "arg2") || $this->check_var($keywords[2], "arg2")) && ($this->check_symb($keywords[3], "arg3") || $this->check_var($keywords[3], "arg3") ) )
                        {
                            $this->instance_to_writer->write_instruction_opcode_end();
                            return true;
                        }
                            
                    }
                    exit(23);
                }
            case "CREATEFRAME":
            case "PUSHFRAME":
            case "POPFRAME":
            case "RETURN":
            case "BREAK":
                {
                    if(count($keywords) == 1)
                    {
                        $this->instance_to_writer->write_instruction_opcode($keywords[0], $order);
                        $this->instance_to_writer->write_instruction_opcode_end();
                        return true;
                    }
                    exit(23);
                }
            case "MOVE":
            case "NOT":
            case "INT2CHAR":
            case "STRLEN":
            case "TYPE":
                {
                    if(count($keywords) == 3)
                    {
                        
                        $this->instance_to_writer->write_instruction_opcode($keywords[0], $order);
                        if($this->check_var($keywords[1], "arg1") && ($this->check_symb($keywords[2], "arg2") || $this->check_var($keywords[2], "arg2") ) )
                        {
                            $this->instance_to_writer->write_instruction_opcode_end();
                            return true;
                        }
                            
                    }
                    exit(23);
                }
            case "PUSHS":
            case "WRITE":
            case "EXIT":
            case "DPRINT":
                {
                    if(count($keywords) == 2)
                    {
                        $this->instance_to_writer->write_instruction_opcode($keywords[0], $order);
                        if($this->check_symb($keywords[1], "arg1") || $this->check_var($keywords[1], "arg1"))
                        {
                            $this->instance_to_writer->write_instruction_opcode_end();
                            return true;
                        }
                            
                    }
                    exit(23);
                }
            case "CALL":
            case "LABEL":
            case "JUMP":
                {
                    if(count($keywords) == 2)
                    {
                        $this->instance_to_writer->write_instruction_opcode($keywords[0], $order);
                        if($this->check_label($keywords[1], "arg1"))
                        {
                            $this->instance_to_writer->write_instruction_opcode_end();
                            return true;
                        }
                        
                    }
                    exit(23);
                }
            case "JUMPIFEQ":
            case "JUMPIFNEQ":
                {
                    if(count($keywords) == 4)
                    {
                        $this->instance_to_writer->write_instruction_opcode($keywords[0], $order);
                        if($this->check_label($keywords[1], "arg1") && ($this->check_symb($keywords[2], "arg2") || $this->check_var($keywords[2], "arg2") ) && ($this->check_symb($keywords[3], "arg3") || $this->check_var($keywords[2], "arg3") ) )
                        {
                            $this->instance_to_writer->write_instruction_opcode_end();
                            return true;
                        }
                           
                    }
                    exit(23);
                }
            case "DEFVAR":
 	        case "POPS":
                {
                    if(count($keywords) == 2)
                    {
                        $this->instance_to_writer->write_instruction_opcode($keywords[0], $order);
                        
                        if($this->check_var($keywords[1], "arg1"))
                        {
                            $this->instance_to_writer->write_instruction_opcode_end();
                            return true;
                        }
                        
                    }
                    exit(23);
                }
            case "READ":
                {
                    if(count($keywords) == 3)
                    {
                        $this->instance_to_writer->write_instruction_opcode($keywords[0], $order);
                        
                        if($this->check_var($keywords[1], "arg1") && preg_match('/^(int|string|bool)$/', $keywords[2]))
                        {
                            $this->instance_to_writer->write_instruction_operands("arg2", "type", $keywords[2]);
                            $this->instance_to_writer->write_instruction_opcode_end();
                            return true;
                        }
                        
                    }
                    exit(23); //LEX or SYNTAX err
                }
                
                
            default:
                exit(22); // neznamy nebo chybny opcode
        }
        
        
    }
    
    # funkce ktera kontroluje spravnost zapisu promenne
    # @vstup - $var = nazev promenne
    # @vstup - $name = poradi argumentu (arg1 | arg2 | arg3)
    function check_var($var, $name) // kontrola syntaxe promenne
    {
        
        if(preg_match('/^(TF|LF|GF)@([_|\-|\$|\&|%|\*|!|\?]|[a-zA-Z])([a-zA-Z0-9]|_|\-|\$|\&|%|\*|!|\?)*$/', $var) && preg_match('/[a-zA-Z]+/', substr($var, 3)))
        {
            $this->instance_to_writer->write_instruction_operands($name, "var" ,$var);
            return true;
        }
        
        else
            return false;
    }
    # funkce ktera kontroluje spravnost zapisu konstanty
    # @vstup - $symb = textovy retezec konstanty
    # @vstup - $name = poradi argumentu (arg1 | arg2 | arg3)
    function check_symb($symb, $name) //kontrola syntaxe konstanty
    {
        if(preg_match('/^(int|bool|string|nil)@(.*)$/', $symb))
        {
            
            $symb_arr = explode("@", $symb, 2);
            
            if($symb_arr[0] == "int")
            {
                if(!preg_match('/^(\+|\-|[0-9])[0-9]*$/', $symb_arr[1]))
                    return false;
            }
            elseif($symb_arr[0] == "bool")
            {
                $symb_arr[1] = strtolower($symb_arr[1]);
                if(!preg_match('/^(true|false)$/', $symb_arr[1]))
                    return false;
            }
            elseif($symb_arr[0] == "string")
            {
                
                if(!preg_match('/^(?:[^\s#\\\\]|(?:\\\\\d{3}))*$/', $symb_arr[1]))
                {
                    return false;
                }
            }
            
            elseif($symb_arr[0] == "nil")
            {
                if(!preg_match('/^(nil)$/', $symb_arr[1]))
                    return false;
            }
            else
            {
                return false;
            }
            
            $this->instance_to_writer->write_instruction_operands($name, $symb_arr[0], $symb_arr[1]);
            return true;
            
        }
        else
            return false;
            
    }
    # funkce ktera kontroluje spravnost zapisu navesti
    # @vstup - $label = textovy retezec navesti
    # @vstup - $name = poradi argumentu (arg1 | arg2 | arg3)
    function check_label($label, $name) // kontrola syntaxe navesti
    {
        if(preg_match('/^([_|\-|\$|\&|%|\*|!|\?]|[a-zA-Z])([a-zA-Z0-9]|_|\-|\$|\&|%|\*|!|\?)*$/', $label) && preg_match('/[a-zA-Z]+/', $label))
        {
            $this->instance_to_writer->write_instruction_operands($name, "label", $label);
            return true;
        }
        else
            return false;
    }
    
    # vytisknuti xml na stdout
    function print_output() 
    {
        $this->instance_to_writer->print_output();
    }
}






