# Import functions from flask
from flask import Flask

# Create server
app = Flask(__name__)

# Create a GET request handler for the / route
@app.get("/")
def hello_world():
    return """
<!DOCTYPE html>
<html lang="en">
	<head>
		<meta charset="UTF-8" />
		<meta http-equiv="X-UA-Compatible" content="IE=edge" />
		<meta name="viewport" content="width=device-width, initial-scale=1.0" />
		<title>Document</title>
	</head>
	<body>
		<h1>E</h1>
	</body>
</html>

    """