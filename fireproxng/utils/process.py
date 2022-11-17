import configparser
import datetime
import logging
import os

import boto3
import tldextract
import validators
from rich.console import Console
from rich.logging import RichHandler

# Setting up logging with rich
FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")
console = Console()


class Process:
    def __init__(
        self,
        profile_name,
        access_key,
        secret_access_key,
        session_token,
        region,
        target,
    ) -> None:
        self.profile_name = profile_name
        self.access_key = access_key
        self.secret_access_key = secret_access_key
        self.session_token = session_token
        self.region = region
        self.target = target
        self.client = None

    def _check_auth(self):

        try:
            self.client = boto3.client(
                "apigateway",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_access_key,
                aws_session_token=self.session_token,
                region_name=self.region,
            )
            self.client.get_account()
        except Exception as e:
            log.error(f"Error authenticating: {e}")
            exit(1)

    def auth_config_handler(self):

        if not self.access_key and not self.secret_access_key:
            try:
                assert os.path.exists(os.path.expanduser("~/.aws/credentials"))

                config = configparser.ConfigParser()
                config.read(os.path.expanduser("~/.aws/credentials"))

                if self.profile_name in config.sections():
                    self.region = config[self.profile_name]["region"]
                    self.access_key = config[self.profile_name]["aws_access_key_id"]
                    self.secret_access_key = config[self.profile_name][
                        "aws_secret_access_key"
                    ]
            except AssertionError as a:
                log.error(f"Error loading credentials from configuration file: {a}")
                exit(1)

        self._check_auth()
        return self.client, self.region

    def build_template(self):
        try:
            assert validators.url(self.target)
            if self.target[-1] == "/":
                self.target = self.target[:-1]

            title = "fireprox_{}".format(tldextract.extract(self.target).domain)
            version_date = f"{datetime.datetime.now():%Y-%m-%dT%XZ}"

            # Evasion techniques added from credmaster
            # https://github.com/knavesec/CredMaster/blob/master/fire.py
            template = """
            {
              "swagger": "2.0",
              "info": {
                "version": "{{version_date}}",
                "title": "{{title}}"
              },
              "basePath": "/",
              "schemes": [
                "https"
              ],
              "paths": {
                "/": {
                  "get": {
                    "parameters": [
                      {
                        "name": "proxy",
                        "in": "path",
                        "required": true,
                        "type": "string"
                      },
                      {
                        "name": "X-My-X-Forwarded-For",
                        "in": "header",
                        "required": false,
                        "type": "string"
                      },
                      {
                        "name": "X-My-Authorization",
                        "in": "header",
                        "required": false,
                        "type": "string"
                      },
                      {
                        "name" : "X-My-X-Amzn-Trace-Id",
                        "in" : "header",
                        "required" : false,
                        "type" : "string"
                      }
                    ],
                    "responses": {},
                    "x-amazon-apigateway-integration": {
                      "uri": "{{url}}/",
                      "responses": {
                        "default": {
                          "statusCode": "200"
                        }
                      },
                      "requestParameters": {
                        "integration.request.path.proxy": "method.request.path.proxy",
                        "integration.request.header.X-Forwarded-For" : "method.request.header.X-My-X-Forwarded-For",
                        "integration.request.header.Authorization" : "method.request.header.X-My-Authorization",
                        "integration.request.header.X-Amzn-Trace-Id" : "method.request.header.X-My-X-Amzn-Trace-Id"
                      },
                      "passthroughBehavior": "when_no_match",
                      "httpMethod": "ANY",
                      "cacheNamespace": "irx7tm",
                      "cacheKeyParameters": [
                        "method.request.path.proxy"
                      ],
                      "type": "http_proxy"
                    }
                  }
                },
                "/{proxy+}": {
                  "x-amazon-apigateway-any-method": {
                    "produces": [
                      "application/json"
                    ],
                    "parameters": [
                      {
                        "name": "proxy",
                        "in": "path",
                        "required": true,
                        "type": "string"
                      },
                      {
                        "name": "X-My-X-Forwarded-For",
                        "in": "header",
                        "required": false,
                        "type": "string"
                      },
                      {
                        "name": "X-My-Authorization",
                        "in": "header",
                        "required": false,
                        "type": "string"
                      },
                      {
                        "name" : "X-My-X-Amzn-Trace-Id",
                        "in" : "header",
                        "required" : false,
                        "type" : "string"
                      }
                    ],
                    "responses": {},
                    "x-amazon-apigateway-integration": {
                      "uri": "{{url}}/{proxy}",
                      "responses": {
                        "default": {
                          "statusCode": "200"
                        }
                      },
                      "requestParameters": {
                        "integration.request.path.proxy": "method.request.path.proxy",
                        "integration.request.header.X-Forwarded-For": "method.request.header.X-My-X-Forwarded-For",
                        "integration.request.header.Authorization": "method.request.header.X-My-Authorization",
                        "integration.request.header.X-Amzn-Trace-Id": "method.request.header.X-My-X-Amzn-Trace-Id"
                      },
                      "passthroughBehavior": "when_no_match",
                      "httpMethod": "ANY",
                      "cacheNamespace": "irx7tm",
                      "cacheKeyParameters": [
                        "method.request.path.proxy"
                      ],
                      "type": "http_proxy"
                    }
                  }
                }
              }
            }
            """

            template = template.replace("{{url}}", self.target)
            template = template.replace("{{title}}", title)
            template = template.replace("{{version_date}}", version_date)
            return str.encode(template)

        except AssertionError as a:
            log.error(f"Error: {a}")
            exit(1)
