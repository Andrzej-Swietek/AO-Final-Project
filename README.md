# AO-Final-Project
## How to run the app

Ensure that your python is at least version 3.10

Example images can be found in ``backend/example_images`` directory

```sh
cd backend
python -m venv venv
source ./venv/bin/activate
pip install --upgrade pip && pip install -r requirements.txt
flask run --host=0.0.0.0
```

The application will start listening at port 5000. Open your browser and type `http://localhost:5000` to enter.
