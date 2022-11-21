import logging

from rich.console import Console
from rich.logging import RichHandler

# Setting up logging with rich
FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")
console = Console()


class FireProx:
    def __init__(
        self,
        client,
        template,
        region,
        target=None,
        api_id=None,
    ) -> None:
        self.api_id = api_id
        self.client = client
        self.template = template
        self.region = region
        self.target = target

    def _store_api(
        self, api_id, name, created_dt, version, target, resource_id, proxy_url
    ):
        log.info(f"[{created_dt}] ({api_id}) {name} {proxy_url} -> ({target})")

    def _get_resource(self, api_id):
        response = self.client.get_resources(restApiId=api_id)
        for item in response["items"]:
            item_id = item["id"]
            item_path = item["path"]
            if item_path == "/{proxy+}":
                return item_id
        return None

    def _create_deployment(self, api_id):
        response = self.client.create_deployment(
            restApiId=api_id,
            stageName="fireprox",
            stageDescription="FireProx Prod",
            description="FireProx Production Deployment",
        )
        resource_id = response["id"]
        return (
            resource_id,
            f"https://{api_id}.execute-api.{self.region}.amazonaws.com/fireprox/",
        )

    def _get_integration(self, api_id):
        resource_id = self._get_resource(api_id)
        response = self.client.get_integration(
            restApiId=api_id, resourceId=resource_id, httpMethod="ANY"
        )
        return response["uri"]

    def create(self):
        response = self.client.import_rest_api(
            parameters={"endpointConfigurationTypes": "REGIONAL"}, body=self.template
        )
        resource_id, proxy_url = self._create_deployment(response["id"])
        self._store_api(
            response["id"],
            response["name"],
            response["createdDate"],
            response["version"],
            self.target,
            resource_id,
            proxy_url,
        )

        # Convert timestamp to string
        created_dt = response["createdDate"].strftime("%Y-%m-%d %H:%M:%S")

        endpoint = {
            "api_id": response["id"],
            "proxy_url": proxy_url,
            "name": response["name"],
            "created": created_dt,
        }
        return endpoint

    def update(self):
        resource_id = self._get_resource(self.api_id)

        if self.target.endswith("/"):
            self.target = self.target[:-1]

        if resource_id:
            response = self.client.update_integration(
                restApiId=self.api_id,
                resourceId=resource_id,
                httpMethod="ANY",
                patchOperations=[
                    {
                        "op": "replace",
                        "path": "/uri",
                        "value": "{}/{}".format(self.target, r"{proxy}"),
                    },
                ],
            )
            return response["uri"].replace("/{proxy}", "") == self.target

    def list(self, deleted_api_id=None, delete=False):
        response = self.client.get_rest_apis()
        if len(response["items"]) > 0:

            for item in response["items"]:
                try:
                    created_dt = item["createdDate"]
                    api_id = item["id"]
                    name = item["name"]
                    proxy_url = self._get_integration(api_id).replace("{proxy}", "")
                    url = f"https://{api_id}.execute-api.{self.region}.amazonaws.com/fireprox/"
                    if not api_id == deleted_api_id and not delete:
                        log.info(
                            f"[{created_dt}] ({api_id}) {name} {url} -> ({proxy_url})"
                        )
                except Exception as a:
                    log.error(f"Error Getting APIs: {a}")
                    exit(1)
        else:
            log.info(f"No fireprox-ng APIs found in {self.region}")
        return response["items"]

    def delete(self):
        items = self.list(self.api_id, delete=True)
        results = []
        for item in items:
            item_api_id = item["id"]
            try:
                if self.api_id == "all":
                    response = self.client.delete_rest_api(restApiId=item_api_id)
                    results.append(response)
                if item_api_id == self.api_id:
                    response = self.client.delete_rest_api(restApiId=self.api_id)
                    results.append(response)

            except Exception as a:
                log.error(f"Error deleting API: {item_api_id}")

                # Check if base path mappings in error
                if "all base path mappings" in str(a):
                    log.error(
                        f"Base path mapping conflict. Delete the endpoint delete manually from AWS console."
                    )
                # Check if Too Many Requests
                elif "TooManyRequestsException" in str(a):
                    log.error(f"Too Many Requests. Wait a few minutes and try again.")

                else:
                    log.error(f"Error: {a}")

                return False

        return results
