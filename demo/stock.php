<?php
$handler = opendir("./data/Out/");
while (($filename = readdir($handler)) !== false) {
        if ($filename != "." && $filename != "..") {
                $files[] = $filename;
           }
       }
closedir($handler);
$url = "http://ec2-34-222-62-83.us-west-2.compute.amazonaws.com/stock.php?date=";
foreach ($files as $value) {
	$value = substr($value,0,8);
    echo "<a  href=\"$url".$value."\">".$value."</a><br>";
}

$date = $_GET["date"];
if($date == "")
	$date = date("Ymd");
if($date != "" ){
	$stocknews = array();
	$filename = "./data/Out/".$date."_out";
	$infile = fopen($filename,"r");
	while(!feof($infile)){
		$line = fgets($infile);
		$line = trim($line);
		$arr = split("\t", $line);
		$stockSymbol = $arr[0];
		if(!array_key_exists($stockSymbol,$stocknews)){
			$stocknews[$stockSymbol] = array();	
		}
		array_push($stocknews[$stockSymbol],$line);
	}	
	fclose($infile);
	foreach($stocknews as $key=>$value){
		$labels = array();
		$links = array();
		$titles = array();
		$labelPros = array();
		foreach($value as $v){
			$items = split("\t", $v);
			if(count($items) != 5){
				continue;
			}
			if(!array_key_exists($items[3],$labels))
				$labels[$items[3]] = 0;
			$labels[$items[3]] += 1;
			array_push($links, $items[2]);
			array_push($titles, $items[1]);
			array_push($labelPros, $items[4]);
		}
		$labelstr = "";
		foreach($labels as $k=>$v){
			$labelstr.= $k.":".$v." ";
		}
		echo "<p>".$key."</p>";
		echo "<p>".$labelstr."</p>";
		echo "<table border=\"1\">";
		for($i=0; $i< count($links); $i++){
			echo "<tr><td><a  href=\"$links[$i]\">".$titles[$i]."</a></td>"."<td>".$labelPros[$i]."</td>";
		}
		echo "</table>";
	
	}
	
		
}

	
	


?>
