# -*- coding: utf-8 -*-

MATCH_TABLE = '''
<table border="0" cellspacing="0">
<tr>
<td class="s12" width="%d">&nbsp;</td>
<td class="bdcc2" width="%d">&nbsp;wynik&nbsp;</td>
</tr>
%s
</table>
'''

MATCH_LINK = '''
<a href="%s" target="_top">
%s
</a>
'''

MATCH_SCORE = '''
&nbsp;%.1f&nbsp;
'''

MATCH_TEAM_LINK = '''
<a href="%s" onmouseover="Tip('%s')" onmouseout="UnTip()">%s</a>
'''

MATCH_TEAM_NON_LINK = '''
<a onmouseover="Tip('%s')" onmouseout="UnTip()">%s</a>
'''

MATCH_TEAM_ROW = '''
<tr class="%s">
<td class="bd1">&nbsp;%s&nbsp;</td>
<td class="bdc">
%s
</td>
</tr>
'''

MATCH_RUNNING = '''
<img src="images/A.gif" />
<span style="font-size: 10pt">%d</span>
<img src="images/A.gif" />
'''

MATCH_GRID = '''
<div style="position: relative; width: %dpx; height: %dpx; margin: 10px">
<canvas width="%d" height="%d" id="playoff_canvas" %s></canvas>
%s
<script src="sklady/playoff.js" type="text/javascript"></script>
</div>
'''

MATCH_GRID_PHASE_LINK = '''
<a href="%s" target="_top" style="display: inline-block; width: %dpx; text-align: center; position: absolute; top: 0; left: %dpx">
%s
</a>
'''

MATCH_GRID_PHASE_NON_LINK = '''
<span class="phase_header" style="display: inline-block; width: %dpx; text-align: center; position: absolute; top: 0; left: %dpx">
<p style="margin: 0">%s</p>
</span>
'''

MATCH_GRID_PHASE = '''
<font size="4">%s</font>
'''

MATCH_GRID_PHASE_RUNNING = '''
<img src="images/A.gif" />
<font size="4">%s</font>
<img src="images/A.gif" />
'''

MATCH_BOX = '''
<div style="text-align: center; position: absolute; left: %dpx; top: %dpx" data-id="%d" data-winner="%s" data-loser="%s" class="playoff_matchbox">
%s
</div>
'''

LEADERBOARD = '''
<table border="0" cellspacing="0">
<tr>
<td class="bdnl12" colspan="2" align="center"><b>&nbsp;KLASYFIKACJA KOŃCOWA&nbsp;</b></td>
</tr>
<tr>
<td class="e" colspan="2">&nbsp;</td>
</tr>
<tr>
<td class="bdcc12">&nbsp;miejsce&nbsp;</td>
<td class="bdcc2">&nbsp;drużyna&nbsp;</td>
</tr>
%s
</table>
'''

LEADERBOARD_ROW = '''
<tr class="%s">
<td class="bdc1">%d</td>
<td class="bd">
&nbsp;%s&nbsp;&nbsp;%s&nbsp;
</td>
</tr>
'''

LEADERBOARD_ROW_FLAG = '''
<img class="fl" src="images/%s" />
'''

PAGE_HEAD = '''
<meta http-equiv="Pragma" content="no-cache" />
<meta http-equiv="Cache-Control" content="no-cache" />
<meta name="robots" content="noarchive" />
<meta http-equiv="expires" content="0" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta name="Generator" content="PlayOff" />
%s
<title>%s</title>
<link rel="stylesheet" type="text/css" href="css/kolorki.css" />
<script type="text/javascript" src="sklady/myAjax.js"></script>
'''

PAGE_HEAD_REFRESH = '''
<meta http-equiv="Refresh" content="%d" />
'''

PAGE_BODY = '''
<script type="text/javascript" src="sklady/wz_tooltip.js"></script>
%s
%s
<p>
%s
</p>
%s
%s
'''

PAGE_BODY_FOOTER = '''
<p class="f">&nbsp;Admin&nbsp;&copy;Jan Romański&#39;2005, PlayOff&nbsp;&copyMichał Klichowicz&#39;2017-2018, strona wygenerowana %s</p>
'''

PAGE = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
%s
</head>
<body class="all">
%s
</body>
</html>
'''

SWISS_LINK = '''
[<a href="%s" class="zb" target="_top">&nbsp;%s&nbsp;</a>]<br /><br />
'''

SWISS_RUNNING_LINK = '''
[<a href="%s" class="zb" target="_top">&nbsp;<img src="images/A.gif" />&nbsp;%s&nbsp;<img src="images/A.gif" />&nbsp;</a>]<br /><br />
'''

SWISS_DEFAULT_LABEL = 'Turniej o&nbsp;%d.&nbsp;miejsce'
