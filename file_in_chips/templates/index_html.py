# Autogenerated file
def render(status):
    yield """
<html>

<head>
    <meta charset=\"utf-8\">
    <style type=\"text/css\">
        button """
    yield """{
            width: 150px;
            height: 80px;
            background-color: palevioletred;
        }
    </style>
</head>

<body align=\"center\">
    <h1>Wifi 控制 LED</h1>
    </br>
    <p>
        <font size=\"5\">Status:&nbsp;&nbsp;</font>
        <font color=\"red\" size=\"5\">"""
    yield str(status)
    yield """</font>
    </p>
    </br>
    <p><a href=\"/light?switch=on\"><button>ON</button></a></p>
    </br>
    <p><a href=\"/light?switch=off\"><button>OFF</button></a></p>
    </br>
    <p><a href=\"/light?switch=flash\"><button>Flash</button></a></p>
    </br>
</body>

</html>"""
