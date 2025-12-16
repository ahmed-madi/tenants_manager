import os
import json
import boto3
import frappe
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from botocore.exceptions import NoCredentialsError, ClientError

load_dotenv(override=True)

env_name = os.getenv("ENV_NAME", "dev")
default_region = os.getenv("DEFAULT_REGION", "us-east-1")


class S3bucket:

    def __init__(self, bucket_name=None):
        self.env_name = env_name
        self.bucket_name = bucket_name or f"tapp-{env_name}"
        session = boto3.session.Session()
        self.region_name = session.region_name or default_region
        self.s3_client = session.client('s3', region_name=self.region_name)


    def get_s3_file_full_path(self, file_path):
        return f"{self.bucket_name}/{file_path}"

    def get_s3_file_url(self, file_path):
        return f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{file_path}"

    def upload_file(self, file, s3_folder_path):
        """Uploads a file to a specified folder in an Amazon S3 bucket.

        :param file: The file object to upload (e.g., file from a web form).
        :param s3_folder_path: The folder path in the S3 bucket where the file will be stored.

        :return: The public URL of the uploaded file in the S3 bucket.
        """
        file_name = secure_filename(file.filename)
        s3_file_path = os.path.join(s3_folder_path, file_name)
        try:
            self.s3_client.upload_fileobj(file, self.bucket_name, s3_file_path)
            return self.get_s3_file_full_path(s3_file_path)
        except NoCredentialsError:
            return frappe.throw("AWS credentials not available", frappe.ValidationError)
        except ClientError as e:
            return frappe.throw(f"Error uploading file to S3: {str(e)}", frappe.FrappeTypeError)


    def delete_file(self, object_name):
        """Delete a file from an S3 bucket.

        :param object_name: S3 object name
        :return:
        """
        try:
            response = self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)

            if response['ResponseMetadata']['HTTPStatusCode'] == 204:
                return {"message": f"File '{object_name}' deleted successfully from S3."}
            else:
                frappe.throw(f"Failed to delete file: {object_name}. Response: {response}")
        except NoCredentialsError:
            return frappe.throw("AWS credentials not available", frappe.ValidationError)
        except ClientError as e:
            return frappe.throw(f"Error deleting file from S3: {str(e)}", frappe.FrappeTypeError)


    def get_file(self, file_path):
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_path)
            file= response['Body']
            return file
        except NoCredentialsError:
            frappe.throw("AWS credentials not available", frappe.ValidationError)
        except ClientError as e:
            frappe.throw(f"Error retrieving file from S3: {str(e)}")


    def get_bucket_objects_list(self, folder_path):
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=folder_path)
        except NoCredentialsError:
            frappe.throw("AWS credentials not available", frappe.ValidationError)
        except ClientError as e:
            frappe.throw(f"Error retrieving files list from S3: {str(e)}")

        if 'Contents' not in response:
            frappe.throw(f"No files found in the folder: {folder_path}")

        files_list = [obj['Key'].split('/')[-1] for obj in response['Contents'] if obj['Key'] != folder_path]
        return files_list


class BusinessOwnerMenuS3bucket(S3bucket):

    def __init__(self, business_owner_id, business_id):
        super().__init__()
        self.business_owner_id = business_owner_id
        self.business_id = business_id

    @property
    def menu_folder_path(self):
        return f"business-owner/{self.business_owner_id}/business/{self.business_id}/menu/"

    @property
    def menu_item_folder_path(self):
        return f"business-owner/{self.business_owner_id}/business/{self.business_id}/menu-item/"

    def upload_menu(self, file):
        s3_file_path = self.upload_file(file, self.menu_folder_path)
        return s3_file_path

    def delete_menu(self, menu_name):
        self.delete_file(f"{self.menu_folder_path}{menu_name}")

    def get_menu_file(self, menu_name):
        file = self.get_file(f"{self.menu_folder_path}{menu_name}")
        return file

    def get_business_owner_menus(self):
        business_owner_menus = self.get_bucket_objects_list(self.menu_folder_path)
        return business_owner_menus

    def upload_menu_item(self, file):
        s3_full_file_path = self.upload_file(file, self.menu_item_folder_path)
        s3_file_path = '/'.join(s3_full_file_path.split('/')[1:])
        return self.get_s3_file_url(s3_file_path)


class SecretsManager:

    def __init__(self):
        self.env_name = env_name
        session = boto3.session.Session()
        self.region_name = session.region_name or default_region
        self.sm_client = session.client('secretsmanager', region_name=self.region_name)
        self.secret_name = f"tapp/{self.env_name}"
        self._secret_cache = None

    def _get_secret_json(self, secret_name):
        try:
            response = self.sm_client.get_secret_value(SecretId=secret_name)
        except NoCredentialsError:
            frappe.throw("AWS credentials not available", frappe.ValidationError)
        except ClientError as e:
            frappe.throw(f"Error retrieving secret from Secrets manager: {str(e)}", frappe.FrappeTypeError)

        if 'SecretString' in response:
            secret = response['SecretString']
        else:
            secret = response['SecretBinary']

        try:
            secret_dict = json.loads(secret)
        except ValueError:
            secret_dict = {"secret": secret}

        return  secret_dict

    @property
    def secrets(self):
        if self._secret_cache is None:
            self._secret_cache = self._get_secret_json(self.secret_name)
        return self._secret_cache

    def get(self, key, default=None):
        return self.secrets.get(key, default)



secrets_manager = SecretsManager()