# musical-octo-couscous

This project implements an encrypted file storage and retrieval system using Django. The system allows users to upload files, which are encrypted and stored on the file system, and later retrieve and decrypt them securely. It uses `Fernet` symmetric encryption to ensure data confidentiality, with the encryption keys stored securely in a database.

## Features

- **File Upload and Encryption**: Files are uploaded, encrypted using the `Fernet` symmetric encryption algorithm, and stored securely on the file system.
- **File Retrieval and Decryption**: Files can be retrieved by their name, and the system automatically decrypts them using the associated encryption key stored in the database.
- **Modular Design**: The `FileHandler` class is responsible for all file-related operations, making the system modular and easy to maintain.
- **Error Handling**: The system includes robust error handling for missing files, incorrect decryption keys, and corrupted files.

## Technology Stack

- **Django**: A Python web framework for building the backend.
- **Cryptography (Fernet)**: Used for symmetric encryption of files.
- **SQLite**: Used as the default database to store file metadata and encryption keys.
- **Django's Default Storage System**: Used to store files locally. This can easily be extended to use AWS S3 or another cloud storage provider.
- **Pipenv**: Used to manage Python packages and the virtual environment.

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/Amanskywalker/musical-octo-couscous.git
    cd musical-octo-couscous
    ```

2. **Install dependencies using Pipenv:**

    ```bash
    pipenv install --dev
    pipenv shell
    ```

3. **Apply database migrations:**

    ```bash
    python manage.py migrate
    ```

4. **Run the development server:**

    ```bash
    python manage.py runserver
    ```

## How It Works

1. **File Upload**

    Users can upload a file using a POST request to the /upload/ endpoint.
    The file is encrypted using Fernet encryption and stored in the file system.
    The encryption key and file metadata (file name, file path, etc.) are saved to the database.

2. **File Retrieval**

    Users can retrieve a file by making a GET request to the /upload/ endpoint with the file's name as a query parameter.
    The system will fetch the file's encryption key from the database, retrieve the encrypted file from the file system, and decrypt it.
    The decrypted file is then returned as a download to the user.

## Example API Usage

1. **File Upload (POST /upload/)**

    **Request:**
        You must provide the file in the form-data as file.

    ```bash
    curl -X POST -F "file=@/path/to/your/file.txt" http://localhost:8000/upload/
    ```

    **Response:**

    ```json
    {
      "message": "File uploaded and encrypted successfully",
      "file_url": "/media/encrypted_files/filename.txt"
    }
    ```

2. **File Retrieval (GET /upload/?file_name=filename.txt)**

    **Request:**
        Query parameter `file_name` is required.

    ```bash
    curl -X GET "http://localhost:8000/upload/?file_name=filename.txt" -O
    ```
    
    **Response:**
        The server will return the decrypted file as a download.


## Database Schema

A model EncryptedFile is used to store file metadata and encryption keys:

    file_name: The name of the uploaded file.
    file_key: The encryption key used to encrypt/decrypt the file.
    file_path: The path to the encrypted file in the file system.

## Error Handling

**File Not Found:** If the requested file is missing from the database or file system, a 404 error is returned.

**Decryption Failure:** If decryption fails (e.g., due to a corrupted file or invalid key), a 400 error is returned.

## Extending the System

1. **Uploading to AWS S3**

The current implementation uses Django's default file storage to store files on the local file system. However, it is designed to be easily extensible to other storage backends like Amazon S3. To upload files to S3, modify the `_upload_to_file_system` method in the FileHandler class to integrate with django-storages and AWS S3.

2. **Adding Authentication**

You can extend this system to include user authentication and authorization to limit access to files based on the logged-in user.

3. **File Expiry**

You can add functionality to automatically delete files after a certain period by using Django signals or background tasks (e.g., Celery).

## Testing

Unit tests are included to validate the core functionality of the system. The tests cover:

- **File upload and encryption:** Ensures that files are uploaded, encrypted, and stored correctly.
- **File retrieval and decryption:** Ensures that files can be retrieved and decrypted correctly.
- **Error handling:** Tests for cases where files are missing, or decryption fails due to an invalid key.

### Running Tests

To run the test suite:

```bash
python manage.py test
```