#Usage: python app.py
import os
 
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.middleware.shared_data import SharedDataMiddleware
from keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from keras.models import Sequential, load_model
import numpy as np
import argparse
import imutils
import cv2
import time
import uuid
import base64

img_width, img_height = 224, 224
model_path = './models/endoscopy_vgg16.h5'
#model_weights_path = './models/weights.h5'
model = load_model(model_path)
#model.load_weights(model_weights_path)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])

def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)

def predict(file):
    x = load_img(file, target_size=(img_width,img_height))
    x = img_to_array(x)
    x = np.expand_dims(x, axis=0)
    array = model.predict(x)
    result = array[0]
    answer = np.argmax(result)
    if answer == 0:
        print("Label: Dyed Lifted Polyp")
    elif answer == 1:
	    print("Label: Dyed Resection Margin")
    elif answer == 2:
	    print("Label: Esophagitis")
    elif answer == 3:
	    print("Label: Normal Cecum")
    elif answer == 4:
	    print("Label: Normal Pylorus")
    elif answer == 5:
	    print("Label: Normal Z-Line")
    elif answer == 6:
	    print("Label: Polyps")
    elif answer == 7:
	    print("Label: Ulcerative Colitis")
    return answer

def my_random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4()) # Convert UUID format to a Python string.
    random = random.upper() # Make all characters uppercase.
    random = random.replace("-","") # Remove the UUID '-'.
    return random[0:string_length] # Return the random string.

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def template_test():
    return render_template('template.html', label='', imagesource='../uploads/template.jpg')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        import time
        start_time = time.time()
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            result = predict(file_path)
            if result == 0:
                label = 'Dyed Lifted Polyp'
            elif result == 1:
                label = 'Dyed Resection Margin'			
            elif result == 2:
                label = 'Esophagitis'
            elif result == 3:
                label = 'Normal Cecum'
            elif result == 4:
                label = 'Normal Pylorus'
            elif result == 5:
                label = 'Normal Z-Line'
            elif result == 6:
                label = 'Polyps'
            elif result == 7:
                label = 'Ulcerative Colitis'
            print(result)
            print(file_path)
            filename = my_random_string(6) + filename

            os.rename(file_path, os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("--- %s seconds ---" % str (time.time() - start_time))
            return render_template('template.html', label=label, imagesource='../uploads/' + filename)

from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  app.config['UPLOAD_FOLDER']
})

if __name__ == "__main__":
    app.debug=False
    app.run(host='127.0.0.1', port=3000)