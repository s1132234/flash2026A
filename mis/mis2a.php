<!DOCTYPE html>
<html lang="zh-TW">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>黃士豪簡介</title>	
	<style type="text/css">
		* { font-family:"標楷體"; margin-left:auto; margin-right:auto;}
		h1 {color:blue; font-size:60px;}
		h2 {color:#33ff33; font-size:40px;}
	</style>

	<script>
		function change1() {
  			document.getElementById("pic").src = "huang2.jpg";
  			document.getElementById("h2text").innerText = "靜宜資管";
		}

		function change2() {
  			document.getElementById("pic").src = "huang.jpg";
  			document.getElementById("h2text").innerText = "Shih-Hao Huang";
		}
	</script>

</head>
<body>
	<?php echo date("Y-m-d") ?>
	<table width="70%">
		<tr>
			<td>
				<img src="huang.jpg" width="110%" id="pic" onmouseover="change1()" onmouseout="change2()"></img>
			</td>

			<td>
				<h1>黃士豪</h1>
				<h2 id="h2text">Shih-Hao Huang</h2>
			</td>
		</tr>
	</table>
	<table width="70%" border="1">
		<tr>
			<td>
				Instagram: <a href="https://www.instagram.com/zuck">https://www.instagram.com/zuck</a><br>
				X: <a href="https://x.com/elonmusk" target="_blank">https://x.com/elonmusk</a><br>
				Tel: <a href="tel:0424874875">04-24874875</a><br>
				E-Mail: <a href="mailto:s1132234@pu.edu.tw">s1132234@pu.edu.tw</a><br>

			</td>

			<td>
				大象席地而坐電影配樂<br>
				<audio controls>
					<source src="elephant.mp3" type="audio/mP3">
				</audio><br>
			</td>

			<td>
				不要去臺灣<br>
				<iframe src="https://www.youtube.com/embed/pW88QFpHXa8" allowfullscreen></iframe>
			</td>
		</tr>
	</table>

</body>
</html>