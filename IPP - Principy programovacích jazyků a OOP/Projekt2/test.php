<?php

$pr = new Parse();
$pr->arguments();

# nastaveni default cest
$psp=getcwd()."/parse.php";
$isp=getcwd()."/interpret.py";
$jxml="/pub/courses/ipp/jexamxml/jexamxml.jar";

# zpracovani vstupnich parametru
class Parse
{
    static $help_arg = false;
    static $recursive_arg = false;
    static $parse_only_arg = false;
    static $int_only_arg = false;
    static $directory_arg = false;
    static $parse_script_arg = false;
    static $int_script_arg = false;
    static $jexamxml_arg = false;
    
    static $parse_script_path;
    static $int_script_path;
    static $directory_path;
    static $jexamxml_path;
    
    function arguments() 
    {
        global $argv, $argc;
        unset($argv[0]);
        
       
        
        foreach ($argv as $argument)
        {
           
            if($argument == "--help" && !self::$help_arg)
            {
                echo ("Program test.php\n");
                
                if($argc != 2)
                {
                    exit(10);
                }
                
                self::$help_arg = true;
            }
            elseif($argument == "--recursive" && !self::$recursive_arg)
            {
                self::$recursive_arg = true;
            }
            elseif($argument == "--parse-only" && !self::$parse_only_arg && !self::$int_only_arg && !self::$int_script_arg)
            {
                self::$parse_only_arg = true;
            }
            elseif($argument == "--int-only" && !self::$int_only_arg && !self::$parse_only_arg && !self::$parse_script_arg)
            {
                self::$int_only_arg = true;
            }
            elseif(substr($argument,0,15) === "--parse-script=" && !self::$parse_script_arg)
            {
                self::$parse_script_arg = true;
                self::$parse_script_path = substr($argument, 15);
            }
            elseif(substr($argument,0,13) === "--int-script=" && !self::$int_script_arg)
            {
                self::$int_script_arg = true;
                self::$int_script_path = substr($argument, 13);
            }
            elseif(substr($argument,0,12) === "--directory=" && !self::$directory_arg)
            {
                self::$directory_arg = true;
                self::$directory_path = substr($argument, 12);
            }
            elseif(substr($argument,0,11) === "--jexamxml=" && !self::$jexamxml_arg)
            {
                self::$jexamxml_arg = true;
                self::$jexamxml_path = substr($argument, 11);
               
            }
            else
            {
                exit(10);
            }
            
            
            
        }
        
        return;
    }
}


# nastaveni zadanych cest k testovanym skriptum
if(Parse::$parse_script_arg)
{
    $psp = Parse::$parse_script_path;
}
if(Parse::$jexamxml_arg)
{
    $jxml = Parse::$jexamxml_path;
}
if(Parse::$int_script_arg)
{
    $isp = Parse::$int_script_path;
}




$passed = 0;
$failed = 0;


open_directory();



# Vygeneruje zakladni HTML
function make_html()
{
    
    
    echo "<!DOCTYPE html>";
    echo "<html>";
    
    echo "<head>";
        echo "<meta charset=utf-8>";
        echo "<title>IPP projekt - test.php</title>";
    echo "</head>";
    
    echo "<body>";
        echo "<h1>Skript test.php</h1>";
        echo "<b>Autor:</b> Tomáš Dvořáček";
        echo "<p><b>Login:</b> xdvora3d</p>";
        echo "<p><h1>Výsledky testů:</h1></p>";
        
        
    echo "</body>";
        
}

# Otevre slozku s testy zadanou v argumentech
function open_directory()
{
    if(Parse::$directory_arg)
    {
        if(is_dir(Parse::$directory_path))
        {
            $directory = opendir(Parse::$directory_path);
            make_html();
            
            echo "<p><b>Testy byly spuštěny z adresáře:".Parse::$directory_path."</b></p>";
            test(Parse::$directory_path);
        }
        else 
        {
           exit(11);
        }
    }
    else 
    {
        $directory = opendir(".");
        make_html();
        
        
        echo "<p><b>Testy byly spuštěny z adresáře:".getcwd()."</b></p>";
        test(".");
    }
    
    
    
}

# prochazi slozku s testy (poked je --recursive tak i rekurzivně)
function test($dirname)
{
    global $failed, $passed;
    
    $directory = opendir($dirname);
    $bool = true;
    $failed = 0;
    $passed = 0;
   
    while(false !== ($file = readdir($directory)))
    {
      
       
        
        if(is_dir($dirname ."/".$file) && $file !== "." && $file !== "..")
        {
            
            if(Parse::$recursive_arg)
            {
                test($dirname ."/". $file);
            }
        }
        else if($file === "." && $file === "..")
        {
            
        }
        else 
        {
            $extension = pathinfo($file, PATHINFO_EXTENSION);
            
           
            if($extension == "src") 
            {
                if ($bool)
                {
                    echo '<p><font size ="5">Adresář: '.$dirname."</font></p>";
                    $bool = false;
                }

               	$name = basename($file, $extension);
		
		
                file_checker($dirname, $name);
                run_test($dirname ,$name);
            }


		

	}
    }


	$number_of_tests = $failed + $passed;
	echo '<p><b><font size ="4"color="black">Celkem testů: </font>'.$number_of_tests.'</b></p>';
	echo '<p><b><font size ="4"color="red">Testů neprošlo: </font>'.$failed.'</b></p>';
	echo '<p><b><font size ="4" color="green">Testů prošlo: </font>'.$passed.'</b></p>';
	echo "<hr>";

		
		
  
}
    
