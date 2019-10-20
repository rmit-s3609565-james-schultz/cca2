# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import logging

# [START imports]
from flask import Flask, request, render_template, redirect, url_for
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
import os
from storage import upload_file
import bq_handler
# [END imports]

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])
# [START create_app]
app = Flask(__name__)
# [END create_app]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file_to_gs():
    user = users.get_current_user()
    if not user:
        return redirect(url_for('.main'))
    filename = "fail"
    if request.method == 'POST':
        # check if the post request has the file part
        if 'image' not in request.files:
            return redirect(url_for('.main'))
        file = request.files['image']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return redirect(url_for('.main'))
        if file and allowed_file(file.filename):
            filename = file.filename
            logger = logging.getLogger(__name__)
            logger.error(filename)
            filename = upload_file(file.read(), filename, file.content_type, user.user_id())

    else:
        return redirect(url_for('.main'))
    return " <title>File Uploaded</title>" + filename + '''
    <h4>File uploaded, redirecting...</h4>
	<script>
	setTimeout(function() {
        window.location.href = window.location.href
        }, (500));
	</script>
    </form>
    '''

@app.route('/user')
def main():
    user = users.get_current_user()
    photodata = []
    if user:
        from google.cloud import bigquery
        url = users.create_logout_url(request.url)
        url_linktext = 'Logout'
        greeting = 'Welcome, {}!'.format(user.nickname())
        show_upload_link = True
        photodata = get_bq_photo_data(user.user_id())
    else:
        url = users.create_login_url(request.url)
        url_linktext = 'Login'
        greeting = 'Please log in to upload files.'
        show_upload_link = False


    template_values = {
        'greeting': greeting,
        'url': url,
        'url_linktext': url_linktext,
        'show_upload_link': show_upload_link,
        'photodata': photodata
    }

    template = JINJA_ENVIRONMENT.get_template('templates/index.html')
    return template.render(template_values)

def get_bq_photo_data(userid):
    data = bq_handler.get_recent(userid)
    image_info = rows_to_str(data)
    return image_info

def rows_to_str(rows):
    row_list = []
    for row in rows:
        ret_dict = {}
        for key, value in row.items():
            ret_dict[key] = str(value)
    return row_list



@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
# [END app]
