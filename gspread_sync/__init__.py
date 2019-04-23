# -*- coding: utf-8 -*-

from __future__ import print_function
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import AuthorizedSession
import google_auth_httplib2
from apiclient import discovery
import googleapiclient
from googleapiclient.http import build_http
import os
from threading import RLock
import copy
import _pickle as cPickle

discoveryUrl = 'https://sheets.googleapis.com/$discovery/rest?version=v4'

def createQueryRange(sheetName, rangeName=None):
    queryRange = sheetName
    if rangeName:
        queryRange = "'%s'!%s" % (sheetName.replace("'", "\\'"), rangeName)
    return queryRange

def int26(index):
    result = ''
    result = chr(65 + index % 26) + result
    index = index / 26
    while index > 0:
        result = chr(65 + index % 26) + result
        index = index / 26
    return result

class Authorization(object):
    def __init__(self, path, secret_file="client_secret.json", secret_dump_path=None):
        self.credentials = self.get_credentials(
            path, client_secret_file=secret_file,
            secret_dump_path=secret_dump_path)

    @staticmethod
    def get_credentials(credential_dir, client_secret_file, secret_dump_path=None,
                        scopes=['https://www.googleapis.com/auth/spreadsheets'],
                        redirect_uri='urn:ietf:wg:oauth:2.0:oob'):
        if os.path.exists(secret_dump_path):
            with open(secret_dump_path, 'rb') as f:
                return cPickle.load(f)
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_file, scopes=scopes, redirect_uri=redirect_uri)
        flow.run_local_server()
        session = flow.authorized_session()
        with open(secret_dump_path, 'wb') as f:
            cPickle.dump(session.credentials, f)
        return session.credentials

class Sheet(object):
    def __init__(self, sheetId, auth):
        self.sheetId = sheetId
        if isinstance(auth, Authorization):
            self.credentials = copy.deepcopy(auth.credentials)
        else:
            self.credentials = copy.deepcopy(auth)

        self.apiLock = RLock()

        # the AuthorizedHttp already implement refresh in request
        # so we don't have to check if is valid or not
        http = google_auth_httplib2.AuthorizedHttp(self.credentials,
                                                   http=build_http())
        self.service = discovery.build(
                'sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

    def query(self, sheetName, rangeName=None, dimension='ROWS', callback=None,
              retries=3):
        queryRange = createQueryRange(sheetName, rangeName)
        try:
            with self.apiLock:
                result = self.service.spreadsheets().values().get(
                        spreadsheetId=self.sheetId, range=queryRange,
                        majorDimension=dimension).execute(num_retries=retries)
                return result.get('values', [])
        except googleapiclient.errors.HttpError as e:
            if callback:
                return callback(e)
            else:
                raise e
        return []

    def update(self, sheetName, rangeName=None, body=[], callback=None,
            retries=3):
        queryRange = createQueryRange(sheetName, rangeName)
        try:
            with self.apiLock:
                request = self.service.spreadsheets().values().update(
                        spreadsheetId=self.sheetId, range=queryRange,
                        body={"values": body}, valueInputOption="RAW").execute(num_retries=retries)
                return request
        except googleapiclient.errors.HttpError as e:
            if callback:
                return callback(e)
            else:
                raise e
        return {}

    def insert(self, sheetName, rangeName=None, body=[], overwrite=False,
            callback=None, retries=3):
        insertDataOption = "INSERT_ROWS"
        if overwrite:
            insertDataOption = "OVERWRITE"
        queryRange = createQueryRange(sheetName, rangeName)
        try:
            with self.apiLock:
                request = self.service.spreadsheets().values().append(
                        spreadsheetId=self.sheetId, range=queryRange,
                        insertDataOption=insertDataOption,
                        body={"values": body}, valueInputOption="RAW").execute(num_retries=retries)
                return request
        except googleapiclient.errors.HttpError as e:
            if callback:
                return callback(e)
            else:
                raise e
        return {}

    def getProperties(self, ranges=None, includeGridData=False, callback=None, retries=3):
        try:
            with self.apiLock:
                result = self.service.spreadsheets().get(
                        spreadsheetId=self.sheetId,
                        ranges=ranges,
                        includeGridData=includeGridData).execute()
                return result
        except googleapiclient.errors.HttpError as e:
            if callback:
                return callback(e)
            else:
                raise e
        return {}

    def removeSheet(self, sheetId, callback=None, retries=3):
        try:
            with self.apiLock:
                result = self.service.spreadsheets().batchUpdate(
                        spreadsheetId=self.sheetId,
                        body={"requests": [{
                            "deleteSheet": {
                                "sheetId": sheetId}
                            }]}).execute(num_retries=retries)
                return result
        except googleapiclient.errors.HttpError as e:
            if callback:
                return callback(e)
            else:
                raise e
        return {}

    def newSheet(self, sheetName, header=[], callback=None, retries=3):
        queryRange = createQueryRange(sheetName)
        try:
            with self.apiLock:
                result = self.service.spreadsheets().batchUpdate(
                        spreadsheetId=self.sheetId,
                        body={"requests": [{
                            "addSheet": {
                                "properties": {
                                    "title": sheetName,
                                    "gridProperties": {
                                        "columnCount": len(header),
                                        "rowCount": 1000
                                    }
                                }
                            }
                        }]}).execute(num_retries=retries)
                if len(header) == 0:
                    return result['replies'][0]
                newQueryRange = createQueryRange(
                        sheetName, 'A1:' + int26(len(header)-1) + '1')
                request = self.service.spreadsheets().values().update(
                        spreadsheetId=self.sheetId, range=newQueryRange, body={
                            'values': [header]}, valueInputOption='RAW').execute(num_retries=retries)
                return result['replies'][0]
        except googleapiclient.errors.HttpError as e:
            if callback:
                return callback(e)
            else:
                raise e
        return []



