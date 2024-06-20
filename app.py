from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import boto3
from botocore.client import Config
import urllib3
import random
import string
import os

# Suppress only the single InsecureRequestWarning from urllib3 needed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# AWS S3 credentials and endpoint
aws_access_key = ''
aws_secret_access_key = ''
endpoint_url = 'https://s3.amazonaws.com'
bucket_name = 'breaker19er-test'

# Initialize S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_access_key,
    endpoint_url=endpoint_url,
    config=Config(signature_version='s3v4'),
    verify=False
)

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def list_files_in_folder(prefix):
    try:
        response = s3.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix,
            Delimiter='/'
        )
        folders = []
        files = []
        if 'CommonPrefixes' in response:
            folders = [cp['Prefix'] for cp in response['CommonPrefixes']]
        if 'Contents' in response:
            files = [obj['Key'] for obj in response['Contents'] if obj['Key'] != prefix]
        return folders, files
    except Exception as e:
        flash(f'Error listing files: {e}', 'danger')
        return [], []

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_jibberish_content():
    return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation + ' ', k=100))

def get_breadcrumbs(prefix):
    if not prefix:
        return []
    parts = prefix.strip('/').split('/')
    breadcrumbs = [{'name': 'Home', 'prefix': ''}]
    for i, part in enumerate(parts):
        breadcrumbs.append({'name': part, 'prefix': '/'.join(parts[:i + 1]) + '/'})
    return breadcrumbs

@app.route('/')
@app.route('/<path:prefix>')
def index(prefix=''):
    if prefix and not prefix.endswith('/'):
        prefix += '/'
    folders, files = list_files_in_folder(prefix)
    breadcrumbs = get_breadcrumbs(prefix)
    return render_template('index.html', folders=folders, files=files, prefix=prefix, breadcrumbs=breadcrumbs, bucket_name=bucket_name)

@app.route('/create_folder', methods=['POST'])
def create_folder():
    folder_name = request.form['folder_name']
    prefix = request.form['prefix']
    if prefix and not prefix.endswith('/'):
        prefix += '/'
    new_folder = f'{prefix}{folder_name}/'
    try:
        s3.put_object(Bucket=bucket_name, Key=new_folder)
        flash('Folder created successfully.', 'success')
    except Exception as e:
        flash(f'Error creating folder: {e}', 'danger')
    return redirect(url_for('index', prefix=prefix))

@app.route('/upload_file', methods=['POST'])
def upload_file():
    file = request.files['file']
    prefix = request.form['prefix']
    if prefix and not prefix.endswith('/'):
        prefix += '/'
    file_key = f'{prefix}{file.filename}'
    try:
        s3.put_object(Bucket=bucket_name, Key=file_key, Body=file)
        flash('File uploaded successfully.', 'success')
    except Exception as e:
        flash(f'Error uploading file: {e}', 'danger')
    return redirect(url_for('index', prefix=prefix))

@app.route('/create_file', methods=['POST'])
def create_file():
    file_name = request.form['file_name']
    file_content = request.form['file_content']
    prefix = request.form['prefix']
    if prefix and not prefix.endswith('/'):
        prefix += '/'
    file_key = f'{prefix}{file_name}'
    try:
        s3.put_object(Bucket=bucket_name, Key=file_key, Body=file_content)
        flash('File created successfully.', 'success')
    except Exception as e:
        flash(f'Error creating file: {e}', 'danger')
    return redirect(url_for('index', prefix=prefix))

@app.route('/edit_file/<path:key>', methods=['GET', 'POST'])
def edit_file(key):
    if request.method == 'POST':
        new_content = request.form['file_content']
        try:
            s3.put_object(Bucket=bucket_name, Key=key, Body=new_content)
            flash('File updated successfully.', 'success')
        except Exception as e:
            flash(f'Error updating file: {e}', 'danger')
        return redirect(url_for('index', prefix='/'.join(key.split('/')[:-1])))
    else:
        try:
            response = s3.get_object(Bucket=bucket_name, Key=key)
            content = response['Body'].read().decode('utf-8')
        except Exception as e:
            flash(f'Error reading file: {e}', 'danger')
            content = ''
        return render_template('edit.html', key=key, content=content)

@app.route('/delete/<path:key>')
def delete_file_or_folder(key):
    try:
        # Check if it's a folder
        if key.endswith('/'):
            # List all objects with this prefix and delete them
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=key)
            if 'Contents' in response:
                for obj in response['Contents']:
                    s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
        else:
            # It's a file, delete it
            s3.delete_object(Bucket=bucket_name, Key=key)
        flash('Deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting: {e}', 'danger')
    return redirect(url_for('index', prefix='/'.join(key.split('/')[:-1])))

@app.route('/download/<path:key>')
def download_file(key):
    try:
        local_path = os.path.join(os.getcwd(), os.path.basename(key))
        s3.download_file(bucket_name, key, local_path)
        return send_file(local_path, as_attachment=True, download_name=os.path.basename(key))
    except Exception as e:
        flash(f'Error downloading file: {e}', 'danger')
        return redirect(url_for('index', prefix='/'.join(key.split('/')[:-1])))

@app.route('/generate_jibberish', methods=['POST'])
def generate_jibberish():
    prefix = request.form['prefix']
    if prefix and not prefix.endswith('/'):
        prefix += '/'
    
    for _ in range(5):  # Create 5 jibberish folders
        folder_name = generate_random_string()
        new_folder = f'{prefix}{folder_name}/'
        try:
            s3.put_object(Bucket=bucket_name, Key=new_folder)
        except Exception as e:
            flash(f'Error creating folder: {e}', 'danger')
    
    for _ in range(5):  # Create 5 jibberish files
        file_name = generate_random_string() + '.txt'
        file_content = generate_jibberish_content()
        file_key = f'{prefix}{file_name}'
        try:
            s3.put_object(Bucket=bucket_name, Key=file_key, Body=file_content)
        except Exception as e:
            flash(f'Error creating file: {e}', 'danger')
    
    flash('Random jibberish files and folders created successfully.', 'success')
    return redirect(url_for('index', prefix=prefix))

@app.route('/cleanup', methods=['POST'])
def cleanup():
    prefix = request.form['prefix']
    if prefix and not prefix.endswith('/'):
        prefix += '/'
    
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if 'Contents' in response:
            for obj in response['Contents']:
                s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
        flash('Cleanup successful.', 'success')
    except Exception as e:
        flash(f'Error during cleanup: {e}', 'danger')
    
    return redirect(url_for('index', prefix=prefix))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