# provede test nad jednim .src souborem
function run_test($dirname ,$name)
{
    global $passed, $failed, $jxml, $psp, $isp;
    
   
    
       
        if(Parse::$parse_only_arg) //pouze parse-only
        {
            
            exec("touch ./temporary1");
            
            exec("php7.4 ".$psp." < ".$dirname."/".$name."src"." > "."./temporary1",$nothing, $ret_code);
            
            $ref_ret_code = exec("cat ".$dirname."/".$name."rc");
            
            if((string)$ret_code !== "0")
            {
                if((string)$ret_code === (string)$ref_ret_code)
                {
                    $passed++;
                }
                else 
                {
                    echo '<p><font size ="3"color="red">Neprošel: </font>'."/".$name.'</p>';
                    $failed++;
                }
                
                exec("rm -rf ./temporary1");
                return;
                
            }
            else 
            {
                
                
                exec("java -jar ".$jxml." ./temporary1"." ".$dirname."/".$name."out", $nothing, $rc);
                
                if((string)$rc === "0")
                {
                    $passed++;
                }
                else
                {
                    echo '<p><font size ="3"color="red">Neprošel: </font>'."/".$name.'</p>';
                    $failed++;
                    
                }
                
                exec("rm -rf ./temporary1");
                return;
            }
            
            
        }
        elseif(Parse::$int_only_arg) // pouze int-only
        {
           
            
            exec("touch ./temporary1");
            exec("python3.8 ".$isp." --source=".$dirname."/".$name."src"." < ".$dirname."/".$name."in"." > ./temporary1",$nothing, $ret_code);
            
            $ref_ret_code = exec("cat ".$dirname."/".$name."rc");
            
            if($ret_code !==0)
            {
                if($ret_code == $ref_ret_code)
                {
                    $passed++;
                }
                else
                {
                    echo '<p><font size ="3"color="red">Neprošel: </font>'."/".$name.'</p>';
                    $failed++;
                }
                
                exec("rm -rf ./temporary1");
                return;
            }
            else
            {
                $result = shell_exec("diff ".$dirname."/".$name."out"." ./temporary1");
                
                if( (string)$result === "")
                {
                    $passed++;
                }
                else
                {
                    echo '<p><font size ="3"color="red">Neprošel: </font>'."/".$name.'</p>';
                    $failed++;
                }
                
                exec("rm -rf ./temporary1");
                return;
            }
        }
        else // both
        {
            
            exec("touch ./temporary1");
            exec("touch ./temporary2");
            
            exec("php7.4 ".$psp." < ".$dirname."/".$name."src"." > ./temporary1");
      
            exec("python3.8 ".$isp." --source=./temporary1 < ".$dirname."/".$name."in"." > ./temporary2",$nothing, $ret_code);
            
            
            $ref_ret_code = exec("cat ".$dirname."/".$name."rc");
            
            if($ret_code !== 0)
            {
                if($ret_code == $ref_ret_code)
                {
                    $passed++;
                }
                else
                {
                    echo '<p><font size ="3"color="red">Neprošel: </font>'."/".$name.'</p>';
                    $failed++;
                }
                
                exec("rm -rf ./temporary1");
                exec("rm -rf ./temporary2");
                return;
                
            }
            else 
            {
                $result = shell_exec("diff ".$dirname."/".$name."out"." ./temporary2");
                
                if( (string)$result === "")
                {
                    $passed++;
                }
                else
                {
                    echo '<p><font size ="3"color="red">Neprošel: </font>'."/".$name.'</p>';
                    $failed++;
                }
                
                exec("rm -rf ./temporary1");
                exec("rm -rf ./temporary2");
                return;
            }
            
        }
       
    
   
}

# dogeneruje v adresari pripadne chybejici soubory .in, .out, .rc
function file_checker($dirname, $name)
{
    
    $in = false;
    $out = false;
    $rc = false;
    
    $directory = opendir($dirname);
    while(false !== ($file = readdir($directory)))
    {
        
        if(!((is_dir($dirname ."/". $file) && $file !== "." && $file !== "..") || ($file === "." && $file === "..") ) )
        {
            
            $extension = pathinfo($file, PATHINFO_EXTENSION);
            $name2 = basename($file, $extension);
            
            if($extension === "in" && $name === $name2) 
            {
                $in = true;
                
            }
            elseif($extension === "out" && $name === $name2)
            {
                $out = true;
               
            }
            elseif($extension === "rc" && $name === $name2)
            {
                $rc = true;
               
                
            }
        }
    }
    
    
    if(!$in)
    {
        exec("touch ".$dirname."/".$name."in"); //dogeneruje .in
    }
    if(!$out)
    {
        exec("touch ".$dirname."/".$name."out"); //dogeneruje .out
    }
    if(!$rc)
    {  
        exec("touch ".$dirname."/".$name."rc"); //dogeneruje .rc a nastavi na nulu
        exec('echo "0" > '.$dirname."/".$name."rc");
    }
    
    return;
}



    
        
    
        
